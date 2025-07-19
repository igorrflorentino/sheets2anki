"""
Funções de sincronização principal para o addon Sheets2Anki.

Este módulo contém as funções centrais para sincronização
de decks com fontes remotas, usando o novo sistema de configuração.
"""

import time
from .compat import (
    mw, showInfo, QProgressDialog, QPushButton, QLabel, QDialog, QVBoxLayout,
    QTextEdit, QDialogButtonBox, AlignTop, AlignLeft, ButtonBox_Ok, safe_exec_dialog
)
from .config_manager import get_remote_decks, save_remote_decks, disconnect_deck, verify_and_update_deck_info
from .deck_naming import update_deck_name_if_needed
from .validation import validate_url
from .parseRemoteDeck import getRemoteDeck
from .note_processor import create_or_update_notes
from .exceptions import SyncError
from .subdeck_manager import remove_empty_subdecks

def syncDecks(selected_deck_names=None, selected_deck_urls=None):
    """
    Sincroniza todos os decks remotos com suas fontes.
    
    Esta é a função principal de sincronização que:
    1. Baixa dados dos decks remotos
    2. Processa e valida os dados
    3. Atualiza o banco de dados do Anki
    4. Mostra progresso ao usuário
    5. Atualiza nomes automaticamente se configurado
    
    Args:
        selected_deck_names: Lista de nomes de decks para sincronizar. 
                           Se None, sincroniza todos os decks.
        selected_deck_urls: Lista de URLs de decks para sincronizar.
                          Se fornecida, tem precedência sobre selected_deck_names.
    """
    col = mw.col
    remote_decks = get_remote_decks()

    # Inicializar estatísticas e controles
    sync_errors = []
    status_msgs = []
    decks_synced = 0
    total_stats = {
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'ignored': 0,
        'errors': 0,
        'error_details': [],
        'updated_details': []
    }

    # Determinar quais decks sincronizar
    deck_keys = _get_deck_keys_to_sync(remote_decks, selected_deck_names, selected_deck_urls)
    total_decks = len(deck_keys)
    
    # Verificar se há decks para sincronizar
    if total_decks == 0:
        _show_no_decks_message(selected_deck_names)
        return
    
    # Configurar e mostrar barra de progresso
    progress = _setup_progress_dialog(total_decks)
    
    step = 0
    try:
        # Sincronizar cada deck
        for deckKey in deck_keys:
            try:
                step, deck_sync_increment, current_stats = _sync_single_deck(
                    remote_decks, deckKey, progress, status_msgs, step
                )
                
                # Acumular estatísticas
                _accumulate_stats(total_stats, current_stats)
                decks_synced += deck_sync_increment

            except SyncError as e:
                step, sync_errors = _handle_sync_error(
                    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
                )
                continue
            except Exception as e:
                step, sync_errors = _handle_unexpected_error(
                    e, deckKey, remote_decks, progress, status_msgs, sync_errors, step
                )
                continue
        
        # Salvar alterações na configuração
        save_remote_decks(remote_decks)
        
        # Finalizar progresso e mostrar resultados
        _finalize_sync(progress, total_decks, decks_synced, total_stats, sync_errors)
    
    finally:
        # Garantir que o dialog de progresso seja fechado
        if progress.isVisible():
            progress.close()

def _get_deck_keys_to_sync(remote_decks, selected_deck_names, selected_deck_urls=None):
    """
    Determina quais chaves de deck devem ser sincronizadas.
    
    Args:
        remote_decks: Dicionário de decks remotos
        selected_deck_names: Nomes dos decks selecionados ou None
        selected_deck_urls: URLs dos decks selecionados ou None
        
    Returns:
        list: Lista de chaves (URLs) a serem sincronizadas
    """
    # Se URLs específicas foram fornecidas, usar apenas essas
    if selected_deck_urls is not None:
        filtered_keys = []
        for url in selected_deck_urls:
            if url in remote_decks:
                filtered_keys.append(url)
        return filtered_keys
    
    # Criar mapeamento de nomes para chaves
    name_to_key = {}
    for key, deck_info in remote_decks.items():
        # Verificar se o deck ainda existe
        deck_id = deck_info["deck_id"]
        deck = mw.col.decks.get(deck_id)
        
        if deck:
            # Usar nome atual do deck
            actual_deck_name = deck["name"]
            name_to_key[actual_deck_name] = key
            
            # Também mapear nome da configuração se diferente
            config_deck_name = deck_info.get("deck_name", "")
            if config_deck_name and config_deck_name != actual_deck_name:
                name_to_key[config_deck_name] = key
    
    # Se nomes específicos foram selecionados, filtrar por eles
    if selected_deck_names is not None:
        filtered_keys = []
        for deck_name in selected_deck_names:
            if deck_name in name_to_key:
                filtered_keys.append(name_to_key[deck_name])
        return filtered_keys
    
    # Caso contrário, retornar todas as chaves
    return list(remote_decks.keys())

def _build_name_to_key_mapping(config):
    """
    Constrói mapeamento de nomes de deck para chaves de configuração.
    
    Args:
        config: Configuração do addon
        
    Returns:
        dict: Mapeamento de nomes para chaves
    """
    name_to_key = {}
    for key, deck_info in get_remote_decks().items():
        # Obter o nome real do deck no Anki, não o nome salvo na config
        deck_id = deck_info.get("deck_id")
        if deck_id:
            deck = mw.col.decks.get(deck_id)
            if deck:
                actual_deck_name = deck["name"]
                name_to_key[actual_deck_name] = key
            else:
                # Fallback para o nome salvo na config se o deck não existir
                config_deck_name = deck_info.get("deck_name", "")
                if config_deck_name:
                    name_to_key[config_deck_name] = key
    
    return name_to_key

def _show_no_decks_message(selected_deck_names):
    """Mostra mensagem quando não há decks para sincronizar."""
    if selected_deck_names is not None:
        showInfo(f"Nenhum dos decks selecionados foi encontrado na configuração.\n\nDecks selecionados: {', '.join(selected_deck_names)}")
    else:
        showInfo("Nenhum deck remoto configurado para sincronização.")

def _setup_progress_dialog(total_decks):
    """
    Configura e retorna o dialog de progresso com tamanho fixo.
    
    Esta função configura uma barra de progresso com:
    - Largura fixa de 500px para evitar redimensionamento horizontal
    - Altura mínima de 120px e máxima de 300px para acomodar texto multilinha
    - Quebra automática de linha para textos longos
    - Alinhamento adequado do texto
    
    Args:
        total_decks: Número total de decks para calcular o máximo da barra
        
    Returns:
        QProgressDialog: Dialog de progresso configurado
    """
    progress = QProgressDialog("Sincronizando decks...", "", 0, total_decks * 3, mw)
    progress.setWindowTitle("Sincronização de Decks")
    progress.setMinimumDuration(0)
    progress.setValue(0)
    progress.setCancelButton(None)
    progress.setAutoClose(False)  # Não fechar automaticamente
    progress.setAutoReset(False)  # Não resetar automaticamente
    
    # Configurar tamanho fixo horizontal e permitir ajuste vertical
    progress.setFixedWidth(500)  # Largura fixa de 500 pixels
    progress.setMinimumHeight(120)  # Altura mínima
    progress.setMaximumHeight(300)  # Altura máxima
    
    # Configurar o label para quebrar linha automaticamente
    label = progress.findChild(QLabel)
    if label:
        label.setWordWrap(True)  # Permitir quebra de linha
        label.setAlignment(AlignTop | AlignLeft)  # Alinhar ao topo e à esquerda
    
    progress.show()
    mw.app.processEvents()  # Força a exibição da barra
    return progress

def _update_progress_text(progress, status_msgs, max_lines=3):
    """
    Atualiza o texto da barra de progresso com formatação adequada.
    
    Args:
        progress: QProgressDialog instance
        status_msgs: Lista de mensagens de status
        max_lines: Número máximo de linhas a mostrar
    """
    # Pegar apenas as últimas mensagens
    recent_msgs = status_msgs[-max_lines:] if len(status_msgs) > max_lines else status_msgs
    
    # Juntar mensagens com quebra de linha
    text = "\n".join(recent_msgs)
    
    # Limitar o comprimento de cada linha para evitar texto muito longo
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Se a linha for muito longa, quebrar em palavras
        if len(line) > 60:  # Aproximadamente 60 caracteres por linha
            words = line.split(' ')
            current_line = ""
            for word in words:
                if len(current_line + word + " ") <= 60:
                    current_line += word + " "
                else:
                    if current_line:
                        formatted_lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                formatted_lines.append(current_line.strip())
        else:
            formatted_lines.append(line)
    
    # Atualizar o texto da barra de progresso
    final_text = "\n".join(formatted_lines)
    progress.setLabelText(final_text)
    
    # Forçar atualização da interface
    mw.app.processEvents()

def _sync_single_deck(remote_decks, deckKey, progress, status_msgs, step):
    """
    Sincroniza um único deck remoto.
    
    Args:
        remote_decks: Dicionário de decks remotos
        deckKey: Chave (URL) do deck a ser sincronizado
        progress: Dialog de progresso
        status_msgs: Lista de mensagens de status
        step: Passo atual do progresso
    
    Returns:
        tuple: (step_updated, decks_synced_increment, deck_stats)
    """
    currentRemoteInfo = remote_decks[deckKey]
    deck_id = currentRemoteInfo["deck_id"]

    # Obter nome do deck para exibição
    deck = mw.col.decks.get(deck_id)
    
    # Se o deck não existe, recriar usando o nome salvo na configuração
    if not deck or deck["name"].strip().lower() == "default":
        saved_deck_name = currentRemoteInfo.get("deck_name", f"Deck_{deck_id}")
        
        # Recriar o deck com o nome salvo
        msg = f"Recriando deck '{saved_deck_name}' (foi deletado localmente)..."
        status_msgs.append(msg)
        _update_progress_text(progress, status_msgs)
        
        # Verificar se o nome salvo ainda está disponível
        try:
            # Tentar criar o deck com o nome exato salvo anteriormente
            new_deck_id = mw.col.decks.id(saved_deck_name)
            
            # Verificar se o nome foi mantido ou alterado pelo Anki
            new_deck = mw.col.decks.get(new_deck_id)
            actual_name = new_deck["name"]
            
            if actual_name != saved_deck_name:
                # O nome foi alterado pelo Anki (provavelmente já existe)
                msg = f"Nome '{saved_deck_name}' já existe, usando '{actual_name}' em vez disso"
                status_msgs.append(msg)
                _update_progress_text(progress, status_msgs)
        except Exception as e:
            # Em caso de erro, usar um nome genérico
            msg = f"Erro ao recriar deck: {str(e)}"
            status_msgs.append(msg)
            _update_progress_text(progress, status_msgs)
            new_deck_id = mw.col.decks.id(f"Deck_{deck_id}")
            actual_name = mw.col.decks.get(new_deck_id)["name"]
        
        # Atualizar o deck_id na configuração
        if new_deck_id != deck_id:
            currentRemoteInfo["deck_id"] = new_deck_id
            deck_id = new_deck_id
        
        # Obter o deck recriado
        deck = mw.col.decks.get(deck_id)
        
        # Atualizar informações na configuração com o nome real usado (silenciosamente)
        verify_and_update_deck_info(deckKey, deck_id, deck["name"], silent=True)
        
        step += 1
        progress.setValue(step)
        mw.app.processEvents()
    
    deckName = deck["name"]

    # Verificar e atualizar informações do deck na configuração (silenciosamente)
    verify_and_update_deck_info(deckKey, deck_id, deckName, silent=True)

    # Validar URL antes de tentar sincronizar
    validate_url(currentRemoteInfo["url"])

    # 1. Download
    msg = f"{deckName}: baixando arquivo..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    remoteDeck = getRemoteDeck(currentRemoteInfo["url"])
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 2. Processamento (já incluído no getRemoteDeck)
    msg = f"{deckName}: processando dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    remoteDeck.deckName = deckName
    
    # Atualizar nome do deck se necessário (modo automático)
    updated_name = update_deck_name_if_needed(currentRemoteInfo["url"], deck_id, deckName)
    if updated_name != deckName:
        # Atualizar informações do deck na configuração
        currentRemoteInfo["deck_name"] = updated_name
        deckName = updated_name
        remoteDeck.deckName = updated_name
        
        # Atualizar também na configuração global (silenciosamente)
        verify_and_update_deck_info(deckKey, deck_id, updated_name, silent=True)
        
        msg = f"{deckName}: nome do deck atualizado automaticamente..."
        status_msgs.append(msg)
        _update_progress_text(progress, status_msgs)
    
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 3. Escrita no banco
    msg = f"{deckName}: escrevendo no banco de dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    deck_stats = create_or_update_notes(mw.col, remoteDeck, deck_id)
    
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    return step, 1, deck_stats
    
    remoteDeck.deckName = deckName
    # remoteDeck.url = currentRemoteInfo["url"]  # Comentado devido ao erro
    step += 1
    progress.setValue(step)
    mw.app.processEvents()

    # 3. Escrita no banco
    msg = f"{deckName}: escrevendo no banco de dados..."
    status_msgs.append(msg)
    _update_progress_text(progress, status_msgs)
    
    deck_stats = create_or_update_notes(mw.col, remoteDeck, deck_id)
    step += 1
    progress.setValue(step)
    mw.app.processEvents()
    
    return step, 1, deck_stats

def _accumulate_stats(total_stats, deck_stats):
    """Acumula estatísticas de um deck nas estatísticas totais."""
    total_stats['created'] += deck_stats['created']
    total_stats['updated'] += deck_stats['updated']
    total_stats['deleted'] += deck_stats['deleted']
    total_stats['ignored'] += deck_stats.get('ignored', 0)
    total_stats['errors'] += deck_stats['errors']
    total_stats['error_details'].extend(deck_stats['error_details'])
    
    # Adicionar detalhes das atualizações (limitado a 10 total)
    if 'updated_details' in deck_stats:
        current_count = len(total_stats.get('updated_details', []))
        remaining_slots = max(0, 10 - current_count)
        
        if remaining_slots > 0:
            if 'updated_details' not in total_stats:
                total_stats['updated_details'] = []
            total_stats['updated_details'].extend(deck_stats['updated_details'][:remaining_slots])

def _handle_sync_error(e, deckKey, remote_decks, progress, status_msgs, sync_errors, step):
    """Trata erros de sincronização de deck."""
    # Tentar obter o nome do deck para a mensagem de erro
    try:
        deck_info = remote_decks[deckKey]
        deck_id = deck_info["deck_id"]
        deck = mw.col.decks.get(deck_id)
        deckName = deck["name"] if deck else deck_info.get("deck_name", str(deck_id))
    except:
        deckName = "Unknown"
    
    error_msg = f"Failed to sync deck '{deckName}': {str(e)}"
    sync_errors.append(error_msg)
    status_msgs.append(error_msg)
    _update_progress_text(progress, status_msgs)
    step += 3
    progress.setValue(step)
    mw.app.processEvents()
    return step, sync_errors

def _handle_unexpected_error(e, deckKey, remote_decks, progress, status_msgs, sync_errors, step):
    """Trata erros inesperados durante sincronização."""
    # Tentar obter o nome do deck para a mensagem de erro
    try:
        deck_info = remote_decks[deckKey]
        deck_id = deck_info["deck_id"]
        deck = mw.col.decks.get(deck_id)
        deckName = deck["name"] if deck else deck_info.get("deck_name", str(deck_id))
    except:
        deckName = "Unknown"
    
    error_msg = f"Unexpected error syncing deck '{deckName}': {str(e)}"
    sync_errors.append(error_msg)
    status_msgs.append(error_msg)
    _update_progress_text(progress, status_msgs)
    step += 3
    progress.setValue(step)
    mw.app.processEvents()
    return step, sync_errors

def _finalize_sync(progress, total_decks, decks_synced, total_stats, sync_errors):
    """Finaliza a sincronização mostrando resultados."""
    progress.setValue(total_decks * 3)
    mw.app.processEvents()
    
    # Remover subdecks vazios após a sincronização
    remote_decks = get_remote_decks()
    removed_subdecks = remove_empty_subdecks(remote_decks)
    
    # Preparar mensagem final para exibir na barra de progresso
    if sync_errors or total_stats['errors'] > 0:
        final_msg = f"Concluído com problemas: {decks_synced}/{total_decks} decks sincronizados"
        if total_stats['created'] > 0:
            final_msg += f", {total_stats['created']} cards criados"
        if total_stats['updated'] > 0:
            final_msg += f", {total_stats['updated']} atualizados"
        if total_stats['deleted'] > 0:
            final_msg += f", {total_stats['deleted']} deletados"
        if total_stats['ignored'] > 0:
            final_msg += f", {total_stats['ignored']} ignorados"
        if removed_subdecks > 0:
            final_msg += f", {removed_subdecks} subdecks vazios removidos"
        final_msg += f", {total_stats['errors'] + len(sync_errors)} erros"
    else:
        final_msg = f"Sincronização concluída com sucesso!"
        if total_stats['created'] > 0:
            final_msg += f" {total_stats['created']} cards criados"
        if total_stats['updated'] > 0:
            final_msg += f", {total_stats['updated']} atualizados"
        if total_stats['deleted'] > 0:
            final_msg += f", {total_stats['deleted']} deletados"
        if total_stats['ignored'] > 0:
            final_msg += f", {total_stats['ignored']} ignorados"
        if removed_subdecks > 0:
            final_msg += f", {removed_subdecks} subdecks vazios removidos"
    
    # Exibir mensagem final na barra e adicionar botão OK
    # Usar uma lista temporária para a mensagem final
    final_status_msgs = [final_msg]
    _update_progress_text(progress, final_status_msgs, max_lines=5)  # Permitir mais linhas para mensagem final
    
    # Criar e configurar o botão OK
    ok_button = QPushButton("OK")
    progress.setCancelButton(ok_button)
    
    # Aguardar o usuário clicar em OK
    while progress.isVisible() and not progress.wasCanceled():
        mw.app.processEvents()
        time.sleep(0.1)
    
    # Mostrar resumo abrangente dos resultados da sincronização
    _show_sync_summary(sync_errors, total_stats, decks_synced, total_decks, removed_subdecks)

def _show_sync_summary(sync_errors, total_stats, decks_synced, total_decks, removed_subdecks=0):
    """Mostra resumo detalhado da sincronização com área de scroll para detalhes."""
    # Preparar o resumo básico
    if sync_errors or total_stats['errors'] > 0:
        summary = f"Sincronização concluída com alguns problemas:\n\n"
        summary += f"Decks sincronizados: {decks_synced}/{total_decks}\n"
        summary += f"Cards criados: {total_stats['created']}\n"
        summary += f"Cards atualizados: {total_stats['updated']}\n"
        summary += f"Cards deletados: {total_stats['deleted']}\n"
        summary += f"Cards ignorados: {total_stats['ignored']}\n"
        if removed_subdecks > 0:
            summary += f"Subdecks vazios removidos: {removed_subdecks}\n"
        summary += f"Erros encontrados: {total_stats['errors'] + len(sync_errors)}\n\n"
        
        # Adicionar erros de nível de deck
        if sync_errors:
            summary += "Erros de sincronização de decks:\n"
            summary += "\n".join(sync_errors) + "\n\n"
        
        # Adicionar erros de nível de note
        if total_stats['error_details']:
            summary += "Erros de processamento de cards:\n"
            summary += "\n".join(total_stats['error_details'][:10])  # Limitar aos primeiros 10 erros
            if len(total_stats['error_details']) > 10:
                summary += f"\n... e mais {len(total_stats['error_details']) - 10} erros."
    else:
        summary = f"Sincronização concluída com sucesso!\n\n"
        summary += f"Decks sincronizados: {decks_synced}\n"
        summary += f"Cards criados: {total_stats['created']}\n"
        summary += f"Cards atualizados: {total_stats['updated']}\n"
        summary += f"Cards deletados: {total_stats['deleted']}\n"
        summary += f"Cards ignorados: {total_stats['ignored']}\n"
        if removed_subdecks > 0:
            summary += f"Subdecks vazios removidos: {removed_subdecks}\n"
        summary += "Nenhum erro encontrado."
    
    # Se há detalhes de atualizações, mostrar em um diálogo com scroll
    if total_stats.get('updated_details'):
        # Criar diálogo personalizado com área de scroll
        dialog = QDialog(mw)
        dialog.setWindowTitle("Resumo da Sincronização")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Área de texto para o resumo principal
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)
        summary_text.setPlainText(summary)
        summary_text.setMaximumHeight(200)
        layout.addWidget(summary_text)
        
        # Área de texto com scroll para os detalhes das atualizações
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        
        # Preparar texto detalhado das atualizações
        details = "Detalhes das atualizações realizadas:\n\n"
        for i, update in enumerate(total_stats['updated_details'], 1):
            details += f"{i}. ID: {update['id']}\n"
            details += f"   Pergunta: {update['pergunta']}\n"
            details += f"   Mudanças: {'; '.join(update['changes'])}\n\n"
        
        # Adicionar informação sobre subdecks vazios removidos, se houver
        if removed_subdecks > 0:
            details += f"\n\nSubdecks vazios removidos: {removed_subdecks}\n"
            details += "Subdecks sem cards foram automaticamente removidos para manter a organização."
        
        details_text.setPlainText(details)
        layout.addWidget(details_text)
        
        # Botões
        button_box = QDialogButtonBox(ButtonBox_Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        safe_exec_dialog(dialog)
    else:
        # Se não há detalhes de atualizações, mostrar apenas o resumo
        showInfo(summary)
