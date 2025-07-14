#!/usr/bin/env python3
"""
Testes de integração para funcionalidades específicas do Sheets2Anki.
Inclui testes para cards ignorados, validação de colunas, e sincronização.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.parseRemoteDeck import build_remote_deck_from_tsv
from src.column_definitions import REQUIRED_COLUMNS

def test_ignored_cards_counting():
    """Testa se a contagem de cards ignorados está funcionando."""
    print("🧪 Testando contagem de cards ignorados...")
    
    # Dados de teste com TODAS as colunas obrigatórias
    test_data = [
        # Headers completos
        REQUIRED_COLUMNS,
        
        # Dados de teste
        ['001', 'Qual é a capital do Brasil?', 'Brasília', 'true', 'Info complementar', 'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 'VUNESP', '2023', 'PC', 'Alta', 'brasil'],
        ['002', 'Qual é a capital da França?', 'Paris', 'false', 'Info complementar', 'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 'VUNESP', '2023', 'PC', 'Alta', 'frança'],
        ['003', 'Qual é a capital da Alemanha?', 'Berlim', 'true', 'Info complementar', 'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 'VUNESP', '2023', 'PC', 'Alta', 'alemanha'],
        ['004', 'Qual é a capital da Itália?', 'Roma', 'false', 'Info complementar', 'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 'VUNESP', '2023', 'PC', 'Alta', 'italia'],
        ['005', 'Qual é a capital da Espanha?', 'Madrid', 'true', 'Info complementar', 'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 'VUNESP', '2023', 'PC', 'Alta', 'espanha'],
    ]
    
    try:
        remote_deck = build_remote_deck_from_tsv(test_data)
        
        # Verificar resultados
        total_questions = len(remote_deck.questions)
        print(f"  ✅ Total de questões processadas: {total_questions}")
        
        # Contar quantas deveriam ser sincronizadas vs ignoradas
        sync_values = [row[3] for row in test_data[1:]]  # Coluna SYNC?
        expected_synced = sum(1 for val in sync_values if val.lower() not in ['false', '0', 'não', 'nao', 'no', 'falso', 'f'])
        expected_ignored = len(sync_values) - expected_synced
        
        print(f"  📊 Esperado sincronizado: {expected_synced}")
        print(f"  📊 Esperado ignorado: {expected_ignored}")
        print(f"  📊 Obtido sincronizado: {total_questions}")
        
        # Verificar se a contagem está correta
        if total_questions == expected_synced:
            print("  ✅ Contagem de cards ignorados está correta!")
            return True
        else:
            print("  ❌ Contagem de cards ignorados está incorreta!")
            return False
            
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_column_validation():
    """Testa validação de colunas obrigatórias."""
    print("\n🧪 Testando validação de colunas...")
    
    # Teste com colunas corretas
    correct_headers = REQUIRED_COLUMNS.copy()
    test_data_correct = [correct_headers, ['1', 'Pergunta', 'Resposta', 'true'] + [''] * (len(correct_headers) - 4)]
    
    try:
        deck = build_remote_deck_from_tsv(test_data_correct)
        print(f"  ✅ Validação com colunas corretas: {len(deck.questions)} questões")
        result_correct = True
    except Exception as e:
        print(f"  ❌ Validação com colunas corretas falhou: {e}")
        result_correct = False
    
    # Teste com colunas faltantes
    incomplete_headers = REQUIRED_COLUMNS[:10]  # Apenas 10 primeiros
    test_data_incomplete = [incomplete_headers, ['1', 'Pergunta', 'Resposta', 'true'] + [''] * (len(incomplete_headers) - 4)]
    
    try:
        deck = build_remote_deck_from_tsv(test_data_incomplete)
        print(f"  ❌ Validação com colunas faltantes deveria falhar mas passou!")
        result_incomplete = False
    except Exception as e:
        print(f"  ✅ Validação com colunas faltantes falhou como esperado: {e}")
        result_incomplete = True
    
    return result_correct and result_incomplete

def test_sync_logic():
    """Testa lógica de sincronização."""
    print("\n🧪 Testando lógica de sincronização...")
    
    from src.column_definitions import should_sync_question
    
    # Casos de teste
    test_cases = [
        ('true', True),
        ('false', False),
        ('1', True),
        ('0', False),
        ('sim', True),
        ('não', False),
        ('yes', True),
        ('no', False),
        ('', True),  # Vazio = sincronizar
        ('VERDADEIRO', True),
        ('FALSO', False),
        ('invalid', True),  # Valor não reconhecido = sincronizar
    ]
    
    results = []
    for value, expected in test_cases:
        fields = {'SYNC?': value}  # A função espera um dict
        result = should_sync_question(fields)
        success = result == expected
        results.append(success)
        status = "✅" if success else "❌"
        print(f"  {status} SYNC?='{value}' -> {result} (esperado: {expected})")
    
    success_rate = sum(results) / len(results)
    print(f"  📊 Taxa de sucesso: {success_rate:.1%}")
    
    return success_rate == 1.0

def test_formula_cleaning():
    """Testa limpeza de fórmulas."""
    print("\n🧪 Testando limpeza de fórmulas...")
    
    from src.parseRemoteDeck import clean_formula_errors
    
    test_cases = [
        ('#NAME?', ''),
        ('#REF!', ''),
        ('#VALUE!', ''),
        ('#DIV/0!', ''),
        ('=SUM(A1:A10)', ''),
        ('Texto normal', 'Texto normal'),
        ('123', '123'),
        ('', ''),
    ]
    
    results = []
    for input_val, expected in test_cases:
        result = clean_formula_errors(input_val)
        success = result == expected
        results.append(success)
        status = "✅" if success else "❌"
        print(f"  {status} '{input_val}' -> '{result}' (esperado: '{expected}')")
    
    success_rate = sum(results) / len(results)
    print(f"  📊 Taxa de sucesso: {success_rate:.1%}")
    
    return success_rate == 1.0

def main():
    """Executa todos os testes de integração."""
    print("🔍 TESTES DE INTEGRAÇÃO - SHEETS2ANKI")
    print("=" * 50)
    
    # Executar todos os testes
    results = []
    results.append(test_ignored_cards_counting())
    results.append(test_column_validation())
    results.append(test_sync_logic())
    results.append(test_formula_cleaning())
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    
    passed = sum(results)
    total = len(results)
    success_rate = passed / total if total > 0 else 0
    
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {passed}")
    print(f"Testes falharam: {total - passed}")
    print(f"Taxa de sucesso: {success_rate:.1%}")
    
    if success_rate == 1.0:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM!")
    
    return success_rate == 1.0

if __name__ == "__main__":
    main()
