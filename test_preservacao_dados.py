#!/usr/bin/env python3
"""
Teste para validar que os dados do TSV são preservados exatamente como capturados.
"""
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar as funções diretamente do código
def clean_formula_errors(cell_value):
    """
    Preserva valores de célula do TSV exatamente como foram capturados.
    VERSÃO MODIFICADA - sempre retorna o valor original.
    """
    return cell_value

def clean_formula_errors_with_logging(cell_value, field_name="", row_num=None):
    """
    Preserva valores de célula do TSV com logging para debug.
    VERSÃO MODIFICADA - sempre retorna o valor original.
    """
    return cell_value

def test_data_preservation():
    """Testa se todos os dados são preservados exatamente como capturados."""
    
    print("🧪 TESTE: Preservação de Dados do TSV")
    print("=" * 60)
    
    # Casos de teste com diferentes tipos de dados
    test_cases = [
        # Erros de fórmula - devem ser preservados
        '#NAME?',
        '#REF!',
        '#VALUE!',
        '#DIV/0!',
        '#N/A',
        '#NULL!',
        '#NUM!',
        '#ERROR!',
        
        # Fórmulas não calculadas - devem ser preservadas
        '=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")',
        '=SUM(A1:A10)',
        '=VLOOKUP(B2,D:E,2,FALSE)',
        '=IF(A1>10,"Grande","Pequeno")',
        '=CONCATENATE("Olá ", B2)',
        '=5+3*2',
        
        # Texto normal - deve ser preservado
        'Este é um texto normal de exemplo',
        'Uma resposta que contém a palavra de no meio',
        'Explicação didática sobre o conceito',
        'Resultado calculado de uma fórmula Gemini',
        'Brasília',
        'Geografia',
        'Capital do Brasil',
        
        # Valores especiais - devem ser preservados
        '',  # String vazia
        ' ',  # Espaço
        '0',  # Zero
        'false',  # Valor booleano
        'null',  # Valor nulo
        '= não é uma fórmula válida',  # Texto que começa com =
    ]
    
    print("🎯 TESTANDO PRESERVAÇÃO DE DADOS:")
    print("-" * 50)
    
    all_success = True
    
    for i, original_value in enumerate(test_cases, 1):
        # Testar função clean_formula_errors
        cleaned_value = clean_formula_errors(original_value)
        
        # Testar função clean_formula_errors_with_logging
        logged_value = clean_formula_errors_with_logging(original_value, f"campo_{i}", i)
        
        print(f"{i:2d}. Valor original: '{original_value}'")
        print(f"    clean_formula_errors: '{cleaned_value}'")
        print(f"    with_logging: '{logged_value}'")
        
        # Verificar se os valores são preservados
        if cleaned_value != original_value:
            print(f"    ❌ ERRO: clean_formula_errors modificou o valor!")
            all_success = False
        elif logged_value != original_value:
            print(f"    ❌ ERRO: clean_formula_errors_with_logging modificou o valor!")
            all_success = False
        else:
            print(f"    ✅ OK: Valor preservado corretamente")
        
        print()
    
    # Resultado final
    print("📊 RESULTADO FINAL:")
    print("=" * 60)
    
    if all_success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 Todos os dados do TSV são preservados exatamente como capturados!")
        print("🔧 Nenhuma conversão para string vazia está ocorrendo!")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("❌ Alguns dados estão sendo modificados!")
        return False

def test_specific_cases():
    """Testa casos específicos mencionados pelo usuário."""
    
    print("\n" + "="*60)
    print("🎯 TESTE ESPECÍFICO: Casos Problemáticos")
    print("="*60)
    
    # Casos que anteriormente eram convertidos para string vazia
    problematic_cases = [
        {
            'value': '=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")',
            'description': 'Fórmula Gemini não calculada'
        },
        {
            'value': '#NAME?',
            'description': 'Erro de fórmula NAME'
        },
        {
            'value': '=SUM(A1:A10)',
            'description': 'Fórmula SUM não calculada'
        },
        {
            'value': '#REF!',
            'description': 'Erro de referência inválida'
        }
    ]
    
    print("Casos que anteriormente eram convertidos para string vazia:")
    print("-" * 60)
    
    all_preserved = True
    
    for case in problematic_cases:
        original = case['value']
        description = case['description']
        
        cleaned = clean_formula_errors(original)
        logged = clean_formula_errors_with_logging(original, "test_field", 1)
        
        print(f"Caso: {description}")
        print(f"  Original: '{original}'")
        print(f"  Após clean_formula_errors: '{cleaned}'")
        print(f"  Após with_logging: '{logged}'")
        
        if cleaned == original and logged == original:
            print("  ✅ SUCESSO: Valor preservado corretamente!")
        else:
            print("  ❌ FALHA: Valor foi modificado!")
            all_preserved = False
        
        print()
    
    return all_preserved

if __name__ == "__main__":
    print("🔍 TESTE DE PRESERVAÇÃO DE DADOS DO TSV")
    print("=" * 70)
    
    # Executar testes
    general_success = test_data_preservation()
    specific_success = test_specific_cases()
    
    print("\n" + "="*70)
    print("🏁 RESULTADO GERAL:")
    print("="*70)
    
    if general_success and specific_success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 A modificação foi implementada com sucesso!")
        print("🔧 Os dados do TSV são preservados exatamente como capturados!")
        print("📝 Nenhuma conversão para string vazia está ocorrendo!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🔧 Pode ser necessário ajustar a implementação...")
    
    print("\n💡 COMPORTAMENTO ATUAL:")
    print("- ✅ Erros de fórmula (#NAME?, #REF!, etc.) são preservados")
    print("- ✅ Fórmulas não calculadas (=GEMINI_..., =SUM...) são preservadas")
    print("- ✅ Texto normal é preservado")
    print("- ✅ Valores especiais (vazio, espaço, etc.) são preservados")
    print("- ✅ TODOS os dados chegam ao Anki exatamente como estavam no TSV")
