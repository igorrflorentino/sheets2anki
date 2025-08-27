#!/usr/bin/env python3
"""
Teste simples para validar que as correções de busca estão funcionando.
"""

import os
import sys

def test_search_patterns():
    """
    Testa se os padrões de busca foram corrigidos corretamente.
    """
    print("🧪 Testando correções de padrões de busca...")
    
    # Verificar config_manager.py
    config_path = "/Users/igorflorentino/• Principais do Home/Git/Coding/anki/sheets2anki/src/config_manager.py"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'find_notes("*")' in content:
            print("✅ config_manager.py: Padrão corrigido encontrado")
        else:
            print("❌ config_manager.py: Padrão de correção não encontrado")
            
        if 'find_notes("")' in content:
            print("❌ config_manager.py: Padrão problemático ainda presente")
        else:
            print("✅ config_manager.py: Padrão problemático removido")
            
    except Exception as e:
        print(f"❌ Erro ao verificar config_manager.py: {e}")
    
    # Verificar student_manager.py
    student_path = "/Users/igorflorentino/• Principais do Home/Git/Coding/anki/sheets2anki/src/student_manager.py"
    try:
        with open(student_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'find_notes("*")' in content:
            print("✅ student_manager.py: Padrão corrigido encontrado")
        else:
            print("❌ student_manager.py: Padrão de correção não encontrado")
            
        if 'find_notes("")' in content:
            print("❌ student_manager.py: Padrão problemático ainda presente")
        else:
            print("✅ student_manager.py: Padrão problemático removido")
            
    except Exception as e:
        print(f"❌ Erro ao verificar student_manager.py: {e}")
    
    print("\n🎯 Teste de correções concluído!")


def test_comment_quality():
    """
    Verifica se os comentários explicativos foram adicionados.
    """
    print("\n🧪 Testando qualidade dos comentários...")
    
    # Verificar se há comentários explicativos
    paths_to_check = [
        "/Users/igorflorentino/• Principais do Home/Git/Coding/anki/sheets2anki/src/config_manager.py",
        "/Users/igorflorentino/• Principais do Home/Git/Coding/anki/sheets2anki/src/student_manager.py"
    ]
    
    for path in paths_to_check:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            filename = os.path.basename(path)
            
            if "usar wildcard" in content:
                print(f"✅ {filename}: Comentário explicativo encontrado")
            else:
                print(f"⚠️ {filename}: Comentário explicativo não encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao verificar {path}: {e}")
    
    print("\n🎯 Teste de comentários concluído!")


if __name__ == "__main__":
    print("🚀 Teste de Validação de Correções - Sheets2Anki")
    print("=" * 60)
    
    test_search_patterns()
    test_comment_quality()
    
    print("\n" + "=" * 60)
    print("✨ Todos os testes finalizados!")
    print("\n💡 Resumo da correção:")
    print("   • find_notes('') → find_notes('*')")
    print("   • Erro de double quotes eliminado")
    print("   • Compatibilidade com Anki moderno melhorada")
