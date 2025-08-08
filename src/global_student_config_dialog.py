"""
Diálogo de configuração global de alunos para o addon Sheets2Anki.

Este módulo implementa uma interface para configurar globalmente quais alunos
devem ser sincronizados em todos os decks remotos.
"""

import os
from .compat import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
    QPushButton, QCheckBox, QMessageBox, QInputDialog, QSplitter,
    QListWidgetItem, Qt, mw, showWarning, QMenu, QAction,
    ButtonBox_Ok, ButtonBox_Cancel, MessageBox_Information, MessageBox_Warning,
    Horizontal, safe_exec_dialog, DialogAccepted, CustomContextMenu, safe_exec_menu,
    MessageBox_Yes, MessageBox_No
)
from .config_manager import (
    get_global_student_config, save_global_student_config,
    get_enabled_students, is_student_filter_active,
    update_available_students_from_discovery, is_auto_remove_disabled_students,
    set_auto_remove_disabled_students, is_sync_missing_students_notes,
    set_sync_missing_students_notes
)

class GlobalStudentConfigDialog(QDialog):
    """
    Diálogo para configuração global de alunos.
    
    Permite ao usuário:
    - Selecionar quais alunos sincronizar
    - Adicionar/remover alunos manualmente
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuração Global de Alunos - Sheets2Anki")
        self.setMinimumSize(500, 400)
        self.resize(600, 500)
        
        # Lista de alunos disponíveis (carregados da configuração)
        self.available_students = set()
        
        self._setup_ui()
        self._load_current_config()
        
    def _setup_ui(self):
        """Configura a interface do usuário."""
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Configuração Global de Alunos")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Descrição
        desc_label = QLabel(
            "Selecione os alunos que devem ser sincronizados. Esta configuração será\n"
            "aplicada a todos os decks remotos durante a sincronização.\n"
            "Notas interessantes para múltiplos alunos serão criadas para cada um."
        )
        desc_label.setStyleSheet("margin: 10px 0; color: #666;")
        layout.addWidget(desc_label)
        
        # Seção de opções avançadas
        options_layout = QVBoxLayout()
        
        # Checkbox para remoção automática de dados de alunos desabilitados
        self.auto_remove_checkbox = QCheckBox(
            "Remover automaticamente dados de alunos removidos da sincronização"
        )
        self.auto_remove_checkbox.setToolTip(
            "⚠️ CUIDADO: Se ativado, quando um aluno for removido da lista de sincronização,\n"
            "todos os seus dados (notas, cards, note types e decks) serão DELETADOS permanentemente\n"
            "na próxima sincronização. Esta ação é irreversível!"
        )
        self.auto_remove_checkbox.setStyleSheet("color: #d73027; font-weight: bold;")
        options_layout.addWidget(self.auto_remove_checkbox)
        
        # Adicionar um pequeno espaçamento entre os checkboxes
        options_layout.addSpacing(10)
        
        # Checkbox para sincronização de notas sem alunos específicos
        self.sync_missing_checkbox = QCheckBox(
            "Sincronizar notas sem alunos específicos para deck [MISSING A.]"
        )
        self.sync_missing_checkbox.setToolTip(
            "Se ativado, notas que não tenham alunos definidos (coluna ALUNOS vazia)\n"
            "serão sincronizadas para um subdeck chamado [MISSING A.] dentro do deck remoto.\n"
            "Se desativado, essas notas deixarão de ser sincronizadas e serão removidas."
        )
        self.sync_missing_checkbox.setStyleSheet("color: #2166ac; font-weight: bold;")
        options_layout.addWidget(self.sync_missing_checkbox)
        
        layout.addLayout(options_layout)
        
        # Container principal com splitter
        splitter = QSplitter(Horizontal)
        
        # Painel esquerdo - Alunos disponíveis
        left_panel = self._create_available_students_panel()
        splitter.addWidget(left_panel)
        
        # Painel direito - Alunos selecionados
        right_panel = self._create_selected_students_panel()
        splitter.addWidget(right_panel)
        
        # Configurar proporções do splitter
        splitter.setSizes([250, 250])
        layout.addWidget(splitter)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        
        # Botão para busca automática de alunos
        auto_discover_btn = QPushButton("🔍 Busca Automática de Alunos")
        auto_discover_btn.setToolTip("Descobrir alunos de todos os decks remotos configurados")
        auto_discover_btn.clicked.connect(self._auto_discover_students)
        button_layout.addWidget(auto_discover_btn)
        
        # Botão para adicionar aluno manualmente
        add_manual_btn = QPushButton("➕ Adicionar Aluno...")
        add_manual_btn.setToolTip("Adicionar um aluno não listado automaticamente")
        add_manual_btn.clicked.connect(self._add_manual_student)
        button_layout.addWidget(add_manual_btn)
        
        button_layout.addStretch()
        
        # Botões de OK/Cancel
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def _create_available_students_panel(self):
        """Cria o painel de alunos disponíveis."""
        from .compat import QWidget
        
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Alunos Disponíveis")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Lista de alunos disponíveis
        self.available_list = QListWidget()
        self.available_list.setToolTip(
            "Duplo clique para adicionar à lista de selecionados\n"
            "Clique direito para opções de edição/exclusão"
        )
        self.available_list.itemDoubleClicked.connect(self._move_to_selected)
        self.available_list.setContextMenuPolicy(CustomContextMenu)
        self.available_list.customContextMenuRequested.connect(self._show_available_context_menu)
        layout.addWidget(self.available_list)
        
        # Botão para adicionar selecionado
        add_btn = QPushButton("Adicionar →")
        add_btn.clicked.connect(self._move_to_selected)
        layout.addWidget(add_btn)
        
        panel.setLayout(layout)
        return panel
        
    def _create_selected_students_panel(self):
        """Cria o painel de alunos selecionados."""
        from .compat import QWidget
        
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Alunos Selecionados para Sincronização")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)
        
        # Lista de alunos selecionados
        self.selected_list = QListWidget()
        self.selected_list.setToolTip(
            "Duplo clique para remover da seleção\n"
            "Clique direito para opções de edição/exclusão"
        )
        self.selected_list.itemDoubleClicked.connect(self._move_to_available)
        self.selected_list.setContextMenuPolicy(CustomContextMenu)
        self.selected_list.customContextMenuRequested.connect(self._show_selected_context_menu)
        layout.addWidget(self.selected_list)
        
        # Botão para remover selecionado
        remove_btn = QPushButton("← Remover")
        remove_btn.clicked.connect(self._move_to_available)
        layout.addWidget(remove_btn)
        
        panel.setLayout(layout)
        return panel
        
    def _auto_discover_students(self):
        """Descobre automaticamente alunos de todos os decks remotos."""
        try:
            # Descobrir alunos
            discovered_students, new_count = update_available_students_from_discovery()
            
            # Recarregar configuração e interface
            self._load_current_config()
            
            # Mostrar resultado
            if new_count > 0:
                message = f"Busca concluída!\nEncontrados {new_count} novos alunos.\nTotal de alunos disponíveis: {len(discovered_students)}"
            else:
                message = f"Busca concluída!\nNenhum aluno novo encontrado.\nTotal de alunos disponíveis: {len(discovered_students)}"
                
            QMessageBox.information(self, "Busca Automática", message)
            
        except Exception as e:
            QMessageBox.warning(self, "Erro na Busca", 
                              f"Erro ao descobrir alunos:\n{str(e)}")
        
    def _load_current_config(self):
        """Carrega a configuração atual."""
        # Limpar listas
        self.available_list.clear()
        self.selected_list.clear()
        
        config = get_global_student_config()
        
        # Carregar alunos disponíveis e habilitados
        available_students = set(config.get("available_students", []))
        enabled_students = set(config.get("enabled_students", []))
        
        # Carregar configuração de auto-remoção
        auto_remove = config.get("auto_remove_disabled_students", False)
        self.auto_remove_checkbox.setChecked(auto_remove)
        
        # Carregar configuração de sincronização de notas sem alunos
        sync_missing = config.get("sync_missing_students_notes", False)
        self.sync_missing_checkbox.setChecked(sync_missing)
        
        # Atualizar conjunto interno
        self.available_students = available_students.copy()
        
        # Preencher lista de alunos disponíveis (não habilitados)
        for student in sorted(available_students - enabled_students):
            self.available_list.addItem(student)
            
        # Preencher lista de alunos selecionados (habilitados)
        for student in sorted(enabled_students):
            self.selected_list.addItem(student)
        
    def _move_to_selected(self):
        """Move aluno da lista disponível para selecionada."""
        current_item = self.available_list.currentItem()
        if current_item:
            student_name = current_item.text()
            
            # Remover da lista disponível
            row = self.available_list.row(current_item)
            self.available_list.takeItem(row)
            
            # Adicionar à lista selecionada (mantendo ordem)
            self._add_to_selected_sorted(student_name)
            
    def _move_to_available(self):
        """Move aluno da lista selecionada para disponível."""
        current_item = self.selected_list.currentItem()
        if current_item:
            student_name = current_item.text()
            
            # Remover da lista selecionada
            row = self.selected_list.row(current_item)
            self.selected_list.takeItem(row)
            
            # Adicionar à lista disponível (mantendo ordem)
            self._add_to_available_sorted(student_name)
            
    def _add_to_selected_sorted(self, student_name):
        """Adiciona aluno à lista selecionada mantendo ordem alfabética."""
        # Encontrar posição correta
        insert_pos = 0
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            if item and item.text() > student_name:
                insert_pos = i
                break
            insert_pos = i + 1
            
        self.selected_list.insertItem(insert_pos, student_name)
        
    def _add_to_available_sorted(self, student_name):
        """Adiciona aluno à lista disponível mantendo ordem alfabética."""
        # Encontrar posição correta
        insert_pos = 0
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item and item.text() > student_name:
                insert_pos = i
                break
            insert_pos = i + 1
            
        self.available_list.insertItem(insert_pos, student_name)
        
    def _add_manual_student(self):
        """Permite adicionar um aluno manualmente."""
        student_name, ok = QInputDialog.getText(
            self,
            "Adicionar Aluno",
            "Nome do aluno:"
        )
        
        if ok and student_name.strip():
            clean_name = student_name.strip()
            
            # Verificar se já existe (case sensitive)
            if self._student_name_exists(clean_name):
                QMessageBox.warning(self, "Aluno já existe", 
                                  f"O aluno '{clean_name}' já está na lista.")
                return
                
            # Adicionar à lista disponível
            self.available_students.add(clean_name)
            self._add_to_available_sorted(clean_name)
            
    def _show_available_context_menu(self, position):
        """Mostra menu de contexto para lista de alunos disponíveis."""
        item = self.available_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # Ação para adicionar à lista selecionada
        add_action = QAction("Adicionar aos Selecionados", self)
        add_action.triggered.connect(self._move_to_selected)
        menu.addAction(add_action)
        
        menu.addSeparator()
        
        # Ação para editar nome
        edit_action = QAction("Editar Nome...", self)
        edit_action.triggered.connect(lambda: self._edit_student_name(self.available_list))
        menu.addAction(edit_action)
        
        # Ação para deletar
        delete_action = QAction("Deletar Aluno", self)
        delete_action.triggered.connect(lambda: self._delete_student(self.available_list))
        menu.addAction(delete_action)
        
        safe_exec_menu(menu, self.available_list.mapToGlobal(position))
        
    def _show_selected_context_menu(self, position):
        """Mostra menu de contexto para lista de alunos selecionados."""
        item = self.selected_list.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # Ação para remover da lista selecionada
        remove_action = QAction("Remover dos Selecionados", self)
        remove_action.triggered.connect(self._move_to_available)
        menu.addAction(remove_action)
        
        menu.addSeparator()
        
        # Ação para editar nome
        edit_action = QAction("Editar Nome...", self)
        edit_action.triggered.connect(lambda: self._edit_student_name(self.selected_list))
        menu.addAction(edit_action)
        
        # Ação para deletar
        delete_action = QAction("Deletar Aluno", self)
        delete_action.triggered.connect(lambda: self._delete_student(self.selected_list))
        menu.addAction(delete_action)
        
        safe_exec_menu(menu, self.selected_list.mapToGlobal(position))
        
    def _edit_student_name(self, list_widget):
        """Permite editar o nome de um aluno."""
        current_item = list_widget.currentItem()
        if not current_item:
            return
            
        old_name = current_item.text()
        
        new_name, ok = QInputDialog.getText(
            self,
            "Editar Nome do Aluno",
            f"Editar nome do aluno '{old_name}':",
            text=old_name
        )
        
        if ok and new_name.strip() and new_name.strip() != old_name:
            clean_new_name = new_name.strip()
            
            # Verificar se o novo nome já existe (case sensitive)
            if self._student_name_exists(clean_new_name):
                QMessageBox.warning(self, "Nome já existe", 
                                  f"O aluno '{clean_new_name}' já está na lista.")
                return
                
            # Atualizar conjunto interno
            self.available_students.discard(old_name)
            self.available_students.add(clean_new_name)
            
            # Remover item antigo e adicionar novo ordenado
            row = list_widget.row(current_item)
            list_widget.takeItem(row)
            
            if list_widget == self.available_list:
                self._add_to_available_sorted(clean_new_name)
            else:
                self._add_to_selected_sorted(clean_new_name)
                
    def _delete_student(self, list_widget):
        """Permite deletar um aluno da lista."""
        current_item = list_widget.currentItem()
        if not current_item:
            return
            
        student_name = current_item.text()
        
        # Confirmar exclusão
        reply = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja deletar o aluno '{student_name}'?",
            MessageBox_Yes | MessageBox_No,
            MessageBox_No
        )
        
        if reply == MessageBox_Yes:
            # Remover do conjunto interno
            self.available_students.discard(student_name)
            
            # Remover da lista
            row = list_widget.row(current_item)
            list_widget.takeItem(row)
            
    def _student_name_exists(self, name):
        """Verifica se um nome de aluno já existe em qualquer lista (case sensitive)."""
        
        # Verificar lista disponível
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item and item.text() == name:
                return True
                
        # Verificar lista selecionada
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            if item and item.text() == name:
                return True
                
        return False
            
    def get_selected_config(self):
        """
        Obtém a configuração selecionada pelo usuário.
        
        Returns:
            tuple: (enabled_students, filter_enabled)
        """
        # Coletar alunos selecionados
        selected_students = []
        for i in range(self.selected_list.count()):
            item = self.selected_list.item(i)
            if item:
                selected_students.append(item.text())
        
        # O filtro está sempre ativo
        filter_enabled = True
        
        return selected_students, filter_enabled
        
    def accept(self):
        """Salva a configuração e fecha o diálogo."""
        selected_students, filter_enabled = self.get_selected_config()
        
        # Coletar todos os alunos disponíveis (das duas listas)
        available_students = []
        
        # Adicionar alunos da lista disponível
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            if item:
                available_students.append(item.text())
                
        # Adicionar alunos selecionados
        available_students.extend(selected_students)
        
        # Obter configuração de auto-remoção
        auto_remove_enabled = self.auto_remove_checkbox.isChecked()
        
        # Obter configuração de sincronização de notas sem alunos
        sync_missing_enabled = self.sync_missing_checkbox.isChecked()
        
        # Salvar configuração
        save_global_student_config(selected_students, available_students, auto_remove_enabled, sync_missing_enabled)
        
        # Configuração salva silenciosamente - sem mensagem de confirmação
        super().accept()

def show_global_student_config_dialog(parent=None):
    """
    Exibe o diálogo de configuração global de alunos.
    
    Args:
        parent: Widget pai (opcional)
        
    Returns:
        bool: True se o usuário confirmou, False se cancelou
    """
    dialog = GlobalStudentConfigDialog(parent)
    return safe_exec_dialog(dialog) == DialogAccepted
