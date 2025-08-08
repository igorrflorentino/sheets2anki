#!/usr/bin/env python3
"""
Sistema de Backup Consolidado para Sheets2Anki

Este módulo consolida as funcionalidades de backup, incluindo:
- Gerenciador de backup (BackupManager)
- Interface de diálogo para backup/restore
- Exportar configurações de decks remotos
- Importar configurações de decks remotos
- Backup completo das configurações do usuário
- Restauração de configurações
"""

import os
import json
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .compat import (
    mw, showInfo, showCritical, QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFileDialog, QGroupBox, QCheckBox,
    QTextEdit, QProgressBar, DialogAccepted, DialogRejected
)
from .config_manager import get_meta, save_meta, get_config


class BackupManager:
    """Gerenciador de backup para configurações do Sheets2Anki"""
    
    def __init__(self):
        self.backup_version = "1.0"
        
    def create_backup(self, backup_path: str, include_media: bool = False) -> bool:
        """
        Cria um backup completo das configurações
        
        Args:
            backup_path: Caminho para o arquivo de backup (.zip)
            include_media: Se deve incluir arquivos de mídia
            
        Returns:
            bool: True se o backup foi criado com sucesso
        """
        try:
            # Garantir que o diretório de backup existe
            backup_dir = Path(backup_path).parent
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Criar diretório temporário para o backup
            temp_dir = backup_dir / f"sheets2anki_backup_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # 1. Backup das configurações
                self._backup_configurations(temp_dir)
                
                # 2. Backup dos decks remotos
                self._backup_remote_decks(temp_dir)
                
                # 3. Backup das preferências do usuário
                self._backup_user_preferences(temp_dir)
                
                # 4. Backup de mídia (opcional)
                if include_media:
                    self._backup_media_files(temp_dir)
                
                # 5. Criar informações do backup
                self._create_backup_info(temp_dir)
                
                # 6. Criar arquivo ZIP
                self._create_zip_archive(temp_dir, backup_path)
                
                return True
                
            finally:
                # Limpar diretório temporário
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            showCritical(f"Erro ao criar backup: {str(e)}")
            return False
    
    def _backup_configurations(self, temp_dir: Path) -> None:
        """Backup das configurações principais"""
        config_dir = temp_dir / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Backup do config.json
        addon_path = Path(os.path.dirname(os.path.dirname(__file__)))
        config_path = addon_path / "config.json"
        if config_path.exists():
            shutil.copy2(config_path, config_dir / "config.json")
    
    def _backup_remote_decks(self, temp_dir: Path) -> None:
        """Backup dos decks remotos"""
        decks_dir = temp_dir / "decks"
        decks_dir.mkdir(exist_ok=True)
        
        # Salvar informações dos decks remotos
        meta = get_meta()
        remote_decks = meta.get("decks", {})
        
        with open(decks_dir / "remote_decks.json", 'w', encoding='utf-8') as f:
            json.dump(remote_decks, f, indent=2, ensure_ascii=False)
    
    def _backup_user_preferences(self, temp_dir: Path) -> None:
        """Backup das preferências do usuário"""
        prefs_dir = temp_dir / "preferences"
        prefs_dir.mkdir(exist_ok=True)
        
        # Backup do meta.json
        addon_path = Path(os.path.dirname(os.path.dirname(__file__)))
        meta_path = addon_path / "meta.json"
        if meta_path.exists():
            shutil.copy2(meta_path, prefs_dir / "meta.json")
    
    def _backup_media_files(self, temp_dir: Path) -> None:
        """Backup de arquivos de mídia (opcional)"""
        media_dir = temp_dir / "media"
        media_dir.mkdir(exist_ok=True)
        
        # TODO: Implementar backup de mídia se necessário
        pass
    
    def _create_backup_info(self, temp_dir: Path) -> None:
        """Criar informações sobre o backup"""
        backup_info = {
            "version": self.backup_version,
            "created_at": datetime.now().isoformat(),
            "anki_version": getattr(mw, "version", "unknown"),
            "addon_version": "2.0",  # TODO: Obter do manifest
            "contents": [
                "configurations",
                "remote_decks", 
                "user_preferences"
            ]
        }
        
        with open(temp_dir / "backup_info.json", 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    def _create_zip_archive(self, temp_dir: Path, backup_path: str) -> None:
        """Criar arquivo ZIP do backup"""
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
    
    def restore_backup(self, backup_path: str, restore_options: Dict[str, bool]) -> bool:
        """
        Restaura um backup
        
        Args:
            backup_path: Caminho para o arquivo de backup (.zip)
            restore_options: Opções de restauração
            
        Returns:
            bool: True se a restauração foi bem-sucedida
        """
        try:
            # Criar diretório temporário para extração
            temp_dir = Path(backup_path).parent / f"sheets2anki_restore_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # Extrair backup
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                # Verificar informações do backup
                if not self._validate_backup(temp_dir):
                    showCritical("Arquivo de backup inválido ou corrompido.")
                    return False
                
                # Restaurar componentes selecionados
                success = True
                
                if restore_options.get('configurations', True):
                    success &= self._restore_configurations(temp_dir)
                
                if restore_options.get('decks', True):
                    success &= self._restore_remote_decks(temp_dir)
                
                if restore_options.get('preferences', True):
                    success &= self._restore_user_preferences(temp_dir)
                
                if restore_options.get('media', True):
                    success &= self._restore_media_files(temp_dir)
                
                return success
                
            finally:
                # Limpar diretório temporário
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            showCritical(f"Erro ao restaurar backup: {str(e)}")
            return False
    
    def _validate_backup(self, temp_dir: Path) -> bool:
        """Validar se o backup é válido"""
        info_file = temp_dir / "backup_info.json"
        if not info_file.exists():
            return False
            
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
            
            return backup_info.get("version") == self.backup_version
        except:
            return False
    
    def _restore_configurations(self, temp_dir: Path) -> bool:
        """Restaurar configurações"""
        try:
            config_file = temp_dir / "config" / "config.json"
            if config_file.exists():
                addon_path = Path(os.path.dirname(os.path.dirname(__file__)))
                shutil.copy2(config_file, addon_path / "config.json")
            return True
        except Exception as e:
            showCritical(f"Erro ao restaurar configurações: {str(e)}")
            return False
    
    def _restore_remote_decks(self, temp_dir: Path) -> bool:
        """Restaurar decks remotos"""
        try:
            decks_file = temp_dir / "decks" / "remote_decks.json"
            if decks_file.exists():
                with open(decks_file, 'r', encoding='utf-8') as f:
                    remote_decks = json.load(f)
                
                # Atualizar meta com os decks
                meta = get_meta()
                meta["decks"] = remote_decks
                save_meta(meta)
            return True
        except Exception as e:
            showCritical(f"Erro ao restaurar decks remotos: {str(e)}")
            return False
    
    def _restore_user_preferences(self, temp_dir: Path) -> bool:
        """Restaurar preferências do usuário"""
        try:
            meta_file = temp_dir / "preferences" / "meta.json"
            if meta_file.exists():
                addon_path = Path(os.path.dirname(os.path.dirname(__file__)))
                shutil.copy2(meta_file, addon_path / "meta.json")
            return True
        except Exception as e:
            showCritical(f"Erro ao restaurar preferências: {str(e)}")
            return False
    
    def _restore_media_files(self, temp_dir: Path) -> bool:
        """Restaurar arquivos de mídia"""
        # TODO: Implementar se necessário
        return True
    
    def export_deck_configs(self, export_path: str, deck_hashes: List[str]) -> bool:
        """
        Exporta configurações de decks específicos
        
        Args:
            export_path: Caminho para o arquivo de exportação
            deck_hashes: Lista de hashes dos decks para exportar
            
        Returns:
            bool: True se a exportação foi bem-sucedida
        """
        try:
            meta = get_meta()
            remote_decks = meta.get("decks", {})
            
            # Filtrar apenas os decks selecionados
            selected_decks = {
                hash_key: deck_info 
                for hash_key, deck_info in remote_decks.items() 
                if hash_key in deck_hashes
            }
            
            export_data = {
                "version": "1.0",
                "exported_at": datetime.now().isoformat(),
                "decks": selected_decks
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            showCritical(f"Erro ao exportar configurações: {str(e)}")
            return False
    
    def import_deck_configs(self, import_path: str, overwrite: bool = False) -> Tuple[bool, List[str]]:
        """
        Importa configurações de decks
        
        Args:
            import_path: Caminho para o arquivo de importação
            overwrite: Se deve sobrescrever decks existentes
            
        Returns:
            Tuple[bool, List[str]]: (sucesso, lista de mensagens)
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            imported_decks = import_data.get("decks", {})
            if not imported_decks:
                return False, ["Nenhum deck encontrado no arquivo de importação."]
            
            meta = get_meta()
            current_decks = meta.get("decks", {})
            messages = []
            
            for hash_key, deck_info in imported_decks.items():
                if hash_key in current_decks and not overwrite:
                    messages.append(f"Deck {deck_info.get('remote_deck_name', hash_key)} ignorado (já existe)")
                else:
                    current_decks[hash_key] = deck_info
                    action = "sobrescrito" if hash_key in current_decks else "importado"
                    messages.append(f"Deck {deck_info.get('remote_deck_name', hash_key)} {action}")
            
            # Salvar mudanças
            meta["decks"] = current_decks
            save_meta(meta)
            
            return True, messages
            
        except Exception as e:
            return False, [f"Erro ao importar configurações: {str(e)}"]


class BackupDialog(QDialog):
    """Dialog para gerenciar backups"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backup_manager = BackupManager()
        self.setWindowTitle("Gerenciar Backups - Sheets2Anki")
        self.setMinimumSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Gerenciar Backups")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Seção de Backup Completo
        backup_group = QGroupBox("Criar Backup Completo")
        backup_layout = QVBoxLayout()
        
        backup_info = QLabel("Cria um backup completo de todas as configurações e decks remotos.")
        backup_layout.addWidget(backup_info)
        
        self.include_media_cb = QCheckBox("Incluir arquivos de mídia")
        backup_layout.addWidget(self.include_media_cb)
        
        create_backup_btn = QPushButton("Criar Backup")
        create_backup_btn.clicked.connect(self.create_backup)
        backup_layout.addWidget(create_backup_btn)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Seção de Restauração
        restore_group = QGroupBox("Restaurar Backup")
        restore_layout = QVBoxLayout()
        
        restore_info = QLabel("Restaura configurações de um backup anterior.")
        restore_layout.addWidget(restore_info)
        
        # Opções de restauração
        self.restore_configs_cb = QCheckBox("Restaurar configurações")
        self.restore_configs_cb.setChecked(True)
        restore_layout.addWidget(self.restore_configs_cb)
        
        self.restore_decks_cb = QCheckBox("Restaurar decks remotos")
        self.restore_decks_cb.setChecked(True)
        restore_layout.addWidget(self.restore_decks_cb)
        
        self.restore_prefs_cb = QCheckBox("Restaurar preferências")
        self.restore_prefs_cb.setChecked(True)
        restore_layout.addWidget(self.restore_prefs_cb)
        
        restore_backup_btn = QPushButton("Restaurar Backup")
        restore_backup_btn.clicked.connect(self.restore_backup)
        restore_layout.addWidget(restore_backup_btn)
        
        restore_group.setLayout(restore_layout)
        layout.addWidget(restore_group)
        
        # Seção de Exportação/Importação
        export_group = QGroupBox("Exportar/Importar Configurações de Decks")
        export_layout = QVBoxLayout()
        
        export_info = QLabel("Exporta ou importa configurações específicas de decks.")
        export_layout.addWidget(export_info)
        
        export_btn_layout = QHBoxLayout()
        export_decks_btn = QPushButton("Exportar Decks")
        export_decks_btn.clicked.connect(self.export_deck_configs)
        export_btn_layout.addWidget(export_decks_btn)
        
        import_decks_btn = QPushButton("Importar Decks")
        import_decks_btn.clicked.connect(self.import_deck_configs)
        export_btn_layout.addWidget(import_decks_btn)
        
        export_layout.addLayout(export_btn_layout)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Botões
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def log(self, message: str):
        """Adiciona uma mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def create_backup(self):
        """Cria um backup completo"""
        backup_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Backup", 
            f"sheets2anki_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            "Arquivos ZIP (*.zip)"
        )
        
        if backup_path:
            self.log("Criando backup...")
            include_media = self.include_media_cb.isChecked()
            
            if self.backup_manager.create_backup(backup_path, include_media):
                self.log("Backup criado com sucesso!")
                showInfo("Backup criado com sucesso!")
            else:
                self.log("Erro ao criar backup.")
    
    def restore_backup(self):
        """Restaura um backup"""
        backup_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Backup", "",
            "Arquivos ZIP (*.zip)"
        )
        
        if backup_path:
            restore_options = {
                'configurations': self.restore_configs_cb.isChecked(),
                'decks': self.restore_decks_cb.isChecked(),
                'preferences': self.restore_prefs_cb.isChecked(),
                'media': True  # Sempre tentar restaurar mídia se disponível
            }
            
            self.log("Restaurando backup...")
            
            if self.backup_manager.restore_backup(backup_path, restore_options):
                self.log("Backup restaurado com sucesso!")
                showInfo("Backup restaurado com sucesso! Reinicie o Anki para aplicar as mudanças.")
            else:
                self.log("Erro ao restaurar backup.")
    
    def export_deck_configs(self):
        """Exporta configurações de decks específicos"""
        # TODO: Implementar dialog de seleção de decks
        export_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Configurações de Decks", 
            f"sheets2anki_decks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Arquivos JSON (*.json)"
        )
        
        if export_path:
            # Por enquanto, exportar todos os decks
            meta = get_meta()
            deck_hashes = list(meta.get("decks", {}).keys())
            
            self.log("Exportando configurações de decks...")
            
            if self.backup_manager.export_deck_configs(export_path, deck_hashes):
                self.log(f"Configurações de {len(deck_hashes)} decks exportadas!")
                showInfo("Configurações exportadas com sucesso!")
            else:
                self.log("Erro ao exportar configurações.")
    
    def import_deck_configs(self):
        """Importa configurações de decks"""
        import_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Configurações de Decks", "",
            "Arquivos JSON (*.json)"
        )
        
        if import_path:
            self.log("Importando configurações de decks...")
            
            success, messages = self.backup_manager.import_deck_configs(import_path, overwrite=True)
            
            for message in messages:
                self.log(message)
            
            if success:
                showInfo(f"Configurações importadas com sucesso!\n\n" + "\n".join(messages))
            else:
                self.log("Erro ao importar configurações.")


def show_backup_dialog(parent=None):
    """Função para exibir o dialog de backup"""
    from .compat import safe_exec
    dialog = BackupDialog(parent)
    return safe_exec(dialog) == DialogAccepted
