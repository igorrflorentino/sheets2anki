"""
Módulo centralizado para geração de mensagens de confirmação de remoção de dados.

Este módulo fornece uma interface única e consistente para gerar mensagens
de confirmação quando dados de alunos precisam ser removidos.
"""

from typing import List, Optional
from .compat import MessageBox_No, MessageBox_Yes, QMessageBox, safe_exec_dialog


def generate_data_removal_confirmation_message(students_to_remove: List[str]) -> str:
    """
    Gera a mensagem padrão de confirmação para remoção de dados de alunos.
    
    Esta função centraliza a geração da mensagem para garantir consistência
    em todo o sistema.
    
    Args:
        students_to_remove: Lista de nomes de alunos/funcionalidades a serem removidos
        
    Returns:
        str: Mensagem formatada para exibição
    """
    if not students_to_remove:
        return ""
    
    # Remover duplicatas e ordenar
    unique_students = sorted(list(set(students_to_remove)))
    students_list = "\n".join([f"• {student}" for student in unique_students])
    
    message = (
        f"⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️\n\n"
        f"Os seguintes alunos foram removidos da lista de sincronização:\n\n"
        f"{students_list}\n\n"
        f"🗑️ DADOS QUE SERÃO DELETADOS PERMANENTEMENTE:\n"
        f"• Todas as notas dos alunos\n"
        f"• Todos os cards dos alunos\n"
        f"• Todos os decks dos alunos\n"
        f"• Todos os note types dos alunos\n\n"
        f"❌ ESTA AÇÃO É IRREVERSÍVEL!\n\n"
        f"Deseja continuar com a remoção dos dados?"
    )
    
    return message


def show_data_removal_confirmation_dialog(
    students_to_remove: List[str], 
    window_title: str = "Confirmar Remoção Permanente de Dados",
    parent=None
) -> bool:
    """
    Mostra o diálogo de confirmação para remoção de dados de alunos.
    
    Esta função centraliza toda a lógica de exibição do diálogo para garantir
    comportamento consistente em todo o sistema.
    
    Args:
        students_to_remove: Lista de nomes de alunos/funcionalidades a serem removidos
        window_title: Título da janela (opcional)
        parent: Widget pai (opcional)
        
    Returns:
        bool: True se o usuário confirmou a remoção, False caso contrário
    """
    if not students_to_remove:
        return False
    
    # Gerar mensagem usando a função centralizada
    message = generate_data_removal_confirmation_message(students_to_remove)
    
    # Criar MessageBox customizado
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setWindowTitle(window_title)
    msg_box.setText(message)
    msg_box.setStandardButtons(MessageBox_Yes | MessageBox_No)
    msg_box.setDefaultButton(MessageBox_No)  # Default é NOT remover
    
    # Customizar botões
    yes_btn = msg_box.button(MessageBox_Yes)
    no_btn = msg_box.button(MessageBox_No)
    
    if yes_btn:
        yes_btn.setText("🗑️ SIM, DELETAR DADOS")
        yes_btn.setStyleSheet(
            "QPushButton { background-color: #d73027; color: white; font-weight: bold; }"
        )
    
    if no_btn:
        no_btn.setText("🛡️ NÃO, MANTER DADOS")
        no_btn.setStyleSheet(
            "QPushButton { background-color: #4575b4; color: white; font-weight: bold; }"
        )
    
    # Executar diálogo
    result = safe_exec_dialog(msg_box)
    return result == MessageBox_Yes


def collect_students_for_removal(
    disabled_students: List[str], 
    missing_functionality_disabled: bool = False
) -> List[str]:
    """
    Coleta e organiza a lista de alunos/funcionalidades para remoção.
    
    Esta função centraliza a lógica de coleta para garantir que não haja
    duplicações ou inconsistências.
    
    Args:
        disabled_students: Lista de alunos desabilitados
        missing_functionality_disabled: Se True, adiciona [MISSING A.] à lista
        
    Returns:
        List[str]: Lista única e ordenada de alunos/funcionalidades para remoção
    """
    all_students_to_remove = list(disabled_students) if disabled_students else []
    
    # Adicionar [MISSING A.] se a funcionalidade foi desabilitada
    if missing_functionality_disabled:
        if "[MISSING A.]" not in all_students_to_remove:
            all_students_to_remove.append("[MISSING A.]")
    
    # Remover duplicatas e retornar lista ordenada
    return sorted(list(set(all_students_to_remove)))


# Função de conveniência para o caso mais comum
def confirm_students_removal(
    disabled_students: List[str], 
    missing_functionality_disabled: bool = False,
    window_title: str = "Confirmar Remoção Permanente de Dados",
    parent=None
) -> bool:
    """
    Função de conveniência que combina coleta e confirmação.
    
    Args:
        disabled_students: Lista de alunos desabilitados
        missing_functionality_disabled: Se True, inclui [MISSING A.] na remoção
        window_title: Título da janela (opcional)
        parent: Widget pai (opcional)
        
    Returns:
        bool: True se o usuário confirmou a remoção, False caso contrário
    """
    students_to_remove = collect_students_for_removal(
        disabled_students, missing_functionality_disabled
    )
    
    if not students_to_remove:
        return False
    
    return show_data_removal_confirmation_dialog(
        students_to_remove, window_title, parent
    )
