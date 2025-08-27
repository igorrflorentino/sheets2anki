#!/usr/bin/env python3
"""
Teste para verificar se as importações estão corretas no contexto do plugin.
Simula o ambiente de carregamento do Anki.
"""

import sys
import os

def test_plugin_imports():
    """Testa se as importações do plugin estão corretas."""
    print("🔍 Testando importações do plugin...")
    
    # Simular estrutura do Anki
    plugin_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, plugin_dir)
    
    try:
        # Testar importação direta do backup_dialog
        from src.backup_dialog import show_backup_dialog
        print("✅ show_backup_dialog importado diretamente do backup_dialog")
        
        # Verificar se a função existe e é callable
        if callable(show_backup_dialog):
            print("✅ show_backup_dialog é uma função válida")
        else:
            print("❌ show_backup_dialog não é uma função")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_backup_system_content():
    """Verifica se backup_system.py não tem mais show_backup_dialog."""
    print("\n🔍 Verificando conteúdo do backup_system.py...")
    
    try:
        with open('src/backup_system.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def show_backup_dialog' in content:
            print("❌ backup_system.py ainda contém show_backup_dialog")
            return False
        else:
            print("✅ backup_system.py não contém show_backup_dialog")
        
        # Verificar se tem SimplifiedBackupManager
        if 'class SimplifiedBackupManager' in content:
            print("✅ SimplifiedBackupManager presente no backup_system.py")
        else:
            print("❌ SimplifiedBackupManager não encontrado")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar backup_system.py: {e}")
        return False

def test_backup_dialog_content():
    """Verifica se backup_dialog.py tem show_backup_dialog."""
    print("\n🔍 Verificando conteúdo do backup_dialog.py...")
    
    try:
        with open('src/backup_dialog.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'def show_backup_dialog' in content:
            print("✅ backup_dialog.py contém show_backup_dialog")
        else:
            print("❌ backup_dialog.py não contém show_backup_dialog")
            return False
        
        # Verificar se tem BackupDialog
        if 'class BackupDialog' in content:
            print("✅ BackupDialog presente no backup_dialog.py")
        else:
            print("❌ BackupDialog não encontrado")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar backup_dialog.py: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🧪 TESTE DE IMPORTAÇÕES - Correção do Erro show_backup_dialog\n")
    
    tests = [
        ("Importações do Plugin", test_plugin_imports),
        ("Conteúdo backup_system.py", test_backup_system_content),
        ("Conteúdo backup_dialog.py", test_backup_dialog_content),
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
    print(f"📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 CORREÇÃO COMPLETA! Importações estão corretas!")
        print("\n📋 Resumo da correção:")
        print("   ✅ show_backup_dialog movido para backup_dialog.py")
        print("   ✅ Importação corrigida no __init__.py principal")
        print("   ✅ backup_system.py limpo (apenas SimplifiedBackupManager)")
        print("   ✅ Estrutura de arquivos organizada")
    else:
        print("⚠️  Alguns problemas ainda precisam ser corrigidos.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
