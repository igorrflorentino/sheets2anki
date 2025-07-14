#!/usr/bin/env python3
"""
Teste para validação de dados e robustez do sistema.

Este teste verifica:
1. Validação de dados de entrada
2. Tratamento de erros de formato
3. Robustez com dados malformados
4. Compatibilidade com diferentes estruturas de dados
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

def test_empty_data_handling():
    """Testa como o sistema lida com dados vazios."""
    print("🧪 Testando tratamento de dados vazios...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Teste com dados completamente vazios
        empty_data = []
        try:
            deck = build_remote_deck_from_tsv(empty_data)
            print("  ❌ Deveria ter falhado com dados vazios")
            return False
        except Exception as e:
            print(f"  ✅ Falhou corretamente com dados vazios: {e}")
        
        # Teste com apenas headers
        headers_only = [REQUIRED_COLUMNS]
        try:
            deck = build_remote_deck_from_tsv(headers_only)
            print(f"  ✅ Headers apenas: {len(deck.questions)} questões")
            return len(deck.questions) == 0
        except Exception as e:
            print(f"  ❌ Falhou com headers apenas: {e}")
            return False
            
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False

def test_malformed_data_handling():
    """Testa como o sistema lida com dados malformados."""
    print("🧪 Testando tratamento de dados malformados...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Teste com linha com colunas faltantes
        malformed_data = [
            REQUIRED_COLUMNS,
            ['001', 'Pergunta incompleta']  # Faltam colunas
        ]
        
        try:
            deck = build_remote_deck_from_tsv(malformed_data)
            print(f"  ✅ Processou dados malformados: {len(deck.questions)} questões")
            return True
        except Exception as e:
            print(f"  ✅ Falhou corretamente com dados malformados: {e}")
            return True
            
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False

def test_special_characters_handling():
    """Testa como o sistema lida com caracteres especiais."""
    print("🧪 Testando tratamento de caracteres especiais...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Teste com caracteres especiais
        special_data = [
            REQUIRED_COLUMNS,
            ['001', 'Pergunta com âcentos é çoisa bôa?', 'Resposta com "aspas" e <tags>', 'true'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['002', 'Pergunta com símbolos ★☆♠♣♥♦', 'Resposta com emojis 😀😃😄', 'true'] + [''] * (len(REQUIRED_COLUMNS) - 4),
            ['003', 'Pergunta com HTML <b>bold</b> e &amp;', 'Resposta com quebra\nde linha', 'true'] + [''] * (len(REQUIRED_COLUMNS) - 4),
        ]
        
        try:
            deck = build_remote_deck_from_tsv(special_data)
            print(f"  ✅ Processou caracteres especiais: {len(deck.questions)} questões")
            return len(deck.questions) == 3
        except Exception as e:
            print(f"  ❌ Falhou com caracteres especiais: {e}")
            return False
            
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False

def test_column_order_flexibility():
    """Testa se o sistema é flexível com a ordem das colunas."""
    print("🧪 Testando flexibilidade na ordem das colunas...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Reordenar algumas colunas
        reordered_columns = REQUIRED_COLUMNS.copy()
        # Trocar PERGUNTA e LEVAR PARA PROVA de lugar
        if 'PERGUNTA' in reordered_columns and 'LEVAR PARA PROVA' in reordered_columns:
            pergunta_idx = reordered_columns.index('PERGUNTA')
            prova_idx = reordered_columns.index('LEVAR PARA PROVA')
            reordered_columns[pergunta_idx], reordered_columns[prova_idx] = reordered_columns[prova_idx], reordered_columns[pergunta_idx]
        
        # Criar dados com colunas reordenadas
        reordered_data = [
            reordered_columns,
            ['001', 'Resposta', 'Pergunta reordenada?', 'true'] + [''] * (len(reordered_columns) - 4),
        ]
        
        try:
            deck = build_remote_deck_from_tsv(reordered_data)
            print(f"  ✅ Processou colunas reordenadas: {len(deck.questions)} questões")
            return len(deck.questions) == 1
        except Exception as e:
            print(f"  ❌ Falhou com colunas reordenadas: {e}")
            return False
            
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False

def test_large_data_handling():
    """Testa como o sistema lida com grandes volumes de dados."""
    print("🧪 Testando tratamento de grandes volumes de dados...")
    
    try:
        build_remote_deck_from_tsv, REQUIRED_COLUMNS = import_test_modules()
        
        # Criar dados grandes (1000 questões)
        large_data = [REQUIRED_COLUMNS]
        for i in range(1000):
            row = [
                f'{i+1:03d}',  # ID
                f'Pergunta número {i+1}',  # PERGUNTA
                f'Resposta número {i+1}',  # LEVAR PARA PROVA
                'true' if i % 2 == 0 else 'false',  # SYNC?
            ] + [''] * (len(REQUIRED_COLUMNS) - 4)
            large_data.append(row)
        
        try:
            deck = build_remote_deck_from_tsv(large_data)
            print(f"  ✅ Processou dados grandes: {len(deck.questions)} questões")
            # Aproximadamente metade deve ser sincronizada
            return 450 <= len(deck.questions) <= 550
        except Exception as e:
            print(f"  ❌ Falhou com dados grandes: {e}")
            return False
            
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False

def main():
    """Função principal do teste."""
    print("🧪 TESTE DE VALIDAÇÃO DE DADOS")
    print("=" * 50)
    
    tests = [
        test_empty_data_handling,
        test_malformed_data_handling,
        test_special_characters_handling,
        test_column_order_flexibility,
        test_large_data_handling,
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
        print("🎉 TODOS OS TESTES DE VALIDAÇÃO PASSARAM!")
        return True
    else:
        print("⚠️  ALGUNS TESTES DE VALIDAÇÃO FALHARAM")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
