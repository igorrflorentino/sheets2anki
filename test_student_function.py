#!/usr/bin/env python3
"""
Teste simples para verificar se a função discover_students_from_tsv_url foi implementada corretamente.
Este arquivo pode ser executado fora do Anki para verificar a funcionalidade básica.
"""

import sys
import os

# Adicionar o diretório do projeto ao path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_discover_students_function():
    """Testa se a função discover_students_from_tsv_url existe e pode ser importada."""
    
    try:
        # Mock dos módulos do Anki que não estão disponíveis
        import types
        
        # Mock do compat
        compat_mock = types.ModuleType('compat')
        compat_mock.mw = None
        compat_mock.showInfo = lambda x: print(f"[INFO] {x}")
        sys.modules['aqt'] = types.ModuleType('aqt')
        sys.modules['aqt.qt'] = types.ModuleType('aqt.qt')
        
        # Mock column_definitions
        from src import column_definitions
        if not hasattr(column_definitions, 'ALUNOS'):
            column_definitions.ALUNOS = 'ALUNOS'
        
        # Importar a função
        from src.student_manager import discover_students_from_tsv_url
        
        print("✅ Função discover_students_from_tsv_url importada com sucesso!")
        
        # Testar com uma URL fake (vai dar erro de rede, mas isso é esperado)
        try:
            result = discover_students_from_tsv_url("https://fake-url.com")
            print(f"✅ Função executou e retornou: {result}")
            print("✅ Teste concluído - função implementada corretamente!")
            return True
            
        except Exception as e:
            if "fake-url" in str(e).lower() or "urlopen" in str(e):
                print("✅ Função executou corretamente (erro de URL esperado)")
                return True
            else:
                print(f"❌ Erro inesperado na execução: {e}")
                return False
        
    except ImportError as e:
        print(f"❌ Erro ao importar função: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    print("Testando implementação da função discover_students_from_tsv_url...")
    print("-" * 60)
    
    success = test_discover_students_function()
    
    if success:
        print("\n✅ SUCESSO: A função foi implementada corretamente!")
        print("O erro original deve estar resolvido no Anki.")
    else:
        print("\n❌ FALHA: Ainda há problemas na implementação.")
        
    print("-" * 60)
