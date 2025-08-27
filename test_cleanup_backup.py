#!/usr/bin/env python3
"""
Teste final após limpeza do código legado.
Verifica se o sistema simplificado está funcionando sem código desnecessário.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_clean_imports():
    """Testa se todas as importações estão limpas."""
    print("🧹 Testando importações limpas...")
    
    try:
        from backup_system import SimplifiedBackupManager
        print("✅ SimplifiedBackupManager importado")
        
        from backup_dialog import BackupDialog, show_backup_dialog
        print("✅ BackupDialog e show_backup_dialog importados")
        
        # Verificar se não há mais referências ao backup automático
        with open('src/sync.py', 'r', encoding='utf-8') as f:
            sync_content = f.read()
        if 'backup_before_sync' in sync_content:
            print("❌ Ainda há referência ao backup_before_sync no sync.py")
            return False
        else:
            print("✅ Referências ao backup_before_sync removidas do sync.py")
        
        return True
    except Exception as e:
        print(f"❌ Erro nas importações: {e}")
        return False

def test_config_files():
    """Verifica se os arquivos de configuração estão limpos."""
    print("\n🧹 Testando arquivos de configuração...")
    
    try:
        import json
        
        # Verificar config.json
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        if 'backup_before_sync' in config:
            print("❌ backup_before_sync ainda presente em config.json")
            return False
        else:
            print("✅ backup_before_sync removido de config.json")
        
        # Verificar meta.json
        with open('meta.json', 'r') as f:
            meta = json.load(f)
        
        if 'backup_before_sync' in meta.get('config', {}):
            print("❌ backup_before_sync ainda presente em meta.json")
            return False
        else:
            print("✅ backup_before_sync removido de meta.json")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar configurações: {e}")
        return False

def test_legacy_files():
    """Verifica se arquivos legados foram removidos."""
    print("\n🧹 Testando remoção de arquivos legados...")
    
    legacy_files = [
        'src/backup_system_backup.py',
        'src/backup_system_simple.py',
        'src/backup_system_new.py',
        'src/backup_dialog_backup.py',
        'src/backup_dialog_simple.py'
    ]
    
    removed_count = 0
    for legacy_file in legacy_files:
        if not os.path.exists(legacy_file):
            removed_count += 1
    
    if removed_count == len(legacy_files):
        print(f"✅ Todos os {len(legacy_files)} arquivos legados foram removidos")
        return True
    else:
        print(f"❌ {len(legacy_files) - removed_count} arquivos legados ainda existem")
        return False

def test_simplified_functionality():
    """Testa se a funcionalidade simplificada está funcionando."""
    print("\n🧹 Testando funcionalidade simplificada...")
    
    try:
        from backup_system import SimplifiedBackupManager
        from backup_dialog import BackupDialog
        
        # Instanciar manager
        manager = SimplifiedBackupManager()
        
        # Verificar métodos essenciais
        essential_methods = ['create_backup', 'restore_backup']
        for method in essential_methods:
            if not hasattr(manager, method):
                print(f"❌ Método essencial {method} não encontrado")
                return False
        
        print("✅ Funcionalidade simplificada verificada")
        return True
    except Exception as e:
        print(f"❌ Erro na funcionalidade: {e}")
        return False

def main():
    """Executa todos os testes de limpeza."""
    print("🧹 TESTE DE LIMPEZA - Sistema Simplificado de Backup\n")
    
    tests = [
        ("Importações Limpas", test_clean_imports),
        ("Arquivos de Configuração", test_config_files),
        ("Arquivos Legados Removidos", test_legacy_files),
        ("Funcionalidade Simplificada", test_simplified_functionality),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 {test_name}")
        print("-" * 50)
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSOU\n")
        else:
            print(f"❌ {test_name} - FALHOU\n")
    
    print("=" * 60)
    print(f"📊 RESULTADO DA LIMPEZA: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 LIMPEZA COMPLETA! Sistema totalmente simplificado!")
        print("\n🎯 RESUMO DA LIMPEZA:")
        print("   ✅ Código legado removido")
        print("   ✅ Funcionalidade backup_before_sync removida")
        print("   ✅ Arquivos duplicados eliminados")
        print("   ✅ Configurações desnecessárias removidas")
        print("   ✅ Sistema mantém apenas funcionalidades essenciais")
        print("\n🚀 Sistema pronto com versão ultra-simplificada!")
    else:
        print("⚠️  Limpeza parcial. Verifique os problemas acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
