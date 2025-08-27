#!/usr/bin/env python3
"""
Sistema de Backup Simplificado para Sheets2Anki

Este módulo fornece apenas duas funcionalidades essenciais:
1. Gerar Backup: Cria backup completo (.apkg + configurações)
2. Recuperar Backup: Restaura tudo ao estado original
"""

import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from aqt import mw
from aqt.utils import showInfo, showWarning, showCritical, askUser

try:
    from .compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL
    from .config_manager import get_meta, save_meta, get_remote_decks, save_remote_decks
except ImportError:
    # Para testes independentes
    from compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL
    from config_manager import get_meta, save_meta, get_remote_decks, save_remote_decks


class SimplifiedBackupManager:
    """Gerenciador de backup simplificado - apenas Gerar e Recuperar"""

    def __init__(self):
        self.backup_version = "2.0"
        self.sheets2anki_deck_name = "Sheets2Anki"

    def create_backup(self, backup_path: str) -> bool:
        """Cria um backup completo do sistema Sheets2Anki"""
        try:
            if not mw or not mw.col:
                showCritical("Anki não está disponível para backup.")
                return False

            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Exportar deck principal como .apkg
                apkg_success = self._export_main_deck_apkg(temp_path)
                if not apkg_success:
                    showWarning("Deck 'Sheets2Anki' não encontrado. Criando backup somente das configurações.")
                
                # 2. Salvar todas as configurações
                self._save_configurations(temp_path)
                
                # 3. Salvar informações do backup
                self._save_backup_info(temp_path, apkg_success)
                
                # 4. Criar arquivo ZIP final
                self._create_backup_zip(temp_path, backup_path)
                
            return True
            
        except Exception as e:
            showCritical(f"Erro ao criar backup: {str(e)}")
            return False

    def restore_backup(self, backup_path: str) -> bool:
        """Restaura um backup completo do sistema Sheets2Anki"""
        try:
            if not os.path.exists(backup_path):
                showCritical("Arquivo de backup não encontrado.")
                return False

            if not mw or not mw.col:
                showCritical("Anki não está disponível para restauração.")
                return False

            # Confirmar operação
            if not askUser(
                "⚠️ ATENÇÃO: Esta operação irá:\n\n"
                "• Remover o deck atual 'Sheets2Anki' e todos os seus subdecks\n"
                "• Restaurar as configurações do backup\n"
                "• Importar o deck do backup\n"
                "• Recriar todas as ligações entre decks remotos e locais\n\n"
                "Deseja continuar?"
            ):
                return False

            # Criar diretório temporário para extração
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Extrair backup
                self._extract_backup_zip(backup_path, temp_path)
                
                # 2. Validar backup
                if not self._validate_backup(temp_path):
                    showCritical("Arquivo de backup inválido ou corrompido.")
                    return False
                
                # 3. Remover deck atual
                self._remove_current_sheets2anki_deck()
                
                # 4. Restaurar configurações
                self._restore_configurations(temp_path)
                
                # 5. Importar deck do backup
                apkg_path = temp_path / "sheets2anki_deck.apkg"
                if apkg_path.exists():
                    self._import_deck_apkg(str(apkg_path))
                
                # 6. Recriar ligações
                self._recreate_deck_links()
                
            showInfo("✅ Backup restaurado com sucesso!\n\nReinicie o Anki para garantir que todas as configurações sejam aplicadas.")
            return True
            
        except Exception as e:
            showCritical(f"Erro ao restaurar backup: {str(e)}")
            return False

    def _export_main_deck_apkg(self, temp_path: Path) -> bool:
        """Exporta o deck principal Sheets2Anki como .apkg"""
        try:
            if not mw or not mw.col:
                return False
                
            # Encontrar deck principal Sheets2Anki
            deck_id = None
            all_decks = mw.col.decks.all()
            for deck_dict in all_decks:
                if deck_dict['name'] == self.sheets2anki_deck_name:
                    deck_id = deck_dict['id']
                    break
            
            if deck_id is None:
                print("Deck principal 'Sheets2Anki' não encontrado para backup")
                return False
            
            # Exportar usando API do Anki
            from anki.exporting import AnkiPackageExporter
            apkg_path = temp_path / "sheets2anki_deck.apkg"
            
            # Configurar exportador com verificação de nulidade
            col = mw.col
            if col is None:
                return False
                
            exporter = AnkiPackageExporter(col)
            exporter.did = deck_id
            exporter.includeSched = True  # Include scheduling information
            exporter.includeMedia = True  # Include media
            
            # Exportar
            exporter.exportInto(str(apkg_path))
            
            print(f"Deck '{self.sheets2anki_deck_name}' exportado com sucesso")
            return True
            
        except Exception as e:
            print(f"Erro ao exportar deck principal: {e}")
            return False

    def _save_configurations(self, temp_path: Path) -> None:
        """Salva todas as configurações do addon"""
        config_dir = temp_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Salvar meta.json
        meta = get_meta()
        with open(config_dir / "meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        # Salvar config.json se existir
        addon_path = Path(__file__).parent.parent
        config_path = addon_path / "config.json"
        if config_path.exists():
            shutil.copy2(config_path, config_dir / "config.json")

    def _save_backup_info(self, temp_path: Path, apkg_included: bool) -> None:
        """Salva informações sobre o backup"""
        backup_info = {
            "version": self.backup_version,
            "created_at": datetime.now().isoformat(),
            "anki_version": getattr(mw, "version", "unknown") if mw else "unknown",
            "addon_version": "2.0",
            "apkg_included": apkg_included,
            "deck_name": self.sheets2anki_deck_name,
            "contents": ["configurations", "deck_apkg"] if apkg_included else ["configurations"]
        }
        
        with open(temp_path / "backup_info.json", "w", encoding="utf-8") as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)

    def _create_backup_zip(self, temp_path: Path, backup_path: str) -> None:
        """Cria o arquivo ZIP do backup"""
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in temp_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_path)
                    zipf.write(file_path, arcname)

    def _extract_backup_zip(self, backup_path: str, temp_path: Path) -> None:
        """Extrai o arquivo ZIP do backup"""
        with zipfile.ZipFile(backup_path, "r") as zipf:
            zipf.extractall(temp_path)

    def _validate_backup(self, temp_path: Path) -> bool:
        """Valida se o backup é válido"""
        backup_info_path = temp_path / "backup_info.json"
        if not backup_info_path.exists():
            return False
        
        try:
            with open(backup_info_path, "r", encoding="utf-8") as f:
                backup_info = json.load(f)
            
            # Verificar se é um backup válido
            return backup_info.get("version") == self.backup_version
        except:
            return False

    def _remove_current_sheets2anki_deck(self) -> None:
        """Remove o deck atual Sheets2Anki e todos os subdecks"""
        try:
            if not mw or not mw.col:
                return
                
            # Encontrar e remover deck principal
            deck_id = None
            all_decks = mw.col.decks.all()
            for deck_dict in all_decks:
                if deck_dict['name'] == self.sheets2anki_deck_name:
                    deck_id = deck_dict['id']
                    break
            
            if deck_id is not None:
                # Remover deck e todos os subdecks
                col = mw.col
                if col is not None:
                    col.decks.rem(deck_id, cardsToo=True)
                    print(f"Deck '{self.sheets2anki_deck_name}' removido para restauração")
            
        except Exception as e:
            print(f"Erro ao remover deck atual: {e}")

    def _restore_configurations(self, temp_path: Path) -> None:
        """Restaura todas as configurações do backup"""
        config_dir = temp_path / "config"
        
        # Restaurar meta.json
        meta_path = config_dir / "meta.json"
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            save_meta(meta)
        
        # Restaurar config.json se existir
        backup_config_path = config_dir / "config.json"
        if backup_config_path.exists():
            addon_path = Path(__file__).parent.parent
            target_config_path = addon_path / "config.json"
            shutil.copy2(backup_config_path, target_config_path)

    def _import_deck_apkg(self, apkg_path: str) -> None:
        """Importa o deck do arquivo .apkg"""
        try:
            # Usar importação do Anki
            from aqt.importing import doImport
            
            # Importar o arquivo
            doImport(mw, apkg_path)
            print("Deck importado com sucesso do backup")
            
        except Exception as e:
            print(f"Erro ao importar deck: {e}")
            showWarning(f"Erro ao importar deck do backup: {e}")

    def _recreate_deck_links(self) -> None:
        """Recria as ligações entre decks remotos e locais"""
        try:
            if not mw or not mw.col:
                return
                
            remote_decks = get_remote_decks()
            
            # Para cada deck remoto, encontrar o deck local correspondente
            for deck_key, deck_info in remote_decks.items():
                local_deck_name = deck_info.get("local_deck_name", "")
                if local_deck_name:
                    # Encontrar deck no Anki
                    all_decks = mw.col.decks.all()
                    for deck_dict in all_decks:
                        if deck_dict['name'] == local_deck_name:
                            # Atualizar ID do deck local
                            deck_info["local_deck_id"] = deck_dict['id']
                            print(f"Deck '{local_deck_name}' religado com ID {deck_dict['id']}")
                            break
            
            # Salvar configurações atualizadas
            save_remote_decks(remote_decks)
            
        except Exception as e:
            print(f"Erro ao recriar ligações de decks: {e}")


# Manter compatibilidade com código antigo
BackupManager = SimplifiedBackupManager
