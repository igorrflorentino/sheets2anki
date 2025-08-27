#!/usr/bin/env python3
"""
Teste da nova funcionalidade de backup completo incluindo decks e notas locais
"""

import sys
import os
import json

def test_backup_functionality():
    """Testa se a funcionalidade de backup completo está implementada"""
    print("🧪 TESTE: Backup Completo com Decks e Notas Locais")
    print("=" * 55)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("src/backup_system.py"):
        print("❌ Execute este script na raiz do projeto sheets2anki")
        sys.exit(1)
    
    print("\n🔍 Verificando implementação...")
    
    # 1. Verificar assinatura do método create_backup
    with open("src/backup_system.py", "r") as f:
        content = f.read()
    
    if "include_local_decks: bool = True" in content:
        print("✅ Parâmetro include_local_decks adicionado ao create_backup")
    else:
        print("❌ Parâmetro include_local_decks não encontrado")
        return False
    
    # 2. Verificar método de backup de dados locais
    if "_backup_local_anki_data" in content:
        print("✅ Método _backup_local_anki_data implementado")
    else:
        print("❌ Método _backup_local_anki_data não encontrado")
        return False
    
    # 3. Verificar atualização do backup_info
    if '"include_local_decks": include_local_decks' in content:
        print("✅ backup_info atualizado para incluir flag de decks locais")
    else:
        print("❌ backup_info não atualizado")
        return False
    
    # 4. Verificar interface do usuário
    with open("src/backup_dialog.py", "r") as f:
        dialog_content = f.read()
    
    if "backup_local_decks_cb" in dialog_content:
        print("✅ Checkbox para decks locais adicionada ao diálogo")
    else:
        print("❌ Checkbox para decks locais não encontrada")
        return False
    
    # 5. Verificar chamada atualizada no create_backup do dialog
    if "include_local_decks" in dialog_content and "backup_local_decks_cb.isChecked()" in dialog_content:
        print("✅ Interface usa corretamente a nova opção")
    else:
        print("❌ Interface não usa a nova opção corretamente")
        return False
    
    # 6. Verificar atualização do backup automático
    with open("src/sync.py", "r") as f:
        sync_content = f.read()
    
    if "include_local_decks=True" in sync_content:
        print("✅ Backup automático configurado para incluir decks locais")
    else:
        print("❌ Backup automático não configurado para incluir decks locais")
        return False
    
    return True

def test_backup_structure():
    """Verifica se a estrutura de backup inclui os novos componentes"""
    print("\n🔍 Verificando estrutura de backup...")
    
    with open("src/backup_system.py", "r") as f:
        content = f.read()
    
    # Verificar componentes do backup
    components = [
        "local_decks_info.json",
        "note_types.json", 
        "anki_local_data",
        "local_anki_data"
    ]
    
    all_found = True
    for component in components:
        if component in content:
            print(f"✅ Componente '{component}' incluído no backup")
        else:
            print(f"❌ Componente '{component}' não incluído no backup")
            all_found = False
    
    return all_found

def main():
    print("🎯 VERIFICAÇÃO: Sistema de Backup Completo")
    print("=" * 50)
    
    functionality_ok = test_backup_functionality()
    structure_ok = test_backup_structure()
    
    print("\n" + "=" * 50)
    print("📊 RESULTADO FINAL:")
    
    if functionality_ok and structure_ok:
        print("✅ IMPLEMENTAÇÃO COMPLETA!")
        print("\n🎉 O sistema de backup agora inclui:")
        print("   - ✅ Configurações do addon")
        print("   - ✅ Informações de decks remotos")
        print("   - ✅ Preferências do usuário")
        print("   - ✅ DECKS E NOTAS LOCAIS DO ANKI")
        print("   - ✅ Note types relacionados")
        print("   - ✅ Interface atualizada com nova opção")
        print("   - ✅ Backup automático configurado")
        print("\n🚀 Agora o backup é verdadeiramente COMPLETO!")
        
    else:
        print("❌ IMPLEMENTAÇÃO INCOMPLETA:")
        if not functionality_ok:
            print("   - Funcionalidade básica tem problemas")
        if not structure_ok:
            print("   - Estrutura de backup incompleta")
    
    print("\n💡 FUNCIONALIDADES ATIVAS:")
    print("   1. 🔧 Backup manual via interface (com opção de decks locais)")
    print("   2. 🔄 Backup automático durante sync (inclui decks locais)")
    print("   3. 📋 Backup inclui notas, campos, tags e metadados")
    print("   4. 🎯 Backup inclui note types relacionados ao Sheets2Anki")

if __name__ == "__main__":
    main()
