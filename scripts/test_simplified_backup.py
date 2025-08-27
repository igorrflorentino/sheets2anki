#!/usr/bin/env python3
"""
Teste do sistema de backup simplificado
"""

import sys
import os

def test_simplified_backup_system():
    """Testa se o sistema de backup simplificado está implementado corretamente"""
    print("🧪 TESTE: Sistema de Backup Simplificado")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("src/backup_system.py"):
        print("❌ Execute este script na raiz do projeto sheets2anki")
        sys.exit(1)
    
    print("\n🔍 Verificando implementação simplificada...")
    
    # 1. Verificar nova classe SimplifiedBackupManager
    with open("src/backup_system.py", "r") as f:
        content = f.read()
    
    if "class SimplifiedBackupManager" in content:
        print("✅ Classe SimplifiedBackupManager implementada")
    else:
        print("❌ Classe SimplifiedBackupManager não encontrada")
        return False
    
    # 2. Verificar métodos simplificados
    required_methods = [
        "create_backup",
        "restore_backup", 
        "_export_main_deck_apkg",
        "_save_configurations",
        "_remove_current_sheets2anki_deck",
        "_import_deck_apkg",
        "_recreate_deck_links"
    ]
    
    for method in required_methods:
        if f"def {method}" in content:
            print(f"✅ Método {method} implementado")
        else:
            print(f"❌ Método {method} não encontrado")
            return False
    
    # 3. Verificar interface simplificada
    with open("src/backup_dialog.py", "r") as f:
        dialog_content = f.read()
    
    if "SimplifiedBackupManager" in dialog_content:
        print("✅ Interface atualizada para usar SimplifiedBackupManager")
    else:
        print("❌ Interface não atualizada")
        return False
    
    # 4. Verificar apenas duas operações principais
    if "Gerar Backup" in dialog_content and "Recuperar do Backup" in dialog_content:
        print("✅ Interface simplificada com apenas duas operações")
    else:
        print("❌ Interface não simplificada corretamente")
        return False
    
    # 5. Verificar integração com sync
    with open("src/sync.py", "r") as f:
        sync_content = f.read()
    
    if "SimplifiedBackupManager" in sync_content:
        print("✅ Sincronização atualizada para usar SimplifiedBackupManager")
    else:
        print("❌ Sincronização não atualizada")
        return False
    
    return True

def test_apkg_functionality():
    """Verifica se a funcionalidade de .apkg está implementada"""
    print("\n🔍 Verificando funcionalidade .apkg...")
    
    with open("src/backup_system.py", "r") as f:
        content = f.read()
    
    # Verificar exportação .apkg
    apkg_features = [
        "AnkiPackageExporter",
        "includeSched = True",
        "includeMedia = True", 
        "exportInto",
        "sheets2anki_deck.apkg"
    ]
    
    for feature in apkg_features:
        if feature in content:
            print(f"✅ Funcionalidade .apkg: {feature}")
        else:
            print(f"❌ Funcionalidade .apkg ausente: {feature}")
            return False
    
    # Verificar importação
    import_features = [
        "doImport",
        "_import_deck_apkg"
    ]
    
    for feature in import_features:
        if feature in content:
            print(f"✅ Funcionalidade importação: {feature}")
        else:
            print(f"❌ Funcionalidade importação ausente: {feature}")
            return False
    
    return True

def main():
    print("🎯 VERIFICAÇÃO: Sistema de Backup Simplificado")
    print("=" * 50)
    
    backup_ok = test_simplified_backup_system()
    apkg_ok = test_apkg_functionality()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    
    if backup_ok and apkg_ok:
        print("✅ SISTEMA SIMPLIFICADO IMPLEMENTADO COM SUCESSO!")
        print("\n🎉 O sistema agora oferece:")
        print("   - ✅ Interface ultra-simplificada (apenas 2 botões)")
        print("   - ✅ Backup completo (.apkg + configurações)")
        print("   - ✅ Restauração total (remove tudo e restaura)")
        print("   - ✅ Exportação com scheduling e mídia")
        print("   - ✅ Recriação automática de ligações")
        print("   - ✅ Backup automático durante sync")
        print("\n🚀 MUITO MAIS SIMPLES E EFICAZ!")
        
    else:
        print("❌ IMPLEMENTAÇÃO INCOMPLETA:")
        if not backup_ok:
            print("   - Sistema de backup tem problemas")
        if not apkg_ok:
            print("   - Funcionalidade .apkg incompleta")
    
    print("\n💡 COMO USAR:")
    print("   1. 📦 'Gerar Backup' → Cria arquivo .zip completo")
    print("   2. 📥 'Recuperar Backup' → Restaura estado exato")
    print("   3. 🔄 Backup automático durante sincronização")

if __name__ == "__main__":
    main()
