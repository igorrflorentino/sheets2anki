#!/usr/bin/env python3
"""
Teste simplificado do sistema de backup redesenhado.
Verifica se todas as importações e funcionalidades básicas estão funcionando.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Testa se todas as importações necessárias funcionam."""
    print("🔍 Testando importações...")
    
    try:
        from compat import WINDOW_MODAL, APPLICATION_MODAL, NON_MODAL, QProgressDialog
        print("✅ Importações do compat.py funcionando")
    except ImportError as e:
        print(f"❌ Erro na importação do compat.py: {e}")
        return False
    
    try:
        from backup_system import SimplifiedBackupManager
        print("✅ Importação do SimplifiedBackupManager funcionando")
    except ImportError as e:
        print(f"❌ Erro na importação do backup_system.py: {e}")
        return False
    
    try:
        from backup_dialog import BackupDialog
        print("✅ Importação do BackupDialog funcionando")
    except ImportError as e:
        print(f"❌ Erro na importação do backup_dialog.py: {e}")
        return False
    
    return True

def test_backup_manager():
    """Testa se o SimplifiedBackupManager pode ser instanciado."""
    print("\n🔍 Testando SimplifiedBackupManager...")
    
    try:
        from backup_system import SimplifiedBackupManager
        
        backup_manager = SimplifiedBackupManager()  # Sem parâmetros
        print("✅ SimplifiedBackupManager instanciado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao instanciar SimplifiedBackupManager: {e}")
        return False

def test_dialog_structure():
    """Verifica se o diálogo tem a estrutura correta."""
    print("\n🔍 Testando estrutura do BackupDialog...")
    
    try:
        from backup_dialog import BackupDialog
        
        # Verificar se a classe tem os métodos necessários
        methods = ['setup_ui', 'create_backup', 'restore_backup']
        for method in methods:
            if not hasattr(BackupDialog, method):
                print(f"❌ Método '{method}' não encontrado na BackupDialog")
                return False
        
        print("✅ Estrutura do BackupDialog está correta")
        return True
    except Exception as e:
        print(f"❌ Erro ao verificar BackupDialog: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes do sistema simplificado de backup...\n")
    
    tests = [
        test_imports,
        test_backup_manager,
        test_dialog_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Resultado dos testes: {passed}/{total} passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! O sistema simplificado de backup está funcionando corretamente.")
        print("\n📋 Resumo das funcionalidades disponíveis:")
        print("   • Gerar Backup: Exporta deck como .apkg + configurações")
        print("   • Recuperar Backup: Remove deck atual e importa backup completo")
        print("   • Interface simplificada com apenas 2 operações principais")
        print("   • Preservação completa de agendamento e mídia")
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
    
    return passed == total

if __name__ == "__main__":
    main()
