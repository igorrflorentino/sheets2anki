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
    from .config_manager import get_meta, save_meta, get_remote_decks, save_remote_decks, get_auto_backup_config, get_auto_backup_directory
except ImportError:
    # Para testes independentes
    from compat import QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog, QTextEdit, QGroupBox, QProgressDialog, WINDOW_MODAL
    from config_manager import get_meta, save_meta, get_remote_decks, save_remote_decks, get_auto_backup_config, get_auto_backup_directory


class SimplifiedBackupManager:
    """Gerenciador de backup simplificado - Gerar Backup Completo, Recuperar Backup Completo e Recuperar Configurações"""

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
                self._save_backup_info(temp_path, apkg_success, config_only=False)
                
                # 4. Criar arquivo ZIP final
                self._create_backup_zip(temp_path, backup_path)
                
            return True
            
        except Exception as e:
            showCritical(f"Erro ao criar backup: {str(e)}")
            return False

    def create_config_backup(self, backup_path: str) -> bool:
        """Cria um backup apenas das configurações do addon"""
        try:
            if not mw or not mw.col:
                showCritical("Anki não está disponível para backup.")
                return False

            # Criar diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Salvar apenas as configurações
                self._save_configurations(temp_path)
                
                # 2. Salvar informações do backup (sem deck)
                self._save_backup_info(temp_path, apkg_included=False, config_only=True)
                
                # 3. Criar arquivo ZIP final
                self._create_backup_zip(temp_path, backup_path)
                
            return True
            
        except Exception as e:
            showCritical(f"Erro ao criar backup de configurações: {str(e)}")
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

    def restore_config_only(self, backup_path: str) -> bool:
        """Restaura apenas as configurações do backup, sem afetar os dados do Anki"""
        try:
            if not os.path.exists(backup_path):
                showCritical("Arquivo de backup não encontrado.")
                return False

            if not mw or not mw.col:
                showCritical("Anki não está disponível para restauração.")
                return False

            # Confirmar operação
            if not askUser(
                "🔧 RECUPERAÇÃO DE CONFIGURAÇÕES\n\n"
                "Esta operação irá:\n\n"
                "• Restaurar todas as configurações do addon\n"
                "• Restaurar as informações de decks remotos\n"
                "• Recriar as ligações entre decks remotos e locais\n"
                "• NÃO alterar nenhum dado do Anki (notas, cards, etc.)\n\n"
                "Ideal para quando você reinstalou o addon e quer\n"
                "recuperar apenas as configurações.\n\n"
                "Deseja continuar?"
            ):
                return False

            # Criar diretório temporário para extração
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. Extrair backup
                self._extract_backup_zip(backup_path, temp_path)
                
                # 2. Validar backup
                backup_info = self._get_backup_info(temp_path)
                if not backup_info:
                    showCritical("Arquivo de backup inválido ou corrompido.")
                    return False
                
                # 3. Verificar se é um backup válido (completo ou só configurações)
                if backup_info.get("version") != self.backup_version:
                    showCritical("Versão do backup incompatível.")
                    return False
                
                # 4. Restaurar apenas configurações
                self._restore_configurations(temp_path)
                
                # 5. Recriar ligações entre decks remotos e locais
                self._recreate_deck_links()
                
            showInfo(
                "✅ Configurações restauradas com sucesso!\n\n"
                "• Configurações do addon foram restauradas\n"
                "• Decks remotos foram religados aos decks locais\n"
                "• Nenhum dado do Anki foi alterado\n\n"
                "Reinicie o Anki para garantir que todas as\n"
                "configurações sejam aplicadas corretamente."
            )
            return True
            
        except Exception as e:
            showCritical(f"Erro ao restaurar configurações: {str(e)}")
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

    def _save_backup_info(self, temp_path: Path, apkg_included: bool, config_only: bool = False) -> None:
        """Salva informações sobre o backup"""
        backup_info = {
            "version": self.backup_version,
            "created_at": datetime.now().isoformat(),
            "anki_version": getattr(mw, "version", "unknown") if mw else "unknown",
            "addon_version": "2.0",
            "apkg_included": apkg_included,
            "config_only": config_only,
            "deck_name": self.sheets2anki_deck_name,
            "contents": ["configurations"] if config_only else (["configurations", "deck_apkg"] if apkg_included else ["configurations"])
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
        backup_info = self._get_backup_info(temp_path)
        return backup_info is not None and backup_info.get("version") == self.backup_version

    def _get_backup_info(self, temp_path: Path) -> Optional[Dict[str, Any]]:
        """Obtém informações do backup"""
        backup_info_path = temp_path / "backup_info.json"
        if not backup_info_path.exists():
            return None
        
        try:
            with open(backup_info_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None

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
        """Importa o deck do arquivo .apkg usando API moderna do Anki"""
        try:
            if not mw or not mw.col:
                raise Exception("Anki não está disponível")
            
            # Método 1: Tentar usar AnkiPackageImporter (API moderna)
            try:
                from anki.importing.apkg import AnkiPackageImporter
                
                importer = AnkiPackageImporter(mw.col, apkg_path)
                importer.run()
                mw.col.save()
                
                print("Deck importado com sucesso (API moderna)")
                showInfo("✅ Deck importado com sucesso do backup!")
                return
                
            except Exception as e:
                print(f"Método moderno falhou: {e}")
            
            # Método 2: Tentar usar importação via interface (mais compatível)
            try:
                from aqt.importing import importFile
                
                # Usar a função de importação da interface
                importFile(mw, apkg_path)
                
                print("Deck importado com sucesso (método interface)")
                showInfo("✅ Deck importado com sucesso do backup!")
                return
                
            except Exception as e:
                print(f"Método interface falhou: {e}")
            
            # Método 3: Fallback para versões mais antigas
            try:
                from aqt.importing import doImport
                doImport(mw, apkg_path)
                
                print("Deck importado com sucesso (método legacy)")
                showInfo("✅ Deck importado com sucesso do backup!")
                return
                
            except Exception as e:
                print(f"Método legacy falhou: {e}")
            
            # Se todos os métodos falharam
            raise Exception("Todos os métodos de importação falharam")
            
        except Exception as e:
            print(f"Erro ao importar deck: {e}")
            showCritical(f"❌ Erro ao importar deck do backup:\n{e}\n\nTente importar manualmente o arquivo .apkg através do menu Arquivo > Importar do Anki.")

    def _import_deck_manual(self, apkg_path: str) -> None:
        """Método manual de importação como último recurso"""
        # Este método foi removido pois é muito complexo e arriscado
        # Em vez disso, orientamos o usuário a importar manualmente
        showInfo(
            "⚠️ Importação automática falhou.\n\n"
            "Para recuperar seus dados:\n"
            "1. Abra o Anki\n"
            "2. Vá em Arquivo > Importar\n"
            f"3. Selecione o arquivo: {apkg_path}\n"
            "4. Siga as instruções na tela\n\n"
            "Seus dados estão seguros no arquivo de backup!"
        )

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


    def create_auto_config_backup(self) -> bool:
        """
        Cria um backup automático de configurações durante a sincronização.
        
        Returns:
            bool: True se o backup foi criado com sucesso
        """
        try:
            # Verificar se backup automático está habilitado
            auto_config = get_auto_backup_config()
            if not auto_config.get("enabled", True):
                print("[AUTO_BACKUP] Backup automático desabilitado")
                return False
            
            # Obter diretório de backup
            backup_dir = get_auto_backup_directory()
            
            # Gerar nome do arquivo com timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"sheets2anki_auto_config_{timestamp}.zip"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Criar backup de configurações
            success = self.create_config_backup(backup_path)
            
            if success:
                print(f"[AUTO_BACKUP] ✅ Backup automático criado: {backup_path}")
                
                # Fazer rotação de arquivos (manter apenas os últimos N)
                self._rotate_auto_backup_files(backup_dir, auto_config.get("max_files", 50))
                
                return True
            else:
                print("[AUTO_BACKUP] ❌ Falha ao criar backup automático")
                return False
                
        except Exception as e:
            print(f"[AUTO_BACKUP] ❌ Erro ao criar backup automático: {e}")
            return False

    def _rotate_auto_backup_files(self, backup_dir: str, max_files: int) -> None:
        """
        Remove arquivos de backup antigos, mantendo apenas os mais recentes.
        
        Args:
            backup_dir (str): Diretório dos backups
            max_files (int): Número máximo de arquivos a manter
        """
        try:
            import glob
            
            # Encontrar todos os arquivos de backup automático
            pattern = os.path.join(backup_dir, "sheets2anki_auto_config_*.zip")
            backup_files = glob.glob(pattern)
            
            # Ordenar por data de modificação (mais recentes primeiro)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Remover arquivos excedentes
            files_to_remove = backup_files[max_files:]
            
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                    print(f"[AUTO_BACKUP] 🗑️ Removido backup antigo: {os.path.basename(file_path)}")
                except Exception as e:
                    print(f"[AUTO_BACKUP] ⚠️ Erro ao remover {file_path}: {e}")
            
            if files_to_remove:
                print(f"[AUTO_BACKUP] 📁 Rotação concluída: {len(files_to_remove)} arquivo(s) removido(s), {len(backup_files) - len(files_to_remove)} mantido(s)")
            
        except Exception as e:
            print(f"[AUTO_BACKUP] ❌ Erro na rotação de arquivos: {e}")

    def get_auto_backup_info(self) -> Dict[str, Any]:
        """
        Obtém informações sobre os backups automáticos.
        
        Returns:
            dict: Informações sobre backups automáticos
        """
        try:
            auto_config = get_auto_backup_config()
            backup_dir = get_auto_backup_directory()
            
            # Contar arquivos de backup existentes
            import glob
            pattern = os.path.join(backup_dir, "sheets2anki_auto_config_*.zip")
            backup_files = glob.glob(pattern)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Informações do backup mais recente
            latest_backup = None
            if backup_files:
                latest_file = backup_files[0]
                latest_backup = {
                    "filename": os.path.basename(latest_file),
                    "path": latest_file,
                    "size": os.path.getsize(latest_file),
                    "created": datetime.fromtimestamp(os.path.getmtime(latest_file)).isoformat()
                }
            
            return {
                "enabled": auto_config.get("enabled", True),
                "directory": backup_dir,
                "max_files": auto_config.get("max_files", 50),
                "total_files": len(backup_files),
                "latest_backup": latest_backup,
                "all_backups": [
                    {
                        "filename": os.path.basename(f),
                        "path": f,
                        "size": os.path.getsize(f),
                        "created": datetime.fromtimestamp(os.path.getmtime(f)).isoformat()
                    }
                    for f in backup_files[:10]  # Mostrar apenas os 10 mais recentes
                ]
            }
            
        except Exception as e:
            print(f"[AUTO_BACKUP] ❌ Erro ao obter informações: {e}")
            return {
                "enabled": False,
                "directory": "",
                "max_files": 50,
                "total_files": 0,
                "latest_backup": None,
                "all_backups": [],
                "error": str(e)
            }


# Manter compatibilidade com código antigo
BackupManager = SimplifiedBackupManager
