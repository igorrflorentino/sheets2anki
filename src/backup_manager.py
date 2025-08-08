#!/usr/bin/env python3
"""
Gerenciador de Backup para Sheets2Anki

Este módulo fornece funcionalidades para:
- Exportar con                if restore_options.get('configurations', True):
                    success &= self._restore_configurations(temp_dir)
                
                if restore_options.get('decks', True):
                    success &= self._restore_remote_decks(temp_dir)
                
                if restore_options.get('preferences', True):
                    success &= self._restore_user_preferences(temp_dir)
                
                if restore_options.get('media', True):
                    success &= self._restore_media_files(temp_dir)de decks remotos
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
                
                # 3. Backup das preferências do usuário (descontinuado)
                self._backup_user_preferences(temp_dir)
                
                # 4. Backup de mídia (opcional)
                if include_media:
                    self._backup_media_files(temp_dir)
                
                # 5. Criar arquivo de metadados do backup
                self._create_backup_metadata(temp_dir)
                
                # 6. Criar arquivo ZIP
                self._create_zip_backup(temp_dir, backup_path)
                
                print(f"✅ Backup criado com sucesso: {backup_path}")
                return True
                
            finally:
                # Limpar diretório temporário
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            print(f"❌ Erro ao criar backup: {e}")
            return False
    
    def restore_backup(self, backup_path: str, restore_options: Optional[Dict] = None) -> bool:
        """
        Restaura um backup das configurações
        
        Args:
            backup_path: Caminho para o arquivo de backup (.zip)
            restore_options: Opções de restauração
            
        Returns:
            bool: True se a restauração foi bem-sucedida
        """
        if restore_options is None:
            restore_options = {
                'configs': True,
                'decks': True,
                'preferences': True,
                'media': True,
                'overwrite': False
            }
        
        try:
            # Verificar se o arquivo existe
            if not os.path.exists(backup_path):
                print(f"❌ Arquivo de backup não encontrado: {backup_path}")
                return False
            
            # Criar diretório temporário para extração
            temp_dir = Path(backup_path).parent / f"sheets2anki_restore_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                # 1. Extrair arquivo ZIP
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 2. Verificar metadados do backup
                if not self._verify_backup_metadata(temp_dir):
                    print("❌ Backup inválido ou incompatível")
                    return False
                
                # 3. Criar backup das configurações atuais (por segurança)
                if not restore_options.get('overwrite', False):
                    self._create_safety_backup()
                
                # 4. Restaurar configurações
                success = True
                if restore_options.get('configs', True):
                    success &= self._restore_configurations(temp_dir)
                
                if restore_options.get('decks', True):
                    success &= self._restore_remote_decks(temp_dir)
                
                if restore_options.get('preferences', True):
                    success &= self._restore_user_preferences(temp_dir)
                
                if restore_options.get('media', True):
                    success &= self._restore_media_files(temp_dir)
                
                if success:
                    print(f"✅ Backup restaurado com sucesso: {backup_path}")
                    return True
                else:
                    print("⚠️  Algumas partes do backup não puderam ser restauradas")
                    return False
                    
            finally:
                # Limpar diretório temporário
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")
            return False
    
    def list_backup_info(self, backup_path: str) -> Optional[Dict]:
        """
        Lista informações sobre um backup
        
        Args:
            backup_path: Caminho para o arquivo de backup
            
        Returns:
            Dict com informações do backup ou None se erro
        """
        try:
            temp_dir = Path(backup_path).parent / f"sheets2anki_info_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            temp_dir.mkdir(exist_ok=True)
            
            try:
                with zipfile.ZipFile(backup_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                metadata_file = temp_dir / "backup_metadata.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    return None
                    
            finally:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            print(f"❌ Erro ao ler informações do backup: {e}")
            return None
    
    def export_decks_config(self, export_path: str, deck_urls: Optional[List[str]] = None) -> bool:
        """
        Exporta configurações específicas de decks
        
        Args:
            export_path: Caminho para o arquivo de exportação
            deck_urls: URLs específicas para exportar (None = todas)
            
        Returns:
            bool: True se exportação foi bem-sucedida
        """
        try:
            # Obter configurações atuais
            meta_data = get_meta()
            
            # Filtrar decks se especificado
            decks_to_export = {}
            if deck_urls:
                for url in deck_urls:
                    if url in meta_data.get('decks', {}):
                        decks_to_export[url] = meta_data['decks'][url]
            else:
                decks_to_export = meta_data.get('decks', {})
            
            # Criar estrutura de exportação
            export_data = {
                'version': self.backup_version,
                'export_date': datetime.now().isoformat(),
                'export_type': 'decks_config',
                'decks': decks_to_export,
                'deck_count': len(decks_to_export)
            }
            
            # Salvar arquivo
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configurações de {len(decks_to_export)} deck(s) exportadas para: {export_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao exportar configurações de decks: {e}")
            return False
    
    def import_decks_config(self, import_path: str, merge_mode: str = 'ask') -> bool:
        """
        Importa configurações de decks
        
        Args:
            import_path: Caminho para o arquivo de importação
            merge_mode: 'overwrite', 'skip', 'ask'
            
        Returns:
            bool: True se importação foi bem-sucedida
        """
        try:
            # Verificar se arquivo existe
            if not os.path.exists(import_path):
                print(f"❌ Arquivo de importação não encontrado: {import_path}")
                return False
            
            # Carregar dados de importação
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Verificar versão e tipo
            if import_data.get('export_type') != 'decks_config':
                print("❌ Arquivo não é uma exportação de configurações de decks")
                return False
            
            # Obter configurações atuais
            meta_data = get_meta()
            current_decks = meta_data.get('decks', {})
            
            # Processar cada deck importado
            decks_to_import = import_data.get('decks', {})
            conflicts = []
            
            for url, deck_config in decks_to_import.items():
                if url in current_decks:
                    conflicts.append(url)
            
            # Lidar com conflitos
            if conflicts and merge_mode == 'ask':
                print(f"⚠️  {len(conflicts)} deck(s) já existem:")
                for url in conflicts:
                    print(f"   - {url}")
                
                response = input("Deseja sobrescrever? (s/n): ").lower()
                if response != 's':
                    print("❌ Importação cancelada pelo usuário")
                    return False
                merge_mode = 'overwrite'
            
            # Importar decks
            imported_count = 0
            for url, deck_config in decks_to_import.items():
                if url in current_decks and merge_mode == 'skip':
                    print(f"⏭️  Pulando deck existente: {url}")
                    continue
                
                # Atualizar configuração
                current_decks[url] = deck_config
                imported_count += 1
                print(f"✅ Importado: {deck_config.get('name', url)}")
            
            # Salvar configurações atualizadas
            meta_data['decks'] = current_decks
            
            # Importar preferências do usuário (se existirem)
            if 'user_preferences' in import_data:
                user_prefs = import_data['user_preferences']
                if user_prefs:
                    meta_data['user_preferences'] = {**meta_data.get('user_preferences', {}), **user_prefs}
            
            # Salvar alterações
            save_meta(meta_data)
            
            print(f"✅ {imported_count} deck(s) importado(s) com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao importar configurações de decks: {e}")
            return False
    
    def _backup_configurations(self, temp_dir: Path) -> None:
        """Faz backup das configurações principais"""
        config_dir = temp_dir / "configs"
        config_dir.mkdir(exist_ok=True)
        
        # Backup do meta.json
        meta_file = Path(__file__).parent.parent / "meta.json"
        if meta_file.exists():
            shutil.copy2(meta_file, config_dir / "meta.json")
        
        # Backup do config.json
        config_file = Path(__file__).parent.parent / "config.json"
        if config_file.exists():
            shutil.copy2(config_file, config_dir / "config.json")
    
    def _backup_remote_decks(self, temp_dir: Path) -> None:
        """Faz backup específico dos decks remotos"""
        meta_data = get_meta()
        decks_data = meta_data.get('decks', {})
        
        decks_dir = temp_dir / "decks"
        decks_dir.mkdir(exist_ok=True)
        
        # Salvar configurações de cada deck
        for url, deck_config in decks_data.items():
            # Criar nome de arquivo seguro
            safe_name = "".join(c for c in deck_config.get('deck_name', 'unnamed') if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            deck_file = decks_dir / f"{safe_name}_{hash(url) % 10000}.json"
            
            deck_backup = {
                'url': url,
                'config': deck_config,
                'backup_date': datetime.now().isoformat()
            }
            
            with open(deck_file, 'w', encoding='utf-8') as f:
                json.dump(deck_backup, f, indent=2, ensure_ascii=False)
    
    def _backup_user_preferences(self, temp_dir: Path) -> None:
        """Faz backup das preferências do usuário (funcionalidade removida - sempre automático)"""
        # As preferências do usuário foram removidas - comportamento sempre automático
        pass
    
    def _backup_media_files(self, temp_dir: Path) -> None:
        """Faz backup de arquivos de mídia (se existirem)"""
        media_dir = temp_dir / "media"
        media_dir.mkdir(exist_ok=True)
        
        # Placeholder para backup de mídia
        # Implementar se necessário no futuro
        pass
    
    def _create_backup_metadata(self, temp_dir: Path) -> None:
        """Cria arquivo de metadados do backup"""
        meta_data = get_meta()
        
        metadata = {
            'backup_version': self.backup_version,
            'creation_date': datetime.now().isoformat(),
            'anki_version': "25.x",
            'sheets2anki_version': "3.0",
            'total_decks': len(meta_data.get('decks', {})),
            'has_media': False,  # Atualizar se implementar backup de mídia
            'contents': [
                'configurations',
                'decks',
                'user_preferences'
            ]
        }
        
        metadata_file = temp_dir / "backup_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def _create_zip_backup(self, temp_dir: Path, backup_path: str) -> None:
        """Cria arquivo ZIP com o backup"""
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    # Usar caminho relativo no ZIP
                    arcname = file_path.relative_to(temp_dir)
                    zip_file.write(file_path, arcname)
    
    def _verify_backup_metadata(self, temp_dir: Path) -> bool:
        """Verifica se o backup é válido"""
        metadata_file = temp_dir / "backup_metadata.json"
        if not metadata_file.exists():
            return False
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verificar versão compatível
            version = metadata.get('backup_version', '0.0')
            if version != self.backup_version:
                print(f"⚠️  Versão do backup ({version}) pode ser incompatível com a atual ({self.backup_version})")
            
            return True
            
        except Exception:
            return False
    
    def _create_safety_backup(self) -> None:
        """Cria backup de segurança antes de restaurar"""
        safety_dir = Path.home() / ".sheets2anki_safety_backups"
        safety_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safety_path = safety_dir / f"safety_backup_{timestamp}.zip"
        
        self.create_backup(str(safety_path))
        print(f"🛡️  Backup de segurança criado: {safety_path}")
    
    def _restore_configurations(self, temp_dir: Path) -> bool:
        """Restaura configurações principais"""
        try:
            config_dir = temp_dir / "configs"
            if not config_dir.exists():
                return True  # Não há configurações para restaurar
            
            # Restaurar meta.json
            meta_file = config_dir / "meta.json"
            if meta_file.exists():
                target_meta = Path(__file__).parent.parent / "meta.json"
                shutil.copy2(meta_file, target_meta)
            
            # Restaurar config.json
            config_file = config_dir / "config.json"
            if config_file.exists():
                target_config = Path(__file__).parent.parent / "config.json"
                shutil.copy2(config_file, target_config)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar configurações: {e}")
            return False
    
    def _restore_remote_decks(self, temp_dir: Path) -> bool:
        """Restaura configurações de decks remotos"""
        try:
            decks_dir = temp_dir / "decks"
            if not decks_dir.exists():
                return True  # Não há decks para restaurar
            
            # Carregar configurações atuais
            meta_data = get_meta()
            current_decks = meta_data.get('decks', {})
            
            # Restaurar cada deck
            for deck_file in decks_dir.glob('*.json'):
                with open(deck_file, 'r', encoding='utf-8') as f:
                    deck_backup = json.load(f)
                
                url = deck_backup['url']
                config = deck_backup['config']
                
                current_decks[url] = config
                print(f"✅ Deck restaurado: {config.get('name', url)}")
            
            # Salvar configurações atualizadas
            meta_data['decks'] = current_decks
            save_meta(meta_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar decks remotos: {e}")
            return False
    
    def _restore_user_preferences(self, temp_dir: Path) -> bool:
        """Restaura preferências do usuário (funcionalidade removida - sempre automático)"""
        # As preferências do usuário foram removidas - comportamento sempre automático
        return True
    
    def _restore_media_files(self, temp_dir: Path) -> bool:
        """Restaura arquivos de mídia"""
        try:
            media_dir = temp_dir / "media"
            if not media_dir.exists():
                return True  # Não há mídia para restaurar
            
            # Placeholder para restauração de mídia
            # Implementar se necessário no futuro
            return True
            
        except Exception as e:
            print(f"❌ Erro ao restaurar mídia: {e}")
            return False
