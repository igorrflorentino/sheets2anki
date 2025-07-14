#!/usr/bin/env python3
"""
Teste realista usando os dados exatos do CSV de exemplo.
"""

import sys
import os

# Adicionar os diretórios necessários ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_with_real_csv():
    """Testa com os dados exatos do CSV de exemplo."""
    from src.parseRemoteDeck import parse_tsv_data, build_remote_deck_from_tsv
    
    print("🧪 Testando com dados reais do CSV...")
    
    # Dados exatos do CSV (convertidos para TSV) - COMPLETO com todas as colunas
    csv_data = '''ID	PERGUNTA	LEVAR PARA PROVA	SYNC?	INFO COMPLEMENTAR	INFO DETALHADA	EXEMPLO 1	EXEMPLO 2	EXEMPLO 3	TOPICO	SUBTOPICO	CONCEITO	BANCAS	ULTIMO ANO EM PROVA	CARREIRA	IMPORTANCIA	TAGS ADICIONAIS
001	Qual é a capital do Brasil?	Brasília	true	Brasília foi fundada em 1960	A capital federal do Brasil é Brasília	Plano Piloto	Distrito Federal	Congresso Nacional	Geografia	Capitais	Capital de país	FCC	2023	PC	Alta	brasil;capital;geografia
002	Quem foi o primeiro presidente do Brasil?	Deodoro da Fonseca	1	Deodoro da Fonseca foi o primeiro presidente	Governou de 1889 a 1891	República Velha	Proclamação da República	Marechal Deodoro	História	República	Primeiro governante	CESPE	2022	PC	Alta	historia;presidentes;brasil
003	Qual é a fórmula da água?	H2O	false	H2O é a fórmula química da água	Composta por 2 átomos de hidrogênio e 1 de oxigênio	Molécula polar	Ligação covalente	Ponto de fusão 0°C	Química	Química Geral	Fórmula molecular	VUNESP	2021	PC	Média	quimica;agua;formula
004	Qual é o maior planeta do sistema solar?	Júpiter	0	Júpiter é o maior planeta	Planeta gasoso com maior massa	Grande Mancha Vermelha	Luas galileanas	Cinturão de asteroides	Astronomia	Sistema Solar	Planeta maior	FGV	2023	PC	Média	astronomia;planetas;jupiter
005	Qual é a velocidade da luz?	299.792.458 m/s	verdadeiro	299.792.458 m/s no vácuo	Velocidade máxima no universo	Teoria da relatividade	Einstein	Constante física	Física	Óptica	Constante física	CESPE	2022	PC	Alta	fisica;luz;velocidade
006	Qual é a capital da França?	Paris	f	Paris é a capital da França	Cidade luz da Europa	Torre Eiffel	Museu do Louvre	Rio Sena	Geografia	Capitais Europeias	Capital de país	FCC	2020	PC	Baixa	geografia;europa;capital
007	Qual é o símbolo químico do ouro?	Au	SIM	Au vem do latim aurum	Metal precioso número atômico 79	Ourives	Joalheria	Reserva de valor	Química	Tabela Periódica	Símbolo químico	VUNESP	2023	PC	Alta	quimica;ouro;simbolo
008	Quantos continentes existem?	6 continentes		Tradicionalmente são 6 continentes	Ásia África América Europa Oceania Antártida	Pangeia	Deriva continental	Placas tectônicas	Geografia	Continentes	Quantidade de continentes	FGV	2021	PC	Média	geografia;continentes;mundo'''
    
    try:
        # Processar como TSV
        data = parse_tsv_data(csv_data)
        deck = build_remote_deck_from_tsv(data)
        
        print(f"  📋 Total de linhas no CSV: {len(data) - 1}")
        print(f"  📋 Total de questões sincronizadas: {len(deck.questions)}")
        
        # Analisar quais questões foram sincronizadas
        expected_synced = []
        expected_not_synced = []
        
        # Mapear quais linhas deveriam ser sincronizadas
        sync_values = ['true', '1', 'verdadeiro', 'SIM', '']  # valores que devem sincronizar
        no_sync_values = ['false', '0', 'f']  # valores que não devem sincronizar
        
        lines_data = [
            ('001', 'true', True),
            ('002', '1', True),
            ('003', 'false', False),
            ('004', '0', False),
            ('005', 'verdadeiro', True),
            ('006', 'f', False),
            ('007', 'SIM', True),
            ('008', '', True),  # vazio = sincronizar
        ]
        
        print("\n  📊 Análise detalhada:")
        for line_id, sync_value, should_sync in lines_data:
            if should_sync:
                expected_synced.append(line_id)
            else:
                expected_not_synced.append(line_id)
            
            print(f"    {'✅' if should_sync else '❌'} ID {line_id}: SYNC?='{sync_value}' -> {'Deve sincronizar' if should_sync else 'Não deve sincronizar'}")
        
        print(f"\n  📋 Esperado sincronizadas: {expected_synced}")
        print(f"  📋 Esperado não sincronizadas: {expected_not_synced}")
        
        # Verificar se as questões sincronizadas estão corretas
        synced_ids = [q['fields']['ID'] for q in deck.questions]
        print(f"  📋 IDs realmente sincronizados: {synced_ids}")
        
        # Verificar se está correto
        success = set(synced_ids) == set(expected_synced)
        print(f"\n  {'✅' if success else '❌'} Resultado: {'Correto' if success else 'Incorreto'}")
        
        if not success:
            missing = set(expected_synced) - set(synced_ids)
            extra = set(synced_ids) - set(expected_synced)
            if missing:
                print(f"    ❌ Faltando: {missing}")
            if extra:
                print(f"    ❌ Sincronizados indevidamente: {extra}")
        
        return success
        
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal."""
    print("🔍 Teste realista com dados do CSV...\n")
    
    success = test_with_real_csv()
    
    if success:
        print("\n🎉 Teste passou! A funcionalidade está funcionando corretamente.")
        print("   O problema deve estar em como você está criando ou carregando o CSV.")
    else:
        print("\n⚠️  Teste falhou! Há um problema na lógica de sincronização.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
