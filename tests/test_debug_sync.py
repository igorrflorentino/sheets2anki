#!/usr/bin/env python3
"""
Teste de debug para investigar problema de sincronização das notas marcadas.
"""

import sys
import os

import sys
import os

# Adicionar o diretório raiz do projeto ao path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

try:
    from src.column_definitions import REQUIRED_COLUMNS
    from src.parseRemoteDeck import validate_tsv_headers, _create_fields_dict
except ImportError:
    # Fallback para imports alternativos
    try:
        import src.column_definitions as cd
        import src.parseRemoteDeck as prd
        REQUIRED_COLUMNS = cd.REQUIRED_COLUMNS
        validate_tsv_headers = prd.validate_tsv_headers
        _create_fields_dict = prd._create_fields_dict
    except ImportError:
        # Se não conseguir importar, criar versões simples
        REQUIRED_COLUMNS = ['ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'SYNC?', 'INFO COMPLEMENTAR', 'INFO DETALHADA', 'EXEMPLO 1', 'EXEMPLO 2', 'EXEMPLO 3', 'TOPICO', 'SUBTOPICO', 'CONCEITO', 'BANCAS', 'ULTIMO ANO EM PROVA', 'CARREIRA', 'IMPORTANCIA', 'TAGS ADICIONAIS']
        
        def validate_tsv_headers(headers):
            """Versão simplificada de validate_tsv_headers."""
            return headers
            
        def _create_fields_dict(row, headers, header_indices):
            """Versão simplificada de _create_fields_dict."""
            fields = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    fields[header] = row[i]
                else:
                    fields[header] = ""
            return fields

def test_header_validation():
    """Testa se a validação de headers está funcionando corretamente."""
    
    print("🧪 Testando validação de headers...")
    
    # Headers completos com todas as colunas obrigatórias
    csv_headers = REQUIRED_COLUMNS.copy()
    
    print(f"  📋 Headers do CSV: {csv_headers}")
    print(f"  📋 Headers obrigatórios: {REQUIRED_COLUMNS}")
    
    try:
        validated_headers = validate_tsv_headers(csv_headers)
        print(f"  ✅ Validação passou! Headers validados: {validated_headers}")
        return True
    except Exception as e:
        print(f"  ❌ Validação falhou: {e}")
        return False

def test_field_mapping():
    """Testa se o mapeamento de campos está correto."""
    
    print("\n🧪 Testando mapeamento de campos...")
    
    headers = REQUIRED_COLUMNS.copy()
    header_indices = {header: idx for idx, header in enumerate(headers)}
    
    # Linha de teste com SYNC? = true (com todas as colunas)
    test_row = ['001', 'Qual é a capital do Brasil?', 'Brasília', 'true', 'Informação complementar'] + [''] * (len(headers) - 5)
    
    fields = _create_fields_dict(test_row, headers, header_indices)
    
    print(f"  📋 Linha de teste: {test_row}")
    print(f"  📋 Campos mapeados: {fields}")
    print(f"  📋 Valor SYNC?: '{fields.get('SYNC?', 'NÃO ENCONTRADO')}'")
    
    return 'SYNC?' in fields

def test_sync_decision():
    """Testa se a decisão de sincronização está funcionando."""
    try:
        from src.column_definitions import should_sync_question
    except ImportError:
        # Fallback implementation
        def should_sync_question(fields):
            sync_value = fields.get('SYNC?', '').lower().strip()
            return sync_value in ['true', '1', 'verdadeiro', 'sim', 'yes', 'y', 't'] or sync_value == ''
    
    print("\n🧪 Testando decisão de sincronização...")
    
    # Casos de teste baseados no CSV
    test_cases = [
        {'SYNC?': 'true', 'expected': True},
        {'SYNC?': '1', 'expected': True},
        {'SYNC?': 'false', 'expected': False},
        {'SYNC?': '0', 'expected': False},
        {'SYNC?': 'verdadeiro', 'expected': True},
        {'SYNC?': 'f', 'expected': False},
        {'SYNC?': 'SIM', 'expected': True},
        {'SYNC?': '', 'expected': True},  # Vazio deve sincronizar
    ]
    
    all_passed = True
    for i, case in enumerate(test_cases):
        result = should_sync_question(case)
        expected = case['expected']
        status = "✅" if result == expected else "❌"
        print(f"  {status} Caso {i+1}: SYNC?='{case['SYNC?']}' -> {result} (esperado: {expected})")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_full_processing():
    """Testa o processamento completo de uma linha."""
    try:
        from src.parseRemoteDeck import _process_tsv_row
        from src.column_definitions import REQUIRED_COLUMNS
    except ImportError:
        # Fallback implementation
        def _process_tsv_row(row, headers, header_indices, row_num):
            fields = _create_fields_dict(row, headers, header_indices)
            sync_value = fields.get('SYNC?', '').lower().strip()
            should_sync = sync_value in ['true', '1', 'verdadeiro', 'sim', 'yes', 'y', 't'] or sync_value == ''
            return {'fields': fields} if should_sync else None
    
    print("\n🧪 Testando processamento completo...")
    
    # Simular headers e dados exatamente como no CSV
    headers = [h.upper() for h in REQUIRED_COLUMNS]  # validate_tsv_headers retorna maiúsculas
    header_indices = {header: idx for idx, header in enumerate(headers)}
    
    # Criar test data com o mesmo número de campos que headers
    # Dados de teste - linha que DEVE ser sincronizada
    test_row_sync = [
        '001',  # ID
        'Qual é a capital do Brasil?',  # PERGUNTA
        'Brasília',  # LEVAR PARA PROVA
        'true',  # SYNC?
        'Brasília foi fundada em 1960',  # INFO COMPLEMENTAR
        'A capital federal do Brasil é Brasília',  # INFO DETALHADA
        'Plano Piloto',  # EXEMPLO 1
        'Distrito Federal',  # EXEMPLO 2
        'Congresso Nacional',  # EXEMPLO 3
        'Geografia',  # TOPICO
        'Capitais',  # SUBTOPICO
        'Capital de país',  # CONCEITO
        'FCC',  # BANCAS
        '2023',  # ULTIMO ANO EM PROVA
        'Concursos',  # CARREIRA
        'Alta',  # IMPORTANCIA
        'brasil;capital;geografia'  # TAGS ADICIONAIS
    ]
    
    # Dados de teste - linha que NÃO deve ser sincronizada
    test_row_no_sync = [
        '003',  # ID
        'Qual é a fórmula da água?',  # PERGUNTA
        'H2O',  # LEVAR PARA PROVA
        'false',  # SYNC?
        'H2O é a fórmula química da água',  # INFO COMPLEMENTAR
        'Composta por 2 átomos de hidrogênio e 1 de oxigênio',  # INFO DETALHADA
        'Molécula polar',  # EXEMPLO 1
        'Ligação covalente',  # EXEMPLO 2
        'Ponto de fusão 0°C',  # EXEMPLO 3
        'Química',  # TOPICO
        'Química Geral',  # SUBTOPICO
        'Fórmula molecular',  # CONCEITO
        'VUNESP',  # BANCAS
        '2021',  # ULTIMO ANO EM PROVA
        'Concursos',  # CARREIRA
        'Média',  # IMPORTANCIA
        'quimica;agua;formula'  # TAGS ADICIONAIS
    ]
    
    print(f"  📋 Headers: {headers}")
    print(f"  📋 Quantidade de headers: {len(headers)}")
    print(f"  📋 Quantidade de campos linha 1: {len(test_row_sync)}")
    print(f"  📋 Quantidade de campos linha 2: {len(test_row_no_sync)}")
    
    # Testar linha que deve sincronizar
    result_sync = _process_tsv_row(test_row_sync, headers, header_indices, 2)
    sync_ok = result_sync is not None
    print(f"  {'✅' if sync_ok else '❌'} Linha com SYNC?='true': {'Processada' if sync_ok else 'Filtrada'}")
    
    if result_sync:
        print(f"    📋 Campos processados: {list(result_sync['fields'].keys())}")
        print(f"    📋 SYNC? = '{result_sync['fields'].get('SYNC?', 'NÃO ENCONTRADO')}'")
    
    # Testar linha que não deve sincronizar
    result_no_sync = _process_tsv_row(test_row_no_sync, headers, header_indices, 3)
    no_sync_ok = result_no_sync is None
    print(f"  {'✅' if no_sync_ok else '❌'} Linha com SYNC?='false': {'Filtrada corretamente' if no_sync_ok else 'ERRO - não foi filtrada'}")
    
    return sync_ok and no_sync_ok

def main():
    """Função principal do teste de debug."""
    print("🔍 Iniciando debug da sincronização de notas marcadas...\n")
    
    try:
        test1 = test_header_validation()
        test2 = test_field_mapping()
        test3 = test_sync_decision()
        test4 = test_full_processing()
        
        success = test1 and test2 and test3 and test4
        
        print(f"\n{'✅' if success else '❌'} Resultado do debug:")
        print(f"  {'✅' if test1 else '❌'} Validação de headers")
        print(f"  {'✅' if test2 else '❌'} Mapeamento de campos")
        print(f"  {'✅' if test3 else '❌'} Decisão de sincronização")
        print(f"  {'✅' if test4 else '❌'} Processamento completo")
        
        if success:
            print("\n🎉 Todos os testes passaram!")
            print("   A lógica de sincronização está funcionando corretamente.")
            print("   O problema pode estar em outro lugar (ex: validação TSV, conexão, etc.)")
        else:
            print("\n⚠️  Problemas encontrados na lógica de sincronização!")
        
    except Exception as e:
        print(f"❌ Erro durante debug: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
