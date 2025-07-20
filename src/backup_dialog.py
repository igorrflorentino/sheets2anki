"""
Interface de diálogo para funcionalidades de backup
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from aqt import mw
from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTabWidget,
    QWidget, QGroupBox, QCheckBox, QLineEdit, QPushButton, QListWidget,
    QListWidgetItem, QRadioButton, QButtonGroup, QAbstractItemView,
    QProgressDialog, QTextBrowser, Qt
)

# Importar constantes de seleção compatíveis
from .fix_multiselection import MULTI_SELECTION
from aqt.utils import showInfo, showWarning, askUser, getFile, getSaveFile

# Compatibilidade com diferentes versões do Qt
try:
    USER_ROLE = Qt.ItemDataRole.UserRole
    WINDOW_MODAL = Qt.WindowModality.WindowModal
except AttributeError:
    # Fallback para versões antigas
    USER_ROLE = Qt.UserRole
    WINDOW_MODAL = Qt.WindowModal

# Definir constantes diretamente para evitar problemas de tipo
if hasattr(QFrame, 'Shape') and hasattr(QFrame.Shape, 'HLine'):
    FRAME_HLINE = QFrame.Shape.HLine
elif hasattr(QFrame, 'HLine'):
    FRAME_HLINE = QFrame.HLine
else:
    FRAME_HLINE = 4  # Valor numérico para HLine

if hasattr(QFrame, 'Shadow') and hasattr(QFrame.Shadow, 'Sunken'):
    FRAME_SUNKEN = QFrame.Shadow.Sunken
elif hasattr(QFrame, 'Sunken'):
    FRAME_SUNKEN = QFrame.Sunken
else:
    FRAME_SUNKEN = 2  # Valor numérico para Sunken

from .backup_manager import BackupManager
from .config_manager import get_meta, save_meta
from .fix_exec import safe_exec


class BackupDialog(QDialog):
    """Diálogo principal para funcionalidades de backup"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backup_manager = BackupManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Configura a interface do diálogo"""
        self.setWindowTitle("Backup de Decks Remotos - Sheets2Anki")
        self.setMinimumSize(500, 400)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Gerenciador de Backup")
        # Usar type: ignore para evitar erros de tipo
        try:
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # type: ignore
        except AttributeError:
            try:
                title.setAlignment(Qt.AlignCenter)  # type: ignore
            except AttributeError:
                title.setAlignment(0x0004)  # type: ignore
        font = title.font()
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Separador
        line = QFrame()
        # Usar type: ignore para evitar erros de tipo
        try:
            line.setFrameShape(QFrame.Shape.HLine)  # type: ignore
        except (AttributeError, TypeError):
            try:
                line.setFrameShape(QFrame.HLine)  # type: ignore
            except (AttributeError, TypeError):
                line.setFrameShape(4)  # type: ignore
        
        try:
            line.setFrameShadow(QFrame.Shadow.Sunken)  # type: ignore
        except (AttributeError, TypeError):
            try:
                line.setFrameShadow(QFrame.Sunken)  # type: ignore
            except (AttributeError, TypeError):
                line.setFrameShadow(2)  # type: ignore
        layout.addWidget(line)
        
        # Informações atuais
        self.info_label = QLabel()
        self.update_info_label()
        layout.addWidget(self.info_label)
        
        # Abas
        tabs = QTabWidget()
        
        # Aba de Backup
        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, "Criar Backup")
        
        # Aba de Restauração
        restore_tab = self.create_restore_tab()
        tabs.addTab(restore_tab, "Restaurar Backup")
        
        # Aba de Exportação/Importação
        export_tab = self.create_export_tab()
        tabs.addTab(export_tab, "Exportar/Importar")
        
        layout.addWidget(tabs)
        
        # Botões
        button_layout = QHBoxLayout()
        
        help_btn = QPushButton("Ajuda")
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_backup_tab(self) -> QWidget:
        """Cria a aba de backup"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Descrição
        desc = QLabel("Crie um backup completo de todos os seus decks remotos e configurações.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Opções de backup
        options_group = QGroupBox("Opções de Backup")
        options_layout = QVBoxLayout()
        
        self.backup_configs_cb = QCheckBox("Incluir configurações gerais")
        self.backup_configs_cb.setChecked(True)
        options_layout.addWidget(self.backup_configs_cb)
        
        self.backup_decks_cb = QCheckBox("Incluir configurações de decks")
        self.backup_decks_cb.setChecked(True)
        options_layout.addWidget(self.backup_decks_cb)
        
        self.backup_preferences_cb = QCheckBox("Incluir preferências do usuário")
        self.backup_preferences_cb.setChecked(True)
        options_layout.addWidget(self.backup_preferences_cb)
        
        self.backup_media_cb = QCheckBox("Incluir arquivos de mídia")
        self.backup_media_cb.setChecked(False)
        self.backup_media_cb.setEnabled(False)  # Futuro
        options_layout.addWidget(self.backup_media_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Local do backup
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Local do backup:"))
        
        self.backup_path_edit = QLineEdit()
        # Caminho padrão
        default_path = str(Path.home() / "Documents" / f"sheets2anki_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        self.backup_path_edit.setText(default_path)
        location_layout.addWidget(self.backup_path_edit)
        
        browse_btn = QPushButton("Procurar...")
        browse_btn.clicked.connect(self.browse_backup_location)
        location_layout.addWidget(browse_btn)
        
        layout.addLayout(location_layout)
        
        # Botão de criar backup
        create_backup_btn = QPushButton("Criar Backup")
        create_backup_btn.clicked.connect(self.create_backup)
        create_backup_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }")
        layout.addWidget(create_backup_btn)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_restore_tab(self) -> QWidget:
        """Cria a aba de restauração"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Descrição
        desc = QLabel("Restaure um backup criado anteriormente.")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Seleção do arquivo
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Arquivo de backup:"))
        
        self.restore_path_edit = QLineEdit()
        file_layout.addWidget(self.restore_path_edit)
        
        browse_restore_btn = QPushButton("Procurar...")
        browse_restore_btn.clicked.connect(self.browse_restore_file)
        file_layout.addWidget(browse_restore_btn)
        
        layout.addLayout(file_layout)
        
        # Informações do backup
        self.backup_info_label = QLabel("Selecione um arquivo de backup para ver as informações.")
        self.backup_info_label.setWordWrap(True)
        layout.addWidget(self.backup_info_label)
        
        # Opções de restauração
        restore_options_group = QGroupBox("Opções de Restauração")
        restore_options_layout = QVBoxLayout()
        
        self.restore_configs_cb = QCheckBox("Restaurar configurações gerais")
        self.restore_configs_cb.setChecked(True)
        restore_options_layout.addWidget(self.restore_configs_cb)
        
        self.restore_decks_cb = QCheckBox("Restaurar configurações de decks")
        self.restore_decks_cb.setChecked(True)
        restore_options_layout.addWidget(self.restore_decks_cb)
        
        self.restore_preferences_cb = QCheckBox("Restaurar preferências do usuário")
        self.restore_preferences_cb.setChecked(True)
        restore_options_layout.addWidget(self.restore_preferences_cb)
        
        self.restore_overwrite_cb = QCheckBox("Sobrescrever configurações existentes")
        self.restore_overwrite_cb.setChecked(False)
        restore_options_layout.addWidget(self.restore_overwrite_cb)
        
        restore_options_group.setLayout(restore_options_layout)
        layout.addWidget(restore_options_group)
        
        # Botão de restaurar
        restore_btn = QPushButton("Restaurar Backup")
        restore_btn.clicked.connect(self.restore_backup)
        restore_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 8px; }")
        layout.addWidget(restore_btn)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_export_tab(self) -> QWidget:
        """Cria a aba de exportação/importação"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Seção de exportação
        export_group = QGroupBox("Exportar Configurações Específicas")
        export_layout = QVBoxLayout()
        
        desc = QLabel("Exporte apenas configurações específicas de decks.")
        desc.setWordWrap(True)
        export_layout.addWidget(desc)
        
        # Lista de decks
        self.deck_list = QListWidget()
        self.deck_list.setSelectionMode(MULTI_SELECTION)
        self.update_deck_list()
        export_layout.addWidget(self.deck_list)
        
        # Botões de seleção
        select_layout = QHBoxLayout()
        select_all_btn = QPushButton("Selecionar Todos")
        select_all_btn.clicked.connect(self.select_all_decks)
        select_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Desselecionar Todos")
        select_none_btn.clicked.connect(self.select_no_decks)
        select_layout.addWidget(select_none_btn)
        
        export_layout.addLayout(select_layout)
        
        # Export path
        export_path_layout = QHBoxLayout()
        export_path_layout.addWidget(QLabel("Arquivo:"))
        
        self.export_path_edit = QLineEdit()
        default_export = str(Path.home() / "Documents" / f"sheets2anki_decks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.export_path_edit.setText(default_export)
        export_path_layout.addWidget(self.export_path_edit)
        
        browse_export_btn = QPushButton("Procurar...")
        browse_export_btn.clicked.connect(self.browse_export_location)
        export_path_layout.addWidget(browse_export_btn)
        
        export_layout.addLayout(export_path_layout)
        
        # Botão de exportar
        export_btn = QPushButton("Exportar Selecionados")
        export_btn.clicked.connect(self.export_selected_decks)
        export_layout.addWidget(export_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Seção de importação
        import_group = QGroupBox("Importar Configurações")
        import_layout = QVBoxLayout()
        
        import_desc = QLabel("Importe configurações de decks de um arquivo exportado.")
        import_desc.setWordWrap(True)
        import_layout.addWidget(import_desc)
        
        # Import path
        import_path_layout = QHBoxLayout()
        import_path_layout.addWidget(QLabel("Arquivo:"))
        
        self.import_path_edit = QLineEdit()
        import_path_layout.addWidget(self.import_path_edit)
        
        browse_import_btn = QPushButton("Procurar...")
        browse_import_btn.clicked.connect(self.browse_import_file)
        import_path_layout.addWidget(browse_import_btn)
        
        import_layout.addLayout(import_path_layout)
        
        # Opções de importação
        self.import_mode_group = QButtonGroup()
        
        self.import_overwrite_rb = QRadioButton("Sobrescrever decks existentes")
        self.import_mode_group.addButton(self.import_overwrite_rb)
        import_layout.addWidget(self.import_overwrite_rb)
        
        self.import_skip_rb = QRadioButton("Pular decks existentes")
        self.import_skip_rb.setChecked(True)
        self.import_mode_group.addButton(self.import_skip_rb)
        import_layout.addWidget(self.import_skip_rb)
        
        self.import_ask_rb = QRadioButton("Perguntar para cada conflito")
        self.import_mode_group.addButton(self.import_ask_rb)
        import_layout.addWidget(self.import_ask_rb)
        
        # Botão de importar
        import_btn = QPushButton("Importar Configurações")
        import_btn.clicked.connect(self.import_deck_configs)
        import_layout.addWidget(import_btn)
        
        import_group.setLayout(import_layout)
        layout.addWidget(import_group)
        
        tab.setLayout(layout)
        return tab
    
    def update_info_label(self):
        """Atualiza as informações atuais"""
        try:
            meta_data = get_meta()
            deck_count = len(meta_data.get('decks', {}))
            
            info_text = f"📊 Atualmente você tem {deck_count} deck(s) remoto(s) configurado(s)."
            self.info_label.setText(info_text)
        except Exception as e:
            print(f"Erro ao atualizar info_label: {e}")
            self.info_label.setText("⚠️ Não foi possível carregar informações atuais.")
    
    def update_deck_list(self):
        """Atualiza a lista de decks"""
        self.deck_list.clear()
        
        try:
            meta_data = get_meta()
            decks = meta_data.get('decks', {})
            
            for url, deck_config in decks.items():
                name = deck_config.get('deck_name', 'Sem nome')
                item_text = f"{name} ({url})"
                item = QListWidgetItem(item_text)
                item.setData(USER_ROLE, url)
                self.deck_list.addItem(item)
                
        except Exception as e:
            print(f"Erro ao atualizar deck_list: {e}")
            showWarning(f"Erro ao carregar lista de decks: {e}")
    
    def browse_backup_location(self):
        """Procura local para salvar backup"""
        try:
            # Usar apenas os parâmetros essenciais
            filename = getSaveFile(self, "Salvar Backup")  # type: ignore
            
            if filename:
                self.backup_path_edit.setText(str(filename))  # type: ignore
        except Exception as e:
            showWarning(f"Erro ao selecionar local para salvar: {e}")
            return
    
    def browse_restore_file(self):
        """Procura arquivo de backup para restaurar"""
        try:
            # Usar apenas os parâmetros essenciais
            filename = getFile(self, "Selecionar Backup")  # type: ignore
            
            if filename:
                self.restore_path_edit.setText(str(filename))  # type: ignore
                self.load_backup_info(str(filename))  # type: ignore
        except Exception as e:
            showWarning(f"Erro ao selecionar arquivo: {e}")
            return
    
    def browse_export_location(self):
        """Procura local para salvar exportação"""
        try:
            # Usar apenas os parâmetros essenciais
            filename = getSaveFile(self, "Salvar Exportação")  # type: ignore
            
            if filename:
                self.export_path_edit.setText(str(filename))  # type: ignore
        except Exception as e:
            showWarning(f"Erro ao selecionar local para salvar: {e}")
            return
    
    def browse_import_file(self):
        """Procura arquivo para importar"""
        try:
            # Usar apenas os parâmetros essenciais
            filename = getFile(self, "Selecionar Arquivo para Importar")  # type: ignore
            
            if filename:
                self.import_path_edit.setText(str(filename))  # type: ignore
        except Exception as e:
            showWarning(f"Erro ao selecionar arquivo: {e}")
            return
    
    def load_backup_info(self, backup_path: str):
        """Carrega informações do backup"""
        info = self.backup_manager.list_backup_info(backup_path)
        
        if info:
            creation_date = info.get('creation_date', 'Desconhecido')
            total_decks = info.get('total_decks', 0)
            version = info.get('backup_version', 'Desconhecido')
            
            info_text = f"""
📅 Data de criação: {creation_date}
📦 Versão do backup: {version}
📊 Total de decks: {total_decks}
📋 Conteúdo: {', '.join(info.get('contents', []))}
            """.strip()
            
            self.backup_info_label.setText(info_text)
        else:
            self.backup_info_label.setText("❌ Não foi possível ler as informações do backup.")
    
    def select_all_decks(self):
        """Seleciona todos os decks"""
        for i in range(self.deck_list.count()):
            item = self.deck_list.item(i)
            if item is not None:
                item.setSelected(True)
    
    def select_no_decks(self):
        """Desseleciona todos os decks"""
        for i in range(self.deck_list.count()):
            item = self.deck_list.item(i)
            if item is not None:
                item.setSelected(False)
    
    def create_backup(self):
        """Cria um backup completo"""
        backup_path = self.backup_path_edit.text().strip()
        
        if not backup_path:
            showWarning("Por favor, especifique o local do backup.")
            return
        
        # Verificar se o diretório existe
        backup_dir = Path(backup_path).parent
        if not backup_dir.exists():
            if not askUser(f"O diretório {backup_dir} não existe. Deseja criá-lo?"):
                return
            
            try:
                backup_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                showWarning(f"Erro ao criar diretório: {e}")
                return
        
        # Criar backup
        include_media = self.backup_media_cb.isChecked()
        
        try:
            # Mostrar progresso
            progress = QProgressDialog("Criando backup...", "Cancelar", 0, 0, self)
            progress.setWindowModality(WINDOW_MODAL)
            progress.show()
            
            success = self.backup_manager.create_backup(backup_path, include_media)
            
            progress.close()
            
            if success:
                showInfo(f"Backup criado com sucesso!\n\nLocal: {backup_path}")
            else:
                showWarning("Erro ao criar backup. Verifique o console para mais detalhes.")
                
        except Exception as e:
            showWarning(f"Erro ao criar backup: {e}")
    
    def restore_backup(self):
        """Restaura um backup"""
        backup_path = self.restore_path_edit.text().strip()
        
        if not backup_path:
            showWarning("Por favor, selecione um arquivo de backup.")
            return
        
        if not os.path.exists(backup_path):
            showWarning("Arquivo de backup não encontrado.")
            return
        
        # Confirmar restauração
        if not askUser("Tem certeza que deseja restaurar este backup?\n\nIsso irá sobrescrever as configurações atuais."):
            return
        
        # Preparar opções de restauração
        restore_options = {
            'configs': self.restore_configs_cb.isChecked(),
            'decks': self.restore_decks_cb.isChecked(),
            'preferences': self.restore_preferences_cb.isChecked(),
            'media': False,  # Futuro
            'overwrite': self.restore_overwrite_cb.isChecked()
        }
        
        try:
            # Mostrar progresso
            progress = QProgressDialog("Restaurando backup...", "Cancelar", 0, 0, self)
            progress.setWindowModality(WINDOW_MODAL)
            progress.show()
            
            success = self.backup_manager.restore_backup(backup_path, restore_options)
            
            progress.close()
            
            if success:
                showInfo("Backup restaurado com sucesso!\n\nReinicie o Anki para aplicar todas as alterações.")
                self.update_info_label()
                self.update_deck_list()
            else:
                showWarning("Erro ao restaurar backup. Verifique o console para mais detalhes.")
                
        except Exception as e:
            showWarning(f"Erro ao restaurar backup: {e}")
    
    def export_selected_decks(self):
        """Exporta decks selecionados"""
        selected_items = self.deck_list.selectedItems()
        
        if not selected_items:
            showWarning("Por favor, selecione pelo menos um deck para exportar.")
            return
        
        export_path = self.export_path_edit.text().strip()
        
        if not export_path:
            showWarning("Por favor, especifique o local da exportação.")
            return
        
        # Obter URLs dos decks selecionados
        selected_urls = []
        for item in selected_items:
            url = item.data(USER_ROLE)
            selected_urls.append(url)
        
        try:
            success = self.backup_manager.export_decks_config(export_path, selected_urls)
            
            if success:
                showInfo(f"Configurações de {len(selected_urls)} deck(s) exportadas com sucesso!\n\nLocal: {export_path}")
            else:
                showWarning("Erro ao exportar configurações.")
                
        except Exception as e:
            showWarning(f"Erro ao exportar: {e}")
    
    def import_deck_configs(self):
        """Importa configurações de decks"""
        import_path = self.import_path_edit.text().strip()
        
        if not import_path:
            showWarning("Por favor, selecione um arquivo para importar.")
            return
        
        if not os.path.exists(import_path):
            showWarning("Arquivo de importação não encontrado.")
            return
        
        # Determinar modo de importação
        if self.import_overwrite_rb.isChecked():
            merge_mode = 'overwrite'
        elif self.import_skip_rb.isChecked():
            merge_mode = 'skip'
        else:
            merge_mode = 'ask'
        
        try:
            success = self.backup_manager.import_decks_config(import_path, merge_mode)
            
            if success:
                showInfo("Configurações importadas com sucesso!")
                self.update_info_label()
                self.update_deck_list()
            else:
                showWarning("Erro ao importar configurações.")
                
        except Exception as e:
            showWarning(f"Erro ao importar: {e}")
    
    def show_help(self):
        """Mostra ajuda sobre backup"""
        help_text = """
<h3>Ajuda - Backup de Decks Remotos</h3>

<h4>Criar Backup</h4>
<p>Cria um backup completo de todas as suas configurações de decks remotos. O backup é salvo como um arquivo ZIP que pode ser transferido para outra máquina.</p>

<h4>Restaurar Backup</h4>
<p>Restaura um backup criado anteriormente. Você pode escolher quais componentes restaurar.</p>

<h4>Exportar/Importar</h4>
<p>Permite exportar apenas configurações específicas de decks ou importar configurações de outro arquivo.</p>

<h4>Dicas</h4>
<ul>
<li>Sempre faça backup antes de fazer grandes alterações</li>
<li>Use a exportação específica para compartilhar apenas alguns decks</li>
<li>Um backup de segurança é criado automaticamente antes de restaurar</li>
</ul>
        """
        
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Ajuda - Backup")
        help_dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        text_browser = QTextBrowser()
        text_browser.setHtml(help_text)
        layout.addWidget(text_browser)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(help_dialog.accept)
        layout.addWidget(ok_btn)
        
        help_dialog.setLayout(layout)
        safe_exec(help_dialog)


def show_backup_dialog():
    """Mostra o diálogo de backup"""
    dialog = BackupDialog(mw)
    safe_exec(dialog)
