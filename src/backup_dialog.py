"""
Interface de diálogo simplificada para funcionalidades de backup
"""

from datetime import datetime
from pathlib import Path

from aqt.utils import showInfo, showWarning, showCritical

try:
    from .compat import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, QCheckBox, QSpinBox, QLineEdit, WINDOW_MODAL, mw
    from .backup_system import SimplifiedBackupManager
    from .config_manager import get_auto_backup_config, set_auto_backup_config, get_auto_backup_directory
except ImportError:
    # Para testes independentes
    from compat import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, QCheckBox, QSpinBox, QLineEdit, WINDOW_MODAL, mw
    from backup_system import SimplifiedBackupManager
    from config_manager import get_auto_backup_config, set_auto_backup_config, get_auto_backup_directory


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
            
            # Aplicar limites (mínimo e máximo) - ajustado para layout de 3 colunas
            final_width = max(1000, min(ideal_width, max_width))  # largura mínima maior para 3 colunas
            final_height = max(550, min(ideal_height, max_height))  # altura mínima reduzida (seções lado a lado)
            
            # Definir tamanho e redimensionar
            self.setMinimumSize(final_width, final_height)
            self.resize(final_width, final_height)
            
            print(f"[DEBUG] Auto-resize: {final_width}x{final_height}")
            print(f"[DEBUG] Baseado em: sizeHint={suggested_size.width()}x{suggested_size.height()}, optimal={optimal_width}x{optimal_height}")
            
        except Exception as e:
            # Fallback robusto em caso de erro - ajustado para layout de 3 colunas
            print(f"[DEBUG] Erro no auto-resize, usando tamanho padrão: {e}")
            self.setMinimumSize(1000, 600)
            self.resize(1000, 600)

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
            
            # Calcular baseado no layout lado a lado com 3 colunas
            # Largura: três seções lado a lado + margens
            section_width = 320  # largura de cada seção (reduzida para 3 colunas)
            estimated_width = max(
                section_width * 3 + 90,  # três seções + espaçamento + margens
                len("Sistema simplificado que preserva TODOS os seus dados:") * char_width,
                1000  # largura mínima para layout de 3 colunas
            )
            
            # Calcular altura baseada no número de elementos (layout vertical)
            title_height = font_height * 2  # título + margem
            description_height = font_height * 4  # 3 linhas + margem
            # Com layout de 3 colunas lado a lado, a altura é a da seção mais alta
            max_section_height = font_height * 9  # seções lado a lado (altura da maior - 3 colunas)
            log_section_height = 120  # área de log fixa
            buttons_height = font_height * 3  # botão fechar + margens
            
            estimated_height = (title_height + description_height + 
                              max_section_height + 
                              log_section_height + buttons_height + 80)  # margem para 3 colunas
            
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
                'primary': '#4CAF50',
                'primary_hover': '#45a049',
                'success': '#4CAF50',
                'success_hover': '#45a049',
                'info': '#2196F3',
                'info_hover': '#1976D2',
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
                'primary': '#4CAF50',
                'primary_hover': '#45a049',
                'success': '#4CAF50',
                'success_hover': '#45a049',
                'info': '#2196F3',
                'info_hover': '#1976D2',
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
        backup_group = QGroupBox("� Gerar Backup")
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
            "Escolha o tipo de backup que deseja criar:"
        )
        backup_desc.setWordWrap(True)
        backup_desc.setStyleSheet(f"margin: 10px; color: {colors['text_secondary']};")
        backup_layout.addWidget(backup_desc)

        # Backup completo
        full_backup_desc = QLabel(
            "🔄 Backup Completo:\n"
            "• Inclui todas as notas e cards do deck\n"
            "• Inclui todas as configurações do addon\n"
            "• Para restauração completa em caso de perda de dados"
        )
        full_backup_desc.setWordWrap(True)
        full_backup_desc.setStyleSheet(f"""
            margin: 5px; 
            color: {colors['text_secondary']}; 
            padding: 10px;
            background-color: {colors['bg_accent']};
            border-radius: 5px;
            border: 1px solid {colors['border']};
        """)
        backup_layout.addWidget(full_backup_desc)

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
                margin-bottom: 10px;
            }} 
            QPushButton:hover {{ 
                background-color: {colors['success_hover']}; 
            }}
            QPushButton:pressed {{
                background-color: #3d8b40;
            }}
        """)
        backup_layout.addWidget(backup_btn)

        # Backup só de configurações
        config_backup_desc = QLabel(
            "⚙️ Backup de Configurações:\n"
            "• Inclui apenas as configurações do addon\n"
            "• Não inclui notas nem cards\n"
            "• Para recuperar configurações após reinstalar o addon"
        )
        config_backup_desc.setWordWrap(True)
        config_backup_desc.setStyleSheet(f"""
            margin: 5px; 
            color: {colors['text_secondary']}; 
            padding: 10px;
            background-color: {colors['bg_accent']};
            border-radius: 5px;
            border: 1px solid {colors['border']};
        """)
        backup_layout.addWidget(config_backup_desc)

        config_backup_btn = QPushButton("⚙️ Gerar Backup de Configurações")
        config_backup_btn.clicked.connect(self.create_config_backup)
        config_backup_btn.setStyleSheet(f"""
            QPushButton {{ 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                background-color: {colors['info']}; 
                color: white; 
                border-radius: 8px; 
                border: none;
            }} 
            QPushButton:hover {{ 
                background-color: {colors['info_hover']}; 
            }}
            QPushButton:pressed {{
                background-color: #1976d2;
            }}
        """)
        backup_layout.addWidget(config_backup_btn)

        backup_group.setLayout(backup_layout)

        # Seção de Restaurar Backup
        restore_group = QGroupBox("📥 Recuperar Backup")
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

        restore_main_desc = QLabel(
            "Escolha o tipo de recuperação:"
        )
        restore_main_desc.setWordWrap(True)
        restore_main_desc.setStyleSheet(f"margin: 10px; color: {colors['text_secondary']};")
        restore_layout.addWidget(restore_main_desc)

        # Restauração completa
        restore_desc = QLabel(
            "⚠️ RECUPERAÇÃO COMPLETA (DESTRUTIVA):\n"
            "• Remove completamente o deck atual 'Sheets2Anki'\n"
            "• Restaura o estado exato do backup\n"
            "• Inclui todas as configurações e dados"
        )
        restore_desc.setWordWrap(True)
        restore_desc.setStyleSheet(f"""
            margin: 5px; 
            color: {colors['warning']}; 
            font-weight: bold;
            padding: 10px;
            background-color: {colors['bg_accent']};
            border-radius: 5px;
            border: 1px solid {colors['warning']};
        """)
        restore_layout.addWidget(restore_desc)

        restore_btn = QPushButton("📥 Recuperação Completa")
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
                margin-bottom: 10px;
            }} 
            QPushButton:hover {{ 
                background-color: {colors['danger_hover']}; 
            }}
            QPushButton:pressed {{
                background-color: #c62828;
            }}
        """)
        restore_layout.addWidget(restore_btn)

        # Restauração só de configurações
        config_restore_desc = QLabel(
            "🔧 RECUPERAÇÃO DE CONFIGURAÇÕES (SEGURA):\n"
            "• Restaura apenas as configurações do addon\n"
            "• NÃO altera nenhum dado do Anki\n"
            "• Ideal após reinstalar o addon"
        )
        config_restore_desc.setWordWrap(True)
        config_restore_desc.setStyleSheet(f"""
            margin: 5px; 
            color: {colors['info']}; 
            font-weight: bold;
            padding: 10px;
            background-color: {colors['bg_accent']};
            border-radius: 5px;
            border: 1px solid {colors['info']};
        """)
        restore_layout.addWidget(config_restore_desc)

        config_restore_btn = QPushButton("🔧 Recuperar Apenas Configurações")
        config_restore_btn.clicked.connect(self.restore_config_only)
        config_restore_btn.setStyleSheet(f"""
            QPushButton {{ 
                padding: 12px; 
                font-size: 14px; 
                font-weight: bold; 
                background-color: {colors['info']}; 
                color: white; 
                border-radius: 8px; 
                border: none;
            }} 
            QPushButton:hover {{ 
                background-color: {colors['info_hover']}; 
            }}
            QPushButton:pressed {{
                background-color: #1976d2;
            }}
        """)
        restore_layout.addWidget(config_restore_btn)

        restore_group.setLayout(restore_layout)

        # Seção de Configurações de Backup Automático
        auto_backup_group = QGroupBox("⚙️ Backup Automático")
        auto_backup_group.setStyleSheet(f"""
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
        auto_backup_layout = QVBoxLayout()

        # Descrição
        auto_backup_desc = QLabel(
            "🔄 Backup automático a cada sincronização.\n"
            "Configure onde salvar e quantos manter:"
        )
        auto_backup_desc.setWordWrap(True)
        auto_backup_desc.setStyleSheet(f"margin: 5px; color: {colors['text_secondary']};")
        auto_backup_layout.addWidget(auto_backup_desc)

        # Layout para configurações
        config_layout = QVBoxLayout()

        # Habilitar/Desabilitar backup automático
        self.auto_backup_enabled = QCheckBox("Habilitar backup automático")
        self.auto_backup_enabled.setStyleSheet(f"""
            QCheckBox {{
                color: {colors['text_primary']};
                font-weight: bold;
            }}
        """)
        config_layout.addWidget(self.auto_backup_enabled)

        # Diretório
        dir_layout = QHBoxLayout()
        dir_label = QLabel("Diretório:")
        dir_label.setStyleSheet(f"color: {colors['text_primary']};")
        dir_layout.addWidget(dir_label)

        self.auto_backup_dir = QLineEdit()
        self.auto_backup_dir.setPlaceholderText("Diretório padrão se vazio")
        self.auto_backup_dir.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px;
                border: 1px solid {colors['border']};
                border-radius: 4px;
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
            }}
        """)
        dir_layout.addWidget(self.auto_backup_dir)

        dir_browse_btn = QPushButton("📁 Procurar")
        dir_browse_btn.clicked.connect(self.browse_auto_backup_directory)
        dir_browse_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 12px;
                background-color: {colors['info']};
                color: white;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {colors['info_hover']};
            }}
        """)
        dir_layout.addWidget(dir_browse_btn)
        config_layout.addLayout(dir_layout)

        # Máximo de arquivos
        max_files_layout = QHBoxLayout()
        max_files_label = QLabel("Máximo de arquivos:")
        max_files_label.setStyleSheet(f"color: {colors['text_primary']};")
        max_files_layout.addWidget(max_files_label)

        self.auto_backup_max_files = QSpinBox()
        self.auto_backup_max_files.setMinimum(1)
        self.auto_backup_max_files.setMaximum(200)
        self.auto_backup_max_files.setValue(50)
        self.auto_backup_max_files.setStyleSheet(f"""
            QSpinBox {{
                padding: 8px;
                border: 1px solid {colors['border']};
                border-radius: 4px;
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
                min-width: 80px;
            }}
        """)
        max_files_layout.addWidget(self.auto_backup_max_files)
        max_files_layout.addStretch()
        config_layout.addLayout(max_files_layout)

        # Botões
        buttons_layout = QHBoxLayout()
        
        save_config_btn = QPushButton("💾 Salvar")
        save_config_btn.clicked.connect(self.save_auto_backup_config)
        save_config_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                font-weight: bold;
                background-color: {colors['primary']};
                color: white;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
        """)
        buttons_layout.addWidget(save_config_btn)

        show_backups_btn = QPushButton("📁 Ver")
        show_backups_btn.clicked.connect(self.show_auto_backups)
        show_backups_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px 16px;
                background-color: {colors['info']};
                color: white;
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {colors['info_hover']};
            }}
        """)
        buttons_layout.addWidget(show_backups_btn)
        buttons_layout.addStretch()

        config_layout.addLayout(buttons_layout)
        auto_backup_layout.addLayout(config_layout)
        auto_backup_group.setLayout(auto_backup_layout)

        # Layout horizontal para colocar as três seções lado a lado
        sections_layout = QHBoxLayout()
        sections_layout.setSpacing(15)  # espaçamento entre as seções (reduzido para 3 colunas)
        sections_layout.addWidget(backup_group)
        sections_layout.addWidget(restore_group)
        sections_layout.addWidget(auto_backup_group)
        
        # Garantir que as três seções tenham largura igual no layout horizontal
        sections_layout.setStretch(0, 1)  # backup_group
        sections_layout.setStretch(1, 1)  # restore_group
        sections_layout.setStretch(2, 1)  # auto_backup_group
        
        layout.addLayout(sections_layout)

        # Carregar configurações atuais
        self._load_auto_backup_config()

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

    def create_config_backup(self):
        """Cria um backup apenas das configurações"""
        # Escolher local para salvar
        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Backup de Configurações",
            f"sheets2anki_config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "Arquivos ZIP (*.zip)"
        )

        if backup_path:
            self.log("⚙️ Iniciando criação de backup de configurações...")
            
            # Mostrar progresso
            progress = QProgressDialog("Criando backup de configurações...", "Cancelar", 0, 0, self)
            progress.setWindowModality(WINDOW_MODAL)
            progress.show()

            success = self.backup_manager.create_config_backup(backup_path)
            progress.close()

            if success:
                self.log("✅ Backup de configurações criado com sucesso!")
                showInfo(
                    f"✅ Backup de configurações criado com sucesso!\n\n"
                    f"📁 Local: {backup_path}\n\n"
                    f"O arquivo contém:\n"
                    f"• Configurações completas do Sheets2Anki\n"
                    f"• Informações de decks remotos\n"
                    f"• Metadados para religação automática\n\n"
                    f"💡 Use este backup para restaurar apenas as\n"
                    f"configurações após reinstalar o addon."
                )
            else:
                self.log("❌ Erro ao criar backup de configurações")

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

    def restore_config_only(self):
        """Restaura apenas as configurações de um backup"""
        # Escolher arquivo de backup
        backup_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo de Backup para Recuperar Configurações",
            "",
            "Arquivos ZIP (*.zip)"
        )

        if backup_path:
            self.log("🔧 Iniciando recuperação de configurações...")
            
            # Mostrar progresso
            progress = QProgressDialog("Recuperando configurações...", "Cancelar", 0, 0, self)
            progress.setWindowModality(WINDOW_MODAL)
            progress.show()

            success = self.backup_manager.restore_config_only(backup_path)
            progress.close()

            if success:
                self.log("✅ Configurações recuperadas com sucesso!")
                self.log("ℹ️ Reinicie o Anki para finalizar a aplicação das configurações")
            else:
                self.log("❌ Erro ao recuperar configurações")

    def _load_auto_backup_config(self):
        """Carrega as configurações atuais de backup automático"""
        try:
            config = get_auto_backup_config()
            
            self.auto_backup_enabled.setChecked(config.get("enabled", True))
            self.auto_backup_dir.setText(config.get("directory", ""))
            self.auto_backup_max_files.setValue(config.get("max_files", 50))
            
        except Exception as e:
            self.log(f"⚠️ Erro ao carregar configurações de backup automático: {e}")

    def browse_auto_backup_directory(self):
        """Abre diálogo para escolher diretório de backup automático"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Escolher Diretório para Backups Automáticos",
            self.auto_backup_dir.text() or str(Path.home() / "Documents")
        )
        
        if directory:
            self.auto_backup_dir.setText(directory)

    def save_auto_backup_config(self):
        """Salva as configurações de backup automático"""
        try:
            enabled = self.auto_backup_enabled.isChecked()
            directory = self.auto_backup_dir.text().strip()
            max_files = self.auto_backup_max_files.value()
            
            success = set_auto_backup_config(
                enabled=enabled,
                directory=directory,
                max_files=max_files
            )
            
            if success:
                self.log("✅ Configurações de backup automático salvas!")
                showInfo(
                    f"✅ Configurações salvas com sucesso!\n\n"
                    f"• Backup automático: {'Habilitado' if enabled else 'Desabilitado'}\n"
                    f"• Diretório: {directory or 'Padrão (Documentos/Sheets2Anki/AutoBackups)'}\n"
                    f"• Máximo de arquivos: {max_files}\n\n"
                    f"Os backups automáticos serão criados a cada sincronização."
                )
            else:
                self.log("❌ Erro ao salvar configurações")
                showWarning("Erro ao salvar configurações de backup automático.")
                
        except Exception as e:
            self.log(f"❌ Erro ao salvar configurações: {e}")
            showWarning(f"Erro ao salvar configurações: {e}")

    def show_auto_backups(self):
        """Mostra informações sobre os backups automáticos"""
        try:
            # Obter informações dos backups
            backup_info = self.backup_manager.get_auto_backup_info()
            
            if backup_info.get("error"):
                showWarning(f"Erro ao obter informações de backup: {backup_info['error']}")
                return
            
            # Construir mensagem informativa
            message = f"📁 INFORMAÇÕES DOS BACKUPS AUTOMÁTICOS\n\n"
            message += f"• Status: {'Habilitado' if backup_info['enabled'] else 'Desabilitado'}\n"
            message += f"• Diretório: {backup_info['directory']}\n"
            message += f"• Máximo de arquivos: {backup_info['max_files']}\n"
            message += f"• Total de backups: {backup_info['total_files']}\n\n"
            
            if backup_info['latest_backup']:
                latest = backup_info['latest_backup']
                message += f"🕒 BACKUP MAIS RECENTE:\n"
                message += f"• Arquivo: {latest['filename']}\n"
                message += f"• Tamanho: {latest['size']} bytes\n"
                message += f"• Criado em: {latest['created']}\n\n"
            
            if backup_info['all_backups']:
                message += f"📋 ÚLTIMOS BACKUPS:\n"
                for backup in backup_info['all_backups'][:5]:  # Mostrar apenas os 5 mais recentes
                    message += f"• {backup['filename']} ({backup['size']} bytes)\n"
                
                if len(backup_info['all_backups']) > 5:
                    message += f"... e mais {len(backup_info['all_backups']) - 5} arquivo(s)\n"
            else:
                message += "Nenhum backup automático encontrado.\n"
            
            # Opção para abrir diretório
            from aqt.utils import askUser
            if askUser(
                message + "\nDeseja abrir o diretório de backups?",
                title="Backups Automáticos"
            ):
                import subprocess
                import platform
                
                # Abrir diretório no explorador de arquivos
                if platform.system() == "Windows":
                    subprocess.Popen(f'explorer "{backup_info["directory"]}"')
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", backup_info["directory"]])
                else:  # Linux
                    subprocess.Popen(["xdg-open", backup_info["directory"]])
            
            self.log(f"📁 Informações de backup exibidas: {backup_info['total_files']} arquivo(s)")
            
        except Exception as e:
            self.log(f"❌ Erro ao mostrar informações de backup: {e}")
            showWarning(f"Erro ao obter informações de backup: {e}")


# Função para manter compatibilidade
def show_backup_dialog():
    """Mostra o diálogo de backup simplificado"""
    dialog = BackupDialog()
    dialog.exec()
