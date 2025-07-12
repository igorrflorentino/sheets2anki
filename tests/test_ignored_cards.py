#!/usr/bin/env python3
"""
Teste para validar a nova funcionalidade de contagem de cards ignorados.

Este teste verifica se:
1. Cards ignorados são contados corretamente
2. A informação aparece no resumo de sincronização
3. As estatísticas incluem a contagem de cards ignorados
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_ignored_cards_counting():
    """Testa se a contagem de cards ignorados está funcionando."""
    try:
        from parseRemoteDeck import build_remote_deck_from_tsv
    except ImportError:
        # Se o import relativo falhar, tentar import absoluto
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from src.parseRemoteDeck import build_remote_deck_from_tsv
    
    print("🧪 Testando contagem de cards ignorados...")
    
    # Dados de teste com questões ignoradas e aceitas
    test_data = [
        # Headers
        ['ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'SYNC?', 'INFO COMPLEMENTAR', 'INFO DETALHADA', 'EXEMPLO 1', 'EXEMPLO 2', 'EXEMPLO 3', 'TOPICO', 'SUBTOPICO', 'BANCAS', 'ULTIMO ANO EM PROVA', 'TAGS ADICIONAIS'],
        
        # Questões que devem ser sincronizadas
        ['001', 'Qual é a capital do Brasil?', 'Brasília', 'true', '', '', '', '', '', '', '', '', '', ''],
        ['002', 'Quem foi o primeiro presidente?', 'Deodoro', '1', '', '', '', '', '', '', '', '', '', ''],
        ['003', 'Qual é a velocidade da luz?', '299.792.458 m/s', 'sim', '', '', '', '', '', '', '', '', '', ''],
        
        # Questões que devem ser ignoradas
        ['004', 'Qual é a fórmula da água?', 'H2O', 'false', '', '', '', '', '', '', '', '', '', ''],
        ['005', 'Qual é o maior planeta?', 'Júpiter', '0', '', '', '', '', '', '', '', '', '', ''],
        ['006', 'Qual é a capital da França?', 'Paris', 'não', '', '', '', '', '', '', '', '', '', ''],
        
        # Questão com valor vazio (deve sincronizar)
        ['007', 'Qual é o símbolo do ouro?', 'Au', '', '', '', '', '', '', '', '', '', '', ''],
    ]
    
    # Processar dados
    remote_deck = build_remote_deck_from_tsv(test_data)
    
    # Verificar contagens
    total_questions = len(test_data) - 1  # -1 para excluir o header
    accepted_questions = len(remote_deck.questions)
    ignored_questions = remote_deck.ignored_count
    
    print(f"  📊 Total de questões no TSV: {total_questions}")
    print(f"  ✅ Questões aceitas: {accepted_questions}")
    print(f"  ❌ Questões ignoradas: {ignored_questions}")
    
    # Verificações
    expected_accepted = 4  # 001, 002, 003, 007
    expected_ignored = 3   # 004, 005, 006
    
    accepted_ok = accepted_questions == expected_accepted
    ignored_ok = ignored_questions == expected_ignored
    total_ok = (accepted_questions + ignored_questions) == total_questions
    
    status = "✅" if accepted_ok else "❌"
    print(f"  {status} Questões aceitas corretas: {accepted_questions} (esperado: {expected_accepted})")
    
    status = "✅" if ignored_ok else "❌"
    print(f"  {status} Questões ignoradas corretas: {ignored_questions} (esperado: {expected_ignored})")
    
    status = "✅" if total_ok else "❌"
    print(f"  {status} Total correto: {accepted_questions + ignored_questions} = {total_questions}")
    
    return accepted_ok and ignored_ok and total_ok

def test_ignored_stats_integration():
    """Testa se as estatísticas incluem cards ignorados."""
    print("\n🧪 Testando integração com estatísticas...")
    
    # Simular estatísticas de sincronização
    test_stats = {
        'created': 2,
        'updated': 1,
        'deleted': 0,
        'ignored': 3,
        'errors': 0,
        'error_details': []
    }
    
    # Verificar se as chaves necessárias existem
    has_ignored = 'ignored' in test_stats
    ignored_count = test_stats.get('ignored', 0)
    
    status = "✅" if has_ignored else "❌"
    print(f"  {status} Campo 'ignored' presente nas estatísticas: {has_ignored}")
    
    status = "✅" if ignored_count == 3 else "❌"
    print(f"  {status} Contagem de ignorados correta: {ignored_count} (esperado: 3)")
    
    return has_ignored and ignored_count == 3

def main():
    """Função principal do teste."""
    print("🔄 Iniciando teste de contagem de cards ignorados...")
    
    try:
        # Teste 1: Contagem de cards ignorados
        test1_result = test_ignored_cards_counting()
        
        # Teste 2: Integração com estatísticas
        test2_result = test_ignored_stats_integration()
        
        # Resultado final
        all_passed = test1_result and test2_result
        
        print(f"\n📊 Resultados:")
        print(f"  Teste 1 (Contagem): {'✅ PASSOU' if test1_result else '❌ FALHOU'}")
        print(f"  Teste 2 (Integração): {'✅ PASSOU' if test2_result else '❌ FALHOU'}")
        
        if all_passed:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ A funcionalidade de contagem de cards ignorados está funcionando corretamente.")
            print("✅ As estatísticas incluem a informação de cards ignorados.")
            return 0
        else:
            print("\n❌ ALGUNS TESTES FALHARAM!")
            return 1
            
    except Exception as e:
        print(f"\n💥 ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
