#!/usr/bin/env python3
"""
Teste avançado para simular o comportamento da sincronização seletiva.

Este teste simula cenários reais de uso da funcionalidade SYNC?.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_sync_behavior():
    """Testa o comportamento da sincronização com diferentes cenários."""
    from column_definitions import should_sync_question, SYNC
    
    print("🧪 Testando comportamento da sincronização seletiva...")
    
    # Simular dados de uma planilha
    planilha_data = [
        # Questões que devem ser sincronizadas
        {'ID': '001', 'PERGUNTA': 'Qual é a capital do Brasil?', 'LEVAR PARA PROVA': 'Brasília', 'SYNC?': 'true'},
        {'ID': '002', 'PERGUNTA': 'Quem foi o primeiro presidente?', 'LEVAR PARA PROVA': 'Deodoro da Fonseca', 'SYNC?': '1'},
        {'ID': '003', 'PERGUNTA': 'Qual é a velocidade da luz?', 'LEVAR PARA PROVA': '299.792.458 m/s', 'SYNC?': 'sim'},
        
        # Questões que NÃO devem ser sincronizadas
        {'ID': '004', 'PERGUNTA': 'Qual é a fórmula da água?', 'LEVAR PARA PROVA': 'H2O', 'SYNC?': 'false'},
        {'ID': '005', 'PERGUNTA': 'Qual é o maior planeta?', 'LEVAR PARA PROVA': 'Júpiter', 'SYNC?': '0'},
        {'ID': '006', 'PERGUNTA': 'Qual é a capital da França?', 'LEVAR PARA PROVA': 'Paris', 'SYNC?': 'não'},
        
        # Questões com valores especiais
        {'ID': '007', 'PERGUNTA': 'Qual é o símbolo do ouro?', 'LEVAR PARA PROVA': 'Au', 'SYNC?': ''},  # Vazio - deve sincronizar
        {'ID': '008', 'PERGUNTA': 'Quantos continentes existem?', 'LEVAR PARA PROVA': '6 continentes', 'SYNC?': 'maybe'},  # Valor estranho - deve sincronizar
    ]
    
    # Simular processamento
    questoes_para_sincronizar = []
    questoes_ignoradas = []
    
    for questao in planilha_data:
        if should_sync_question(questao):
            questoes_para_sincronizar.append(questao)
        else:
            questoes_ignoradas.append(questao)
    
    # Verificar resultados
    print(f"  📊 Total de questões na planilha: {len(planilha_data)}")
    print(f"  ✅ Questões para sincronizar: {len(questoes_para_sincronizar)}")
    print(f"  ❌ Questões ignoradas: {len(questoes_ignoradas)}")
    
    # Verificar se o comportamento está correto
    expected_sync = 5  # 001, 002, 003, 007, 008
    expected_ignore = 3  # 004, 005, 006
    
    sync_ok = len(questoes_para_sincronizar) == expected_sync
    ignore_ok = len(questoes_ignoradas) == expected_ignore
    
    print(f"  {'✅' if sync_ok else '❌'} Questões sincronizadas: {len(questoes_para_sincronizar)} (esperado: {expected_sync})")
    print(f"  {'✅' if ignore_ok else '❌'} Questões ignoradas: {len(questoes_ignoradas)} (esperado: {expected_ignore})")
    
    # Mostrar detalhes das questões sincronizadas
    print("\n  📋 Questões que serão sincronizadas:")
    for q in questoes_para_sincronizar:
        print(f"    - {q['ID']}: {q['PERGUNTA'][:30]}... (SYNC?={q['SYNC?']})")
    
    # Mostrar detalhes das questões ignoradas
    print("\n  🚫 Questões que serão ignoradas:")
    for q in questoes_ignoradas:
        print(f"    - {q['ID']}: {q['PERGUNTA'][:30]}... (SYNC?={q['SYNC?']})")
    
    return sync_ok and ignore_ok

def test_tsv_parsing_simulation():
    """Simula o parsing de TSV com a nova coluna SYNC?."""
    print("\n🧪 Testando simulação de parsing TSV...")
    
    # Simular conteúdo TSV
    tsv_content = """ID	PERGUNTA	LEVAR PARA PROVA	SYNC?	INFO COMPLEMENTAR	INFO DETALHADA	EXEMPLO 1	EXEMPLO 2	EXEMPLO 3	TOPICO	SUBTOPICO	BANCAS	ULTIMO ANO EM PROVA	TAGS ADICIONAIS
001	Qual é a capital do Brasil?	Brasília	true	Brasília fundada em 1960	Capital federal	Plano Piloto	DF	Congresso	Geografia	Capitais	FCC	2023	geografia
002	Quem foi o primeiro presidente?	Deodoro da Fonseca	false	Deodoro da Fonseca	1889-1891	República Velha	Proclamação	Marechal	História	República	CESPE	2022	historia
003	Qual é a fórmula da água?	H2O	1	H2O é a fórmula	2H + 1O	Molécula polar	Ligação covalente	Ponto fusão	Química	Geral	VUNESP	2021	quimica"""
    
    # Simular processamento
    import csv
    import io
    
    # Processar TSV
    lines = tsv_content.strip().split('\n')
    reader = csv.DictReader(lines, delimiter='\t')
    
    questoes_processadas = []
    questoes_filtradas = []
    
    from column_definitions import should_sync_question
    
    for row in reader:
        # Simular validação básica
        if row['ID'] and row['PERGUNTA']:
            if should_sync_question(row):
                questoes_processadas.append(row)
            else:
                questoes_filtradas.append(row)
    
    print(f"  📊 Linhas processadas do TSV: {len(questoes_processadas) + len(questoes_filtradas)}")
    print(f"  ✅ Questões aceitas: {len(questoes_processadas)}")
    print(f"  ❌ Questões filtradas: {len(questoes_filtradas)}")
    
    # Verificar resultado esperado
    expected_accepted = 2  # 001 (true), 003 (1)
    expected_filtered = 1  # 002 (false)
    
    accept_ok = len(questoes_processadas) == expected_accepted
    filter_ok = len(questoes_filtradas) == expected_filtered
    
    print(f"  {'✅' if accept_ok else '❌'} Questões aceitas: {len(questoes_processadas)} (esperado: {expected_accepted})")
    print(f"  {'✅' if filter_ok else '❌'} Questões filtradas: {len(questoes_filtradas)} (esperado: {expected_filtered})")
    
    return accept_ok and filter_ok

def test_migration_scenario():
    """Testa cenário de migração de planilhas existentes."""
    print("\n🧪 Testando cenário de migração...")
    
    # Simular planilha antes da migração (sem SYNC?)
    planilha_antiga = [
        {'ID': '001', 'PERGUNTA': 'Qual é a capital do Brasil?', 'LEVAR PARA PROVA': 'Brasília'},
        {'ID': '002', 'PERGUNTA': 'Quem foi o primeiro presidente?', 'LEVAR PARA PROVA': 'Deodoro da Fonseca'},
        {'ID': '003', 'PERGUNTA': 'Qual é a fórmula da água?', 'LEVAR PARA PROVA': 'H2O'},
    ]
    
    # Simular planilha após migração (com SYNC?)
    planilha_nova = [
        {'ID': '001', 'PERGUNTA': 'Qual é a capital do Brasil?', 'LEVAR PARA PROVA': 'Brasília', 'SYNC?': 'true'},
        {'ID': '002', 'PERGUNTA': 'Quem foi o primeiro presidente?', 'LEVAR PARA PROVA': 'Deodoro da Fonseca', 'SYNC?': 'true'},
        {'ID': '003', 'PERGUNTA': 'Qual é a fórmula da água?', 'LEVAR PARA PROVA': 'H2O', 'SYNC?': 'false'},
    ]
    
    from column_definitions import should_sync_question
    
    # Testar planilha nova
    sync_count = sum(1 for q in planilha_nova if should_sync_question(q))
    
    print(f"  📊 Questões na planilha migrada: {len(planilha_nova)}")
    print(f"  ✅ Questões para sincronizar: {sync_count}")
    print(f"  ❌ Questões para ignorar: {len(planilha_nova) - sync_count}")
    
    # Verificar se duas questões são sincronizadas (001 e 002)
    expected_sync = 2
    migration_ok = sync_count == expected_sync
    
    print(f"  {'✅' if migration_ok else '❌'} Migração correta: {sync_count} (esperado: {expected_sync})")
    
    return migration_ok

def main():
    """Função principal do teste."""
    print("🔄 Iniciando testes avançados de sincronização seletiva...\n")
    
    success = True
    
    try:
        # Executar testes
        test1 = test_sync_behavior()
        test2 = test_tsv_parsing_simulation()
        test3 = test_migration_scenario()
        
        success = test1 and test2 and test3
        
        print(f"\n{'✅' if success else '❌'} Resultado final: {'TODOS OS TESTES PASSARAM!' if success else 'ALGUNS TESTES FALHARAM!'}")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
