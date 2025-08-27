#!/usr/bin/env python3
"""
Script de diagnóstico atualizado para verificar as correções no sistema de backup
"""

import os
import sys

def check_import_fix():
    """Verifica se o import em backup_dialog.py foi corrigido"""
    try:
        with open("src/backup_dialog.py", "r") as f:
            content = f.read()
            
        has_bad_import = "from .backup_manager import BackupManager" in content
        has_good_import = "from .backup_system import BackupManager" in content
        
        if has_bad_import:
            return False, "❌ backup_dialog.py ainda importa backup_manager inexistente"
        elif has_good_import:
            return True, "✅ backup_dialog.py importa corretamente de backup_system"
        else:
            return False, "❌ backup_dialog.py não tem import do BackupManager"
            
    except FileNotFoundError:
        return False, "❌ Arquivo backup_dialog.py não encontrado"

def check_sync_integration():
    """Verifica se o backup automático foi implementado em sync.py"""
    try:
        with open("src/sync.py", "r") as f:
            content = f.read()
            
        has_backup_check = "backup_before_sync" in content
        has_backup_manager_import = "from .backup_system import BackupManager" in content
        has_backup_creation = "backup_manager.create_backup" in content
        
        if has_backup_check and has_backup_manager_import and has_backup_creation:
            return True, "✅ Backup automático implementado em sync.py"
        elif has_backup_check:
            return False, "⚠️ Verificação de config existe mas implementação incompleta"
        else:
            return False, "❌ Backup automático não implementado em sync.py"
            
    except FileNotFoundError:
        return False, "❌ Arquivo sync.py não encontrado"

def check_config_status():
    """Verifica status da configuração backup_before_sync"""
    try:
        with open("config.json", "r") as f:
            import json
            config = json.load(f)
            
        backup_enabled = config.get("backup_before_sync", False)
        return backup_enabled, f"{'✅' if backup_enabled else 'ℹ️'} backup_before_sync: {backup_enabled}"
        
    except (FileNotFoundError, json.JSONDecodeError):
        return False, "❌ Erro ao ler config.json"

def main():
    print("🔍 VERIFICAÇÃO DE CORREÇÕES: Sistema de Backup")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("src/backup_system.py"):
        print("❌ Execute este script na raiz do projeto sheets2anki")
        sys.exit(1)
    
    print("\n📋 VERIFICANDO CORREÇÕES IMPLEMENTADAS:")
    
    # 1. Verificar correção do import
    import_ok, import_msg = check_import_fix()
    print(f"\n1. Correção de Import:")
    print(f"   {import_msg}")
    
    # 2. Verificar implementação do backup automático
    sync_ok, sync_msg = check_sync_integration()
    print(f"\n2. Backup Automático:")
    print(f"   {sync_msg}")
    
    # 3. Verificar configuração
    config_enabled, config_msg = check_config_status()
    print(f"\n3. Configuração:")
    print(f"   {config_msg}")
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DAS CORREÇÕES:")
    
    if import_ok and sync_ok:
        print("✅ PROBLEMAS CRÍTICOS CORRIGIDOS!")
        print("   - Import do BackupManager corrigido")
        print("   - Backup automático implementado")
        print("")
        if config_enabled:
            print("✅ Sistema pronto para usar!")
            print("   - Backup automático ativado")
        else:
            print("ℹ️ Para ativar o backup automático:")
            print("   - Configure backup_before_sync=true no config.json")
    else:
        print("⚠️ AINDA HÁ PROBLEMAS:")
        if not import_ok:
            print("   - Import do BackupManager precisa ser corrigido")
        if not sync_ok:
            print("   - Backup automático não implementado")
    
    print("\n🧪 PRÓXIMOS PASSOS PARA TESTE:")
    print("   1. Testar interface de backup manual")
    print("   2. Testar backup automático durante sync")
    print("   3. Testar restauração de backup")

if __name__ == "__main__":
    main()
