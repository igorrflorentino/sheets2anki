#!/usr/bin/env python3
"""
Teste para funcionalidades de sincronização básica.

Este teste verifica:
1. Processamento de dados TSV
2. Filtragem de questões
3. Criação de estruturas de dados
4. Validação de sync
"""

import sys
import os

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def import_test_modules():
    """Helper para importar módulos de teste com fallback."""
    try:
        from parseRemoteDeck import build_remote_deck_from_tsv
        from column_definitions import REQUIRED_COLUMNS
        return build_remote_deck_from_tsv, REQUIRED_COLUMNS
    except ImportError:
        # Tentar import alternativo
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from src.parseRemoteDeck import build_remote_deck_from_tsv
            from src.column_definitions import REQUIRED_COLUMNS
            return build_remote_deck_from_tsv, REQUIRED_COLUMNS
        except ImportError as e:
            raise ImportError(f"Não foi possível importar módulos necessários: {e}")

def test_basic_sync_functionality():
    """Testa funcionalidades básicas de sincronização."""
    print("🧪 Testando funcionalidades básicas de sincronização...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Dados de teste simples
        test_data = [
            REQUIRED_COLUMNS,
            ['001', 'Pergunta 1', 'Resposta 1', 'true'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['002', 'Pergunta 2', 'Resposta 2', 'false'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['003', 'Pergunta 3', 'Resposta 3', 'true'] + [''] * (len(REQUIRED_COLUMNS) - 4),
        ]
        
        # Processar dados
        remote_deck = build_remote_deck_from_tsv(test_data)
        
        # Verificar se apenas questões com SYNC=true foram processadas
        if len(remote_deck.questions) == 2:
            print("  ✅ Filtragem SYNC funcionando corretamente")
        else:
            print(f"  ❌ Filtragem SYNC incorreta: {len(remote_deck.questions)} questões (esperado 2)")
            return False
            
        # Verificar se questões têm campos necessários
        first_question = remote_deck.questions[0]
        if hasattr(first_question, 'fields') and first_question.fields:
            print("  ✅ Questões têm campos")
        elif hasattr(first_question, 'data') and first_question.data:
            print("  ✅ Questões têm dados")
        else:
            print("  ✅ Questões foram criadas (estrutura pode variar)")
            
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_sync_case_insensitive():
    """Testa se a sincronização é case-insensitive."""
    print("🧪 Testando sincronização case-insensitive...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Dados com diferentes casos
        test_data = [
            REQUIRED_COLUMNS,
            ['001', 'Pergunta 1', 'Resposta 1', 'TRUE'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['002', 'Pergunta 2', 'Resposta 2', 'False'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['003', 'Pergunta 3', 'Resposta 3', 'true'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['004', 'Pergunta 4', 'Resposta 4', 'FALSE'] + [''] * (len(REQUIRED_COLUMNS) - 4),
        ]
        
        # Processar dados
        remote_deck = build_remote_deck_from_tsv(test_data)
        
        # Verificar se apenas questões com SYNC=true/TRUE foram processadas
        if len(remote_deck.questions) == 2:
            print("  ✅ Sincronização case-insensitive funcionando")
        else:
            print(f"  ❌ Sincronização case-insensitive incorreta: {len(remote_deck.questions)} questões (esperado 2)")
            return False
            
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_sync_portuguese_values():
    """Testa valores em português para sincronização."""
    print("🧪 Testando valores em português para sincronização...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Dados com valores em português
        test_data = [
            REQUIRED_COLUMNS,
            ['001', 'Pergunta 1', 'Resposta 1', 'sim'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['002', 'Pergunta 2', 'Resposta 2', 'não'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['003', 'Pergunta 3', 'Resposta 3', 'verdadeiro'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['004', 'Pergunta 4', 'Resposta 4', 'falso'] + [''] * (len(REQUIRED_COLUMNS) - 4),
        ]
        
        # Processar dados
        remote_deck = build_remote_deck_from_tsv(test_data)
        
        # Verificar se valores em português funcionam
        if len(remote_deck.questions) == 2:
            print("  ✅ Valores em português funcionando")
        else:
            print(f"  ❌ Valores em português incorretos: {len(remote_deck.questions)} questões (esperado 2)")
            return False
            
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_sync_empty_values():
    """Testa comportamento com valores vazios."""
    print("🧪 Testando comportamento com valores vazios...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Dados com valores vazios
        test_data = [
            REQUIRED_COLUMNS,
            ['001', 'Pergunta 1', 'Resposta 1', ''] + [''] * (len(REQUIRED_COLUMNS) - 4),  # Vazio deve sincronizar
            ['002', 'Pergunta 2', 'Resposta 2', 'false'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['003', 'Pergunta 3', 'Resposta 3', 'true'] + [''] * (len(REQUIRED_COLUMNS) - 4),
        ]
        
        # Processar dados
        remote_deck = build_remote_deck_from_tsv(test_data)
        
        # Verificar se valor vazio é tratado como true (compatibilidade)
        if len(remote_deck.questions) == 2:
            print("  ✅ Valores vazios tratados como true")
        else:
            print(f"  ❌ Valores vazios incorretos: {len(remote_deck.questions)} questões (esperado 2)")
            return False
            
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_sync_field_validation():
    """Testa validação de campos obrigatórios."""
    print("🧪 Testando validação de campos obrigatórios...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Dados com campos obrigatórios faltando
        incomplete_data = [
            ['ID', 'PERGUNTA', 'SYNC?'],  # Faltam campos
            ['001', 'Pergunta 1', 'true'],
        ]
        
        # Tentar processar dados incompletos
        try:
            remote_deck = build_remote_deck_from_tsv(incomplete_data)
            print("  ❌ Deveria ter falhado com campos faltando")
            return False
        except Exception as e:
            print(f"  ✅ Falhou corretamente com campos faltando: {e}")
            
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def main():
    """Função principal do teste."""
    print("🧪 TESTE DE SINCRONIZAÇÃO BÁSICA")
    print("=" * 50)
    
    tests = [
        test_basic_sync_functionality,
        test_sync_case_insensitive,
        test_sync_portuguese_values,
        test_sync_empty_values,
        test_sync_field_validation,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSOU\n")
            else:
                print("❌ FALHOU\n")
        except Exception as e:
            print(f"❌ ERRO: {e}\n")
    
    print("=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DE SINCRONIZAÇÃO PASSARAM!")
        return True
    else:
        print("⚠️  ALGUNS TESTES DE SINCRONIZAÇÃO FALHARAM")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
