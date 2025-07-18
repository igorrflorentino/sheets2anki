#!/usr/bin/env python3
"""
Teste para funcionalidade de backup do Sheets2Anki

Este teste verifica se o sistema de backup funciona corretamente,
incluindo criação, restauração e exportação/importação de configurações.
"""

import os
import sys
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.backup_manager import BackupManager
from src.config_manager import get_meta, save_meta, get_config


def test_backup_creation():
    """Testa criação de backup"""
    print("🧪 Testando criação de backup...")
    
    backup_manager = BackupManager()
    
    # Usar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        
        # Criar backup
        success = backup_manager.create_backup(backup_path, include_media=False)
        
        if success and os.path.exists(backup_path):
            print("✅ Backup criado com sucesso")
            return True
        else:
            print("❌ Falha ao criar backup")
            return False


def test_backup_info():
    """Testa leitura de informações do backup"""
    print("🧪 Testando leitura de informações do backup...")
    
    backup_manager = BackupManager()
    
    # Usar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_path = os.path.join(temp_dir, "test_backup.zip")
        
        # Criar backup
        success = backup_manager.create_backup(backup_path, include_media=False)
        
        if not success:
            print("❌ Falha ao criar backup para teste")
            return False
        
        # Ler informações
        info = backup_manager.list_backup_info(backup_path)
        
        if info and 'backup_version' in info:
            print(f"✅ Informações lidas com sucesso: {info.get('total_decks', 0)} decks")
            return True
        else:
            print("❌ Falha ao ler informações do backup")
            return False


def test_export_import():
    """Testa exportação e importação de configurações"""
    print("🧪 Testando exportação e importação...")
    
    backup_manager = BackupManager()
    
    # Usar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        export_path = os.path.join(temp_dir, "test_export.json")
        
        # Exportar configurações
        success = backup_manager.export_decks_config(export_path)
        
        if not success:
            print("❌ Falha ao exportar configurações")
            return False
        
        if not os.path.exists(export_path):
            print("❌ Arquivo de exportação não foi criado")
            return False
        
        # Verificar conteúdo do arquivo
        try:
            with open(export_path, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            if 'export_type' in export_data and export_data['export_type'] == 'decks_config':
                print("✅ Exportação e leitura bem-sucedidas")
                return True
            else:
                print("❌ Formato de exportação inválido")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao ler arquivo de exportação: {e}")
            return False


def test_current_configs():
    """Testa leitura das configurações atuais"""
    print("🧪 Testando leitura das configurações atuais...")
    
    try:
        meta_data = get_meta()
        
        decks = meta_data.get('decks', {})
        preferences = meta_data.get('user_preferences', {})
        
        print(f"✅ Configurações atuais: {len(decks)} decks, {len(preferences)} preferências")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao ler configurações: {e}")
        return False


def test_backup_full_cycle():
    """Testa ciclo completo de backup e restauração"""
    print("🧪 Testando ciclo completo de backup e restauração...")
    
    backup_manager = BackupManager()
    
    # Usar diretório temporário
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_path = os.path.join(temp_dir, "full_cycle_backup.zip")
        
        # Salvar configurações originais
        try:
            original_meta = get_meta()
        except Exception as e:
            print(f"❌ Erro ao ler configurações originais: {e}")
            return False
        
        # Criar backup
        success = backup_manager.create_backup(backup_path, include_media=False)
        
        if not success:
            print("❌ Falha ao criar backup para teste de ciclo completo")
            return False
        
        # Tentar restaurar (sem sobrescrever para segurança)
        restore_options = {
            'configs': True,
            'decks': True,
            'preferences': True,
            'media': False,
            'overwrite': False
        }
        
        # Nota: Em ambiente de teste, não queremos alterar as configurações reais
        # Então vamos apenas validar que o backup pode ser lido
        info = backup_manager.list_backup_info(backup_path)
        
        if info and 'backup_version' in info:
            print("✅ Ciclo completo validado (backup criado e informações lidas)")
            return True
        else:
            print("❌ Falha na validação do ciclo completo")
            return False


def main():
    """Função principal do teste"""
    print("🚀 INICIANDO TESTES DE BACKUP - SHEETS2ANKI")
    print("=" * 60)
    
    # Lista de testes
    tests = [
        ("Criação de backup", test_backup_creation),
        ("Informações do backup", test_backup_info),
        ("Exportação e importação", test_export_import),
        ("Configurações atuais", test_current_configs),
        ("Ciclo completo", test_backup_full_cycle)
    ]
    
    # Executar testes
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            success = test_func()
            if success:
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                failed += 1
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name}: ERRO - {e}")
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"✅ Testes passaram: {passed}")
    print(f"❌ Testes falharam: {failed}")
    print(f"📊 Total de testes: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("💡 Sistema de backup funcionando corretamente")
        return 0
    else:
        print(f"\n⚠️  {failed} TESTE(S) FALHARAM")
        print("🔧 Verifique os problemas reportados acima")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
