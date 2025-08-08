#!/usr/bin/env python3
"""
Script de debug para testar a descoberta de estudantes.
"""

import sys
import os
sys.path.insert(0, 'src')

from src.config_manager import (
    get_remote_decks, 
    discover_all_students_from_remote_decks,
    update_available_students_from_discovery,
    get_global_student_config
)

def debug_discovery():
    """Testa a descoberta de estudantes passo a passo."""
    print("🔍 DEBUG: Testando descoberta de estudantes")
    print("=" * 50)
    
    # Passo 1: Verificar decks remotos
    print("📋 Passo 1: Verificando decks remotos...")
    try:
        remote_decks = get_remote_decks()
        print(f"   ✓ Encontrados {len(remote_decks)} decks remotos:")
        for i, (url, info) in enumerate(remote_decks.items(), 1):
            print(f"   {i}. {info.get('remote_deck_name', 'Nome não definido')}")
            print(f"      URL: {url[:80]}...")
    except Exception as e:
        print(f"   ❌ Erro ao obter decks remotos: {e}")
        return
    
    # Passo 2: Testar descoberta de estudantes
    print(f"\n🔍 Passo 2: Descobrindo estudantes de {len(remote_decks)} decks...")
    try:
        discovered_students = discover_all_students_from_remote_decks()
        print(f"   ✓ Descobertos {len(discovered_students)} estudantes únicos:")
        for i, student in enumerate(discovered_students, 1):
            print(f"   {i}. {student}")
    except Exception as e:
        print(f"   ❌ Erro na descoberta: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Passo 3: Verificar configuração atual
    print(f"\n⚙️  Passo 3: Verificando configuração atual...")
    try:
        config = get_global_student_config()
        current_available = config.get("available_students", [])
        current_enabled = config.get("enabled_students", [])
        print(f"   ✓ Alunos disponíveis atuais: {len(current_available)}")
        for i, student in enumerate(current_available, 1):
            print(f"     {i}. {student}")
        print(f"   ✓ Alunos habilitados atuais: {len(current_enabled)}")
        for i, student in enumerate(current_enabled, 1):
            print(f"     {i}. {student}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar configuração: {e}")
        return
    
    # Passo 4: Testar atualização
    print(f"\n🔄 Passo 4: Testando atualização da configuração...")
    try:
        final_students, new_count = update_available_students_from_discovery()
        print(f"   ✓ Resultado da atualização:")
        print(f"     - Total de alunos disponíveis: {len(final_students)}")
        print(f"     - Novos alunos encontrados: {new_count}")
        print(f"   ✓ Lista final de alunos disponíveis:")
        for i, student in enumerate(final_students, 1):
            print(f"     {i}. {student}")
    except Exception as e:
        print(f"   ❌ Erro na atualização: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n✅ Debug concluído com sucesso!")

if __name__ == "__main__":
    debug_discovery()
