#!/usr/bin/env python3
"""
Teste para validar a detecção de fórmulas não calculadas e modificação de URLs.
"""

import re
from urllib.parse import urlparse, parse_qs

def ensure_values_only_url(url):
    """Cópia da função para teste standalone."""
    # Se não é URL do Google Sheets, retornar como está
    if 'docs.google.com/spreadsheets' not in url:
        return url
    
    # Extrair ID da planilha
    spreadsheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if not spreadsheet_id_match:
        return url
    
    spreadsheet_id = spreadsheet_id_match.group(1)
    
    # Extrair GID se presente
    gid = "0"  # Padrão
    
    # Tentar extrair GID do fragmento (#gid=123)
    if '#gid=' in url:
        gid_match = re.search(r'#gid=(\d+)', url)
        if gid_match:
            gid = gid_match.group(1)
    
    # Tentar extrair GID dos parâmetros (?gid=123)
    elif '?gid=' in url or '&gid=' in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'gid' in params:
            gid = params['gid'][0]
    
    # Construir URL de export que garante valores calculados
    export_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export"
    export_url += f"?format=tsv&exportFormat=tsv&gid={gid}"
    
    return export_url

def detect_formula_content(cell_value):
    """Cópia melhorada da função para teste standalone."""
    if not cell_value or not isinstance(cell_value, str):
        return False
    
    cell_value = cell_value.strip()
    
    # Verificar se é apenas o sinal de igual
    if cell_value == '=':
        return False
    
    # Verificar se começa com = mas não é uma fórmula válida
    if cell_value.startswith('='):
        # Deve ter pelo menos um caractere após o =
        if len(cell_value) <= 1:
            return False
        
        # Verificar padrões de fórmulas válidas
        formula_content = cell_value[1:]  # Remove o =
        
        # Se contém apenas espaços após =, não é fórmula
        if not formula_content.strip():
            return False
        
        # Se contém palavras comuns que indicam que não é fórmula
        non_formula_indicators = [
            ' não ', ' nao ', ' is ', ' are ', ' was ', ' were ',
            ' the ', ' and ', ' or ', ' but ', ' if ', ' when ',
            ' para ', ' com ', ' sem ', ' por ', ' em ', ' de ',
        ]
        
        for indicator in non_formula_indicators:
            if indicator in cell_value.lower():
                return False
        
        # Verificar padrões comuns de fórmulas válidas
        valid_formula_patterns = [
            r'^=\w+\(',  # =FUNCAO(
            r'^=\d+[\+\-\*\/]',  # =5+, =10*, etc.
            r'^=[A-Z]+\d+',  # =A1, =B2, etc.
            r'^=.*\([^\)]*\).*$',  # Qualquer função com parênteses
            r'^=\d+(\.\d+)?([\+\-\*\/]\d+(\.\d+)?)+$',  # Operações matemáticas: =5+3, =10*2.5
        ]
        
        for pattern in valid_formula_patterns:
            if re.search(pattern, cell_value):
                return True
        
        return False
    
    return False

def test_url_modification():
    """Testa a modificação de URLs para garantir valores calculados."""
    
    print("🧪 Testando modificação de URLs...")
    
    test_cases = [
        # (input_url, expected_contains, description)
        (
            "https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit#gid=0",
            "/export?format=tsv&exportFormat=tsv&gid=0",
            "URL básica com edit#gid=0"
        ),
        (
            "https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit#gid=123456",
            "/export?format=tsv&exportFormat=tsv&gid=123456",
            "URL com GID específico"
        ),
        (
            "https://docs.google.com/spreadsheets/d/1ABC123DEF456/export?format=tsv&gid=0",
            "/export?format=tsv&exportFormat=tsv&gid=0",
            "URL já é de export"
        ),
        (
            "https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit",
            "/export?format=tsv&exportFormat=tsv&gid=0",
            "URL sem GID (usar padrão 0)"
        ),
        (
            "https://example.com/not-google-sheets.csv",
            "https://example.com/not-google-sheets.csv",
            "URL não-Google Sheets (manter inalterada)"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_url, expected_contains, description) in enumerate(test_cases, 1):
        try:
            result = ensure_values_only_url(input_url)
            
            if isinstance(expected_contains, str) and expected_contains in result:
                print(f"✅ Teste {i}: {description}")
                print(f"    Input: {input_url}")
                print(f"    Output: {result}")
                passed += 1
            elif expected_contains == result:
                print(f"✅ Teste {i}: {description}")
                print(f"    Input: {input_url}")
                print(f"    Output: {result}")
                passed += 1
            else:
                print(f"❌ Teste {i}: {description}")
                print(f"    Input: {input_url}")
                print(f"    Esperado conter: {expected_contains}")
                print(f"    Obtido: {result}")
                failed += 1
        except Exception as e:
            print(f"💥 Teste {i}: {description} - ERRO: {e}")
            failed += 1
        
        print()
    
    print(f"📊 Resultados: {passed} passou(ram), {failed} falhou(ram)")
    return failed == 0

def test_formula_detection():
    """Testa a detecção de fórmulas não calculadas."""
    
    print("🧪 Testando detecção de fórmulas...")
    
    test_cases = [
        # (input, expected, description)
        ('=SUM(A1:A10)', True, 'Fórmula SUM básica'),
        ('=VLOOKUP(B2,D:E,2,FALSE)', True, 'Fórmula VLOOKUP complexa'),
        ('=5+3', True, 'Operação matemática simples'),
        ('=A1*B1', True, 'Multiplicação de células'),
        ('=IF(A1>0,"Positivo","Negativo")', True, 'Fórmula IF com strings'),
        ('=CONCATENATE(A1,B1)', True, 'Função CONCATENATE'),
        ('Texto normal', False, 'Texto normal'),
        ('123', False, 'Número como string'),
        ('Total: 150', False, 'Texto com número'),
        ('= não é fórmula', False, 'Texto começando com ='),
        ('Email: user@domain.com', False, 'Email com @'),
        ('', False, 'String vazia'),
        ('  =SUM(A1:A10)  ', True, 'Fórmula com espaços'),
        ('=', False, 'Apenas sinal de igual'),
        ('Resultado = 10', False, 'Texto com = no meio'),
    ]
    
    passed = 0
    failed = 0
    
    for i, (input_val, expected, description) in enumerate(test_cases, 1):
        try:
            result = detect_formula_content(input_val)
            
            if result == expected:
                print(f"✅ Teste {i}: {description}")
                print(f"    Input: {repr(input_val)} → Output: {result}")
                passed += 1
            else:
                print(f"❌ Teste {i}: {description}")
                print(f"    Input: {repr(input_val)}")
                print(f"    Esperado: {expected}")
                print(f"    Obtido: {result}")
                failed += 1
        except Exception as e:
            print(f"💥 Teste {i}: {description} - ERRO: {e}")
            failed += 1
        
        print()
    
    print(f"📊 Resultados: {passed} passou(ram), {failed} falhou(ram)")
    return failed == 0

def test_integration_example():
    """Testa um exemplo de integração com fórmulas."""
    
    print("🔄 Testando integração com fórmulas não calculadas...")
    
    # Simular dados TSV com fórmulas
    sample_data = [
        ['ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'SYNC?'],
        ['1', 'Quanto é 2+2?', '=2+2', 'true'],
        ['2', 'Qual é a soma?', '=SUM(A1:A5)', 'true'],
        ['3', 'Texto normal', 'Resposta normal', 'true'],
        ['4', 'Erro de fórmula', '#NAME?', 'true'],
        ['5', 'Busca', '=VLOOKUP(A1,B:C,2,FALSE)', 'false'],
    ]
    
    # Simular limpeza
    def clean_cell(value):
        # Aplicar as regras de limpeza
        if not value or not isinstance(value, str):
            return value
        
        # Erros de fórmula
        formula_errors = ['#NAME?', '#REF!', '#VALUE!', '#DIV/0!', '#N/A', '#NULL!', '#NUM!', '#ERROR!']
        if value.strip() in formula_errors:
            return ""
        
        # Fórmulas não calculadas
        if detect_formula_content(value):
            return ""
        
        return value
    
    print("📋 Dados originais:")
    for i, row in enumerate(sample_data):
        print(f"  Linha {i}: {row}")
    
    print("\n✨ Dados após limpeza:")
    cleaned_data = []
    for i, row in enumerate(sample_data):
        if i == 0:  # Header
            cleaned_row = row
        else:
            cleaned_row = [clean_cell(cell) for cell in row]
        cleaned_data.append(cleaned_row)
        print(f"  Linha {i}: {cleaned_row}")
    
    # Verificar resultados esperados
    expected_results = {
        1: ['1', 'Quanto é 2+2?', '', 'true'],  # =2+2 → ''
        2: ['2', 'Qual é a soma?', '', 'true'],  # =SUM → ''
        3: ['3', 'Texto normal', 'Resposta normal', 'true'],  # Inalterado
        4: ['4', 'Erro de fórmula', '', 'true'],  # #NAME? → ''
        5: ['5', 'Busca', '', 'false'],  # =VLOOKUP → ''
    }
    
    success = True
    for row_idx, expected_row in expected_results.items():
        actual_row = cleaned_data[row_idx]
        if actual_row != expected_row:
            print(f"❌ Erro na linha {row_idx}:")
            print(f"  Esperado: {expected_row}")
            print(f"  Obtido: {actual_row}")
            success = False
    
    if success:
        print("\n🎉 Integração funcionando corretamente!")
        return True
    else:
        print("\n⚠️  Problemas na integração detectados")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTES DE DETECÇÃO DE FÓRMULAS E MODIFICAÇÃO DE URL")
    print("=" * 70)
    
    test1_result = test_url_modification()
    print("\n" + "=" * 70)
    test2_result = test_formula_detection()
    print("\n" + "=" * 70)
    test3_result = test_integration_example()
    
    print("\n" + "=" * 70)
    if test1_result and test2_result and test3_result:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
