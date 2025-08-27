"""
Interface de diálogo simplificada para funcionalidades de backup
"""

from datetime import datetime
from pathlib import Path

from aqt.utils import showInfo, showWarning, showCritical

try:
    from .compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL
    from .backup_system import SimplifiedBackupManager
except ImportError:
    # Para testes independentes
    from compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL
    from backup_system import SimplifiedBackupManager


class BackupDialog(QDialog):
    """Diálogo simplificado para backup e restauração"""

    def __init__(self):
        super().__init__()
        self.backup_manager = SimplifiedBackupManager()
        self.setWindowTitle("Backup Sheets2Anki")
        self.setMinimumSize(500, 350)
        self.setup_ui()

    def setup_ui(self):
        """Configura a interface simplificada"""
        layout = QVBoxLayout()

        # Título
        title = QLabel("🔄 Sistema de Backup Sheets2Anki")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 15px; text-align: center;")
        layout.addWidget(title)

        # Descrição
        desc = QLabel(
            "Sistema simplificado que preserva TODOS os seus dados:\n\n"
            "✅ Decks e notas (incluindo histórico de estudo)\n"
            "✅ Configurações e preferências do addon\n"
            "✅ Ligações entre decks remotos e locais\n"
            "✅ Note types e templates customizados"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("margin: 15px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(desc)

        # Seção de Gerar Backup
        backup_group = QGroupBox("📦 Gerar Backup Completo")
        backup_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        backup_layout = QVBoxLayout()

        backup_desc = QLabel(
            "Cria um arquivo .zip contendo:\n"
            "• Arquivo .apkg do deck principal (com scheduling e mídia)\n"
            "• Todas as configurações do Sheets2Anki\n"
            "• Metadados para restauração completa"
        )
        backup_desc.setWordWrap(True)
        backup_desc.setStyleSheet("margin: 10px; color: #333;")
        backup_layout.addWidget(backup_desc)

        backup_btn = QPushButton("🔄 Gerar Backup Completo")
        backup_btn.clicked.connect(self.create_backup)
        backup_btn.setStyleSheet(
            "QPushButton { "
            "padding: 15px; font-size: 14px; font-weight: bold; "
            "background-color: #4CAF50; color: white; border-radius: 5px; "
            "} "
            "QPushButton:hover { background-color: #45a049; }"
        )
        backup_layout.addWidget(backup_btn)

        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # Seção de Restaurar Backup
        restore_group = QGroupBox("📥 Recuperar do Backup")
        restore_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; }")
        restore_layout = QVBoxLayout()

        restore_desc = QLabel(
            "⚠️ OPERAÇÃO DESTRUTIVA ⚠️\n\n"
            "Remove completamente o deck atual 'Sheets2Anki' e restaura\n"
            "o estado exato do backup, incluindo todas as configurações."
        )
        restore_desc.setWordWrap(True)
        restore_desc.setStyleSheet("margin: 10px; color: #d32f2f; font-weight: bold;")
        restore_layout.addWidget(restore_desc)

        restore_btn = QPushButton("📥 Recuperar do Backup")
        restore_btn.clicked.connect(self.restore_backup)
        restore_btn.setStyleSheet(
            "QPushButton { "
            "padding: 15px; font-size: 14px; font-weight: bold; "
            "background-color: #f44336; color: white; border-radius: 5px; "
            "} "
            "QPushButton:hover { background-color: #da190b; }"
        )
        restore_layout.addWidget(restore_btn)

        restore_group.setLayout(restore_layout)
        layout.addWidget(restore_group)

        # Log area
        log_group = QGroupBox("📋 Log de Operações")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: #fafafa; border: 1px solid #ddd;")
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Botão fechar
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("padding: 10px; margin-top: 10px;")
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def log(self, message: str):
        """Adiciona mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def create_backup(self):
        """Cria um backup completo"""
        # Escolher local para salvar
        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Backup Completo",
            f"sheets2anki_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "Arquivos ZIP (*.zip)"
        )

        if backup_path:
            self.log("🔄 Iniciando criação de backup completo...")
            
            # Mostrar progresso
            progress = QProgressDialog("Criando backup completo...", "Cancelar", 0, 0, self)
            progress.setWindowModality(WINDOW_MODAL)
            progress.show()

            success = self.backup_manager.create_backup(backup_path)
            progress.close()

            if success:
                self.log("✅ Backup criado com sucesso!")
                showInfo(
                    f"✅ Backup completo criado com sucesso!\n\n"
                    f"📁 Local: {backup_path}\n\n"
                    f"O arquivo contém:\n"
                    f"• Deck .apkg com todas as notas e histórico\n"
                    f"• Configurações completas do Sheets2Anki\n"
                    f"• Metadados para restauração perfeita"
                )
            else:
                self.log("❌ Erro ao criar backup")

    def restore_backup(self):
        """Restaura um backup"""
        # Escolher arquivo de backup
        backup_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo de Backup",
            "",
            "Arquivos ZIP (*.zip)"
        )

        if backup_path:
            self.log("🔄 Iniciando restauração de backup...")
            
            # Mostrar progresso
            progress = QProgressDialog("Restaurando backup...", "Cancelar", 0, 0, self)
            progress.setWindowModality(WINDOW_MODAL)
            progress.show()

            success = self.backup_manager.restore_backup(backup_path)
            progress.close()

            if success:
                self.log("✅ Backup restaurado com sucesso!")
                self.log("ℹ️ Reinicie o Anki para finalizar a restauração")
            else:
                self.log("❌ Erro ao restaurar backup")


# Função para manter compatibilidade
def show_backup_dialog():
    """Mostra o diálogo de backup simplificado"""
    dialog = BackupDialog()
    dialog.exec()
