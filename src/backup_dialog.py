"""
Interface de diálogo simplificada para funcionalidades de backup
"""

from datetime import datetime
from pathlib import Path

from aqt.utils import showInfo, showWarning, showCritical

try:
    from .compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL, mw
    from .backup_system import SimplifiedBackupManager
except ImportError:
    # Para testes independentes
    from compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL, mw
    from backup_system import SimplifiedBackupManager


class BackupDialog(QDialog):
    """Diálogo simplificado para backup e restauração com suporte a dark mode"""

    def __init__(self):
        super().__init__()
        self.backup_manager = SimplifiedBackupManager()
        self.setWindowTitle("Backup Sheets2Anki")
        
        # Detectar tema
        self.is_dark_mode = self._detect_dark_mode()
        self.setup_ui()
        self._apply_theme()
        
        # Calcular e aplicar tamanho ideal automaticamente
        self._auto_resize_to_content()

    def _auto_resize_to_content(self):
        """Calcula e aplica automaticamente o tamanho ideal da janela baseado no conteúdo"""
        try:
            # Método 1: Usar sizeHint do Qt (tamanho sugerido pelo layout)
            layout = self.layout()
            if layout:
                layout.activate()
            self.adjustSize()
            suggested_size = self.sizeHint()
            
            # Método 2: Calcular baseado em métricas de fonte e conteúdo
            optimal_width, optimal_height = self._calculate_optimal_size()
            
            # Combinar os dois métodos (usar o maior)
            base_width = max(suggested_size.width(), optimal_width)
            base_height = max(suggested_size.height(), optimal_height)
            
            # Adicionar margens de segurança
            safety_margin_width = 30
            safety_margin_height = 50
            
            ideal_width = base_width + safety_margin_width
            ideal_height = base_height + safety_margin_height
            
            # Ajustar para DPI scaling
            ideal_width, ideal_height = self._adjust_for_dpi_scaling(ideal_width, ideal_height)
            
            # Verificar limites da tela
            screen_geometry = self._get_screen_geometry()
            max_width = int(screen_geometry.width() * 0.7)  # 70% da largura da tela
            max_height = int(screen_geometry.height() * 0.8)  # 80% da altura da tela
            
            # Aplicar limites (mínimo e máximo)
            final_width = max(500, min(ideal_width, max_width))
            final_height = max(400, min(ideal_height, max_height))
            
            # Definir tamanho e redimensionar
            self.setMinimumSize(final_width, final_height)
            self.resize(final_width, final_height)
            
            print(f"[DEBUG] Auto-resize: {final_width}x{final_height}")
            print(f"[DEBUG] Baseado em: sizeHint={suggested_size.width()}x{suggested_size.height()}, optimal={optimal_width}x{optimal_height}")
            
        except Exception as e:
            # Fallback robusto em caso de erro
            print(f"[DEBUG] Erro no auto-resize, usando tamanho padrão: {e}")
            self.setMinimumSize(550, 500)
            self.resize(550, 500)

    def _get_screen_geometry(self):
        """Obtém a geometria da tela onde a janela será exibida"""
        try:
            from aqt.qt import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                return screen.availableGeometry()
        except:
            pass
        
        # Fallback para tamanho padrão
        from aqt.qt import QRect
        return QRect(0, 0, 1920, 1080)

    def _calculate_optimal_size(self):
        """Calcula o tamanho ótimo baseado em múltiplos fatores"""
        try:
            # Obter métricas de fonte atual
            font_metrics = self.fontMetrics()
            font_height = font_metrics.height()
            char_width = font_metrics.averageCharWidth()
            
            # Calcular baseado no conteúdo de texto
            estimated_width = max(
                len("Sistema simplificado de backup que preserva todos os seus dados:") * char_width,
                len("• Decks e notas (com histórico de estudo)") * char_width,
                450  # largura mínima
            )
            
            # Calcular altura baseada no número de elementos
            title_height = font_height * 2  # título + margem
            description_height = font_height * 4  # 3 linhas + margem
            backup_section_height = font_height * 4  # descrição + botão + margens
            restore_section_height = font_height * 4  # descrição + botão + margens
            log_section_height = 120  # área de log fixa
            buttons_height = font_height * 3  # botão fechar + margens
            
            estimated_height = (title_height + description_height + 
                              backup_section_height + restore_section_height + 
                              log_section_height + buttons_height + 60)  # margem extra
            
            return estimated_width, estimated_height
            
        except Exception as e:
            print(f"[DEBUG] Erro no cálculo ótimo: {e}")
            return 550, 500  # fallback

    def _adjust_for_dpi_scaling(self, width, height):
        """Ajusta o tamanho para diferentes escalas de DPI"""
        try:
            from aqt.qt import QApplication
            screen = QApplication.primaryScreen()
            if screen:
                dpi_ratio = screen.devicePixelRatio()
                if dpi_ratio > 1.0:
                    # Para telas de alta resolução, ajustar proporcionalmente
                    width = int(width * min(dpi_ratio, 1.5))  # limitar o ajuste
                    height = int(height * min(dpi_ratio, 1.5))
            
            return width, height
        except:
            return width, height

    def _detect_dark_mode(self) -> bool:
        """Detecta se o Anki está usando tema escuro"""
        try:
            if mw and hasattr(mw, 'pm') and hasattr(mw.pm, 'night_mode'):
                return mw.pm.night_mode()
            # Fallback: verificar cor de fundo da janela principal
            if mw:
                palette = mw.palette()
                bg_color = palette.color(palette.Window)
                # Se a cor de fundo for escura, assumir dark mode
                return bg_color.lightness() < 128
        except:
            pass
        return False
    
    def _get_theme_colors(self) -> dict:
        """Retorna cores baseadas no tema atual"""
        if self.is_dark_mode:
            return {
                'bg_primary': '#2b2b2b',
                'bg_secondary': '#3c3c3c', 
                'bg_accent': '#404040',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#999999',
                'success': '#4CAF50',
                'success_hover': '#45a049',
                'danger': '#f44336', 
                'danger_hover': '#da190b',
                'border': '#555555',
                'log_bg': '#1e1e1e',
                'warning': '#ff9800'
            }
        else:
            return {
                'bg_primary': '#ffffff',
                'bg_secondary': '#f5f5f5',
                'bg_accent': '#f0f0f0', 
                'text_primary': '#000000',
                'text_secondary': '#333333',
                'text_muted': '#666666',
                'success': '#4CAF50',
                'success_hover': '#45a049',
                'danger': '#f44336',
                'danger_hover': '#da190b', 
                'border': '#dddddd',
                'log_bg': '#fafafa',
                'warning': '#ff5722'
            }

    def setup_ui(self):
        """Configura a interface simplificada"""
        layout = QVBoxLayout()
        colors = self._get_theme_colors()

        # Título
        title = QLabel("🔄 Sistema de Backup Sheets2Anki")
        title.setStyleSheet(f"""
            font-size: 18px; 
            font-weight: bold; 
            margin: 10px; 
            text-align: center;
            color: {colors['text_primary']};
        """)
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
        desc.setStyleSheet(f"""
            margin: 10px; 
            padding: 12px; 
            background-color: {colors['bg_accent']}; 
            border-radius: 8px;
            color: {colors['text_secondary']};
            border: 1px solid {colors['border']};
        """)
        layout.addWidget(desc)

        # Seção de Gerar Backup
        backup_group = QGroupBox("📦 Gerar Backup Completo")
        backup_group.setStyleSheet(f"""
            QGroupBox {{ 
                font-weight: bold; 
                margin-top: 10px;
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        backup_layout = QVBoxLayout()

        backup_desc = QLabel(
            "Cria um arquivo .zip contendo:\n"
            "• Arquivo .apkg do deck principal (com scheduling e mídia)\n"
            "• Todas as configurações do Sheets2Anki\n"
            "• Metadados para restauração completa"
        )
        backup_desc.setWordWrap(True)
        backup_desc.setStyleSheet(f"""
            margin: 10px; 
            color: {colors['text_muted']};
            padding: 5px;
        """)
        backup_layout.addWidget(backup_desc)

        backup_btn = QPushButton("🔄 Gerar Backup Completo")
        backup_btn.clicked.connect(self.create_backup)
        backup_btn.setStyleSheet(f"""
            QPushButton {{ 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                background-color: {colors['success']}; 
                color: white; 
                border-radius: 8px; 
                border: none;
            }} 
            QPushButton:hover {{ 
                background-color: {colors['success_hover']}; 
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
        """)
        backup_layout.addWidget(backup_btn)

        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # Seção de Restaurar Backup
        restore_group = QGroupBox("📥 Recuperar do Backup")
        restore_group.setStyleSheet(f"""
            QGroupBox {{ 
                font-weight: bold; 
                margin-top: 10px;
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        restore_layout = QVBoxLayout()

        restore_desc = QLabel(
            "⚠️ OPERAÇÃO DESTRUTIVA ⚠️\n\n"
            "Remove completamente o deck atual 'Sheets2Anki' e restaura\n"
            "o estado exato do backup, incluindo todas as configurações."
        )
        restore_desc.setWordWrap(True)
        restore_desc.setStyleSheet(f"""
            margin: 10px; 
            color: {colors['warning']}; 
            font-weight: bold;
            padding: 10px;
            background-color: {colors['bg_accent']};
            border-radius: 5px;
            border: 1px solid {colors['warning']};
        """)
        restore_layout.addWidget(restore_desc)

        restore_btn = QPushButton("📥 Recuperar do Backup")
        restore_btn.clicked.connect(self.restore_backup)
        restore_btn.setStyleSheet(f"""
            QPushButton {{ 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                background-color: {colors['danger']}; 
                color: white; 
                border-radius: 8px; 
                border: none;
            }} 
            QPushButton:hover {{ 
                background-color: {colors['danger_hover']}; 
            }}
            QPushButton:pressed {{
                background-color: #c62828;
            }}
        """)
        restore_layout.addWidget(restore_btn)

        restore_group.setLayout(restore_layout)
        layout.addWidget(restore_group)

        # Log area
        log_group = QGroupBox("📋 Log de Operações")
        log_group.setStyleSheet(f"""
            QGroupBox {{ 
                font-weight: bold; 
                margin-top: 10px;
                color: {colors['text_primary']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(90)  # Reduzido de 120 para 90
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(f"""
            background-color: {colors['log_bg']}; 
            border: 1px solid {colors['border']};
            color: {colors['text_secondary']};
            border-radius: 5px;
            padding: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        """)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Botão fechar
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 10px; 
                margin-top: 10px;
                font-size: 13px;
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {colors['bg_accent']};
            }}
            QPushButton:pressed {{
                background-color: {colors['border']};
            }}
        """)
        layout.addWidget(close_btn)

        self.setLayout(layout)
    
    def _apply_theme(self):
        """Aplica o tema geral ao diálogo"""
        colors = self._get_theme_colors()
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg_primary']};
                color: {colors['text_primary']};
            }}
        """)

    def log(self, message: str):
        """Adiciona mensagem ao log e reajusta tamanho se necessário"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Verificar se o log está ficando muito cheio e reajustar
        try:
            text_content = self.log_text.toPlainText()
            if text_content.count('\n') > 3:
                self._maybe_readjust_size()
        except:
            pass  # Ignorar erro de verificação do log

    def _maybe_readjust_size(self):
        """Reajusta o tamanho da janela se o conteúdo aumentou significativamente"""
        try:
            current_height = self.height()
            suggested_height = self.sizeHint().height()
            
            # Se o conteúdo sugerido é muito maior que o atual, reajustar
            if suggested_height > current_height + 50:
                new_height = min(suggested_height + 30, int(self._get_screen_geometry().height() * 0.8))
                self.resize(self.width(), new_height)
                print(f"[DEBUG] Reajustado altura para: {new_height}")
        except Exception as e:
            print(f"[DEBUG] Erro no reajuste dinâmico: {e}")

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
