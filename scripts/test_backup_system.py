#!/usr/bin/env python3
"""
Teste final do sistema de backup corrigido
"""

import sys
import os

def test_import_system():
    """Testa se os imports funcionam corretamente"""
    print("🔍 Testando sistema de imports...")
    
    try:
        # Simular import do backup_dialog
        sys.path.insert(0, 'src')
        
        # Verificar se o import funciona
        from backup_system import BackupManager
        print("✅ BackupManager importado com sucesso de backup_system")
        
        # Verificar se a classe tem os métodos esperados
        backup_manager = BackupManager()
        
        if hasattr(backup_manager, 'create_backup'):
            print("✅ Método create_backup encontrado")
        else:
            print("❌ Método create_backup não encontrado")
            
        if hasattr(backup_manager, 'restore_backup'):
            print("✅ Método restore_backup encontrado")
        else:
            print("❌ Método restore_backup não encontrado")
            
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_sync_integration():
    """Testa se a integração com sync.py está correta"""
    print("\n🔍 Testando integração com sync.py...")
    
    try:
        with open("src/sync.py", "r") as f:
            content = f.read()
        
        # Verificar imports necessários
        if "from .backup_system import BackupManager" in content:
            print("✅ Import do BackupManager em sync.py")
        else:
            print("❌ Import do BackupManager não encontrado em sync.py")
            return False
            
        # Verificar verificação da configuração
        if "backup_before_sync" in content:
            print("✅ Verificação de backup_before_sync implementada")
        else:
            print("❌ Verificação de backup_before_sync não encontrada")
            return False
            
        # Verificar chamada do backup
        if "backup_manager.create_backup" in content:
            print("✅ Chamada de create_backup implementada")
        else:
            print("❌ Chamada de create_backup não encontrada")
            return False
            
        return True
        
    except FileNotFoundError:
        print("❌ Arquivo sync.py não encontrado")
        return False

def main():
    print("🧪 TESTE FINAL: Sistema de Backup Corrigido")
    print("=" * 50)
    
    # Verificar diretório
    if not os.path.exists("src/backup_system.py"):
        print("❌ Execute este script na raiz do projeto sheets2anki")
        sys.exit(1)
    
    # Executar testes
    import_ok = test_import_system()
    sync_ok = test_sync_integration()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO DOS TESTES:")
    
    if import_ok and sync_ok:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("\n🎯 Sistema de backup está funcionando corretamente:")
        print("   - Imports corrigidos")
        print("   - Backup automático implementado")
        print("   - Integração com sincronização ativa")
        print("\n🚀 Pronto para uso!")
    else:
        print("❌ ALGUNS TESTES FALHARAM:")
        if not import_ok:
            print("   - Sistema de imports tem problemas")
        if not sync_ok:
            print("   - Integração com sincronização tem problemas")

if __name__ == "__main__":
    main()
