#!/usr/bin/env python3
"""
Teste para validar limpeza de erros de fórmulas do Google Sheets.

Este script testa a função clean_formula_errors para garantir que
valores de erro como #NAME?, #REF!, etc. sejam tratados corretamente.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Agora importar diretamente
import parseRemoteDeck

def test_clean_formula_errors():
    """Testa a função clean_formula_errors com diversos valores."""
    
    print("🧪 Testando função clean_formula_errors()...")
    
    # Casos de teste: (input, expected_output, description)
    test_cases = [
        ('#NAME?', '', 'Erro de nome de função'),
        ('#REF!', '', 'Erro de referência'),
        ('#VALUE!', '', 'Erro de valor'),
        ('#DIV/0!', '', 'Erro de divisão por zero'),
        ('#N/A', '', 'Valor não disponível'),
        ('#NULL!', '', 'Intersecção inválida'),
        ('#NUM!', '', 'Erro numérico'),
        ('#ERROR!', '', 'Erro genérico'),
        ('  #NAME?  ', '', 'Erro com espaços em branco'),
        ('Conteúdo normal', 'Conteúdo normal', 'Conteúdo válido'),
        ('Questão válida', 'Questão válida', 'Texto normal'),
        ('', '', 'String vazia'),
        ('   ', '   ', 'Apenas espaços'),
        ('123', '123', 'Número como string'),
        ('#CUSTOM!', '', 'Erro customizado (padrão #...!)'),
        ('texto#normal', 'texto#normal', 'Texto com # no meio'),
        ('#', '#', 'Apenas # (não é erro)'),
        ('#texto', '#texto', 'Texto iniciando com # (não é erro)'),
        (None, None, 'Valor None'),
    ]
    
    print(f"\n📋 Executando {len(test_cases)} casos de teste:\n")
    
    passed = 0
    failed = 0
    
    for i, (input_val, expected, description) in enumerate(test_cases, 1):
        try:
            result = parseRemoteDeck.clean_formula_errors(input_val)
            if result == expected:
                print(f"✅ Teste {i:2d}: {description}")
                print(f"    Input: {repr(input_val)} → Output: {repr(result)}")
                passed += 1
            else:
                print(f"❌ Teste {i:2d}: {description}")
                print(f"    Input: {repr(input_val)}")
                print(f"    Esperado: {repr(expected)}")
                print(f"    Obtido: {repr(result)}")
                failed += 1
        except Exception as e:
            print(f"💥 Teste {i:2d}: {description} - ERRO: {e}")
            failed += 1
        
        print()
    
    print(f"📊 Resultados: {passed} passou(ram), {failed} falhou(ram)")
    
    if failed == 0:
        print("🎉 Todos os testes passaram!")
        return True
    else:
        print(f"⚠️  {failed} teste(s) falharam")
        return False

def test_integration_example():
    """Testa um exemplo de integração completa."""
    
    print("🔄 Testando integração com dados de exemplo...")
    
    # Simular dados TSV com erros de fórmula
    sample_row = [
        '1',                    # ID
        'Qual é a resposta?',   # PERGUNTA
        '#NAME?',               # LEVAR PARA PROVA (erro de fórmula)
        'true',                 # SYNC?
        'Informação válida',    # INFO COMPLEMENTAR
        '#REF!',                # INFO DETALHADA (erro de fórmula)
        'Exemplo 1',            # EXEMPLO 1
        '#VALUE!',              # EXEMPLO 2 (erro de fórmula)
    ]
    
    headers = ['ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'SYNC?', 
               'INFO COMPLEMENTAR', 'INFO DETALHADA', 'EXEMPLO 1', 'EXEMPLO 2']
    
    # Simular criação de fields dict
    fields = {}
    for i, header in enumerate(headers):
        if i < len(sample_row):
            raw_value = sample_row[i].strip()
            cleaned_value = parseRemoteDeck.clean_formula_errors(raw_value)
            fields[header] = cleaned_value
        else:
            fields[header] = ""
    
    print("\n📋 Dados originais:")
    for i, (header, raw_val) in enumerate(zip(headers, sample_row)):
        print(f"  {header}: {repr(raw_val)}")
    
    print("\n✨ Dados após limpeza:")
    for header in headers:
        print(f"  {header}: {repr(fields[header])}")
    
    # Verificar se os erros foram limpos
    expected_clean = {
        'ID': '1',
        'PERGUNTA': 'Qual é a resposta?',
        'LEVAR PARA PROVA': '',  # Limpo de #NAME?
        'SYNC?': 'true',
        'INFO COMPLEMENTAR': 'Informação válida',
        'INFO DETALHADA': '',    # Limpo de #REF!
        'EXEMPLO 1': 'Exemplo 1',
        'EXEMPLO 2': '',         # Limpo de #VALUE!
    }
    
    success = True
    for header, expected_val in expected_clean.items():
        if fields[header] != expected_val:
            print(f"❌ Erro no campo {header}: esperado {repr(expected_val)}, obtido {repr(fields[header])}")
            success = False
    
    if success:
        print("\n🎉 Integração funcionando corretamente!")
        return True
    else:
        print("\n⚠️  Problemas na integração detectados")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTES DE LIMPEZA DE ERROS DE FÓRMULAS")
    print("=" * 60)
    
    test1_result = test_clean_formula_errors()
    print("\n" + "=" * 60)
    test2_result = test_integration_example()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        sys.exit(1)
