#!/usr/bin/env python3
"""
Teste específico para verificar comportamento do código com fórmula GEMINI.
"""
import sys
import os
import re

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar funções necessárias do parseRemoteDeck
def detect_formula_content(cell_value):
    """
    Detecta se o conteúdo da célula ainda contém uma fórmula não calculada.
    Versão corrigida da função do parseRemoteDeck.py.
    """
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
        
        # Verificar padrões de fórmulas válidas PRIMEIRO (antes dos indicadores)
        # Isso permite que fórmulas legítimas sejam detectadas mesmo com palavras comuns
        valid_formula_patterns = [
            r'^=\w+\(',  # =FUNCAO(
            r'^=\w+_\w+\(',  # =FUNCAO_COMPOSTA( (ex: GEMINI_2_5_FLASH)
            r'^=\w+_\w+_\w+\(',  # =FUNCAO_COMPOSTA_LONGA( (ex: GEMINI_2_5_FLASH)
            r'^=\d+[\+\-\*\/]',  # =5+, =10*, etc.
            r'^=[A-Z]+\d+',  # =A1, =B2, etc.
            r'^=.*\([^\)]*\).*$',  # Qualquer função com parênteses
            r'^=\d+(\.\d+)?([\+\-\*\/]\d+(\.\d+)?)+$',  # Operações matemáticas: =5+3, =10*2.5
        ]
        
        # Verificar padrões válidos primeiro
        for pattern in valid_formula_patterns:
            if re.search(pattern, cell_value):
                # Se coincide com um padrão válido, verificar se não é falso positivo
                # Para fórmulas com parênteses, assumir que são válidas
                if '(' in cell_value and ')' in cell_value:
                    return True
                # Para outros padrões, continuar com verificação de indicadores
                break
        else:
            # Se não coincide com nenhum padrão válido, não é fórmula
            return False
        
        # Verificar padrões de fórmulas válidas
        formula_content = cell_value[1:]  # Remove o =
        
        # Se contém apenas espaços após =, não é fórmula
        if not formula_content.strip():
            return False
        
        # Para fórmulas com parênteses, ser menos restritivo com indicadores
        # Verificar se é uma função válida (tem parênteses balanceados)
        if '(' in cell_value and ')' in cell_value:
            # Contar parênteses para verificar se estão balanceados
            open_count = cell_value.count('(')
            close_count = cell_value.count(')')
            if open_count == close_count and open_count > 0:
                # É provável que seja uma função válida, aplicar filtros mais relaxados
                restrictive_indicators = [
                    ' não é ', ' nao é ', ' não deve ', ' nao deve ',
                    ' não pode ', ' nao pode ', ' não tem ', ' nao tem ',
                ]
                
                for indicator in restrictive_indicators:
                    if indicator in cell_value.lower():
                        return False
                
                # Se passou nos filtros restritivos, é uma fórmula
                return True
        
        # Para outros casos, aplicar filtros mais rigorosos
        non_formula_indicators = [
            ' não ', ' nao ', ' is ', ' are ', ' was ', ' were ',
            ' the ', ' and ', ' or ', ' but ', ' if ', ' when ',
            ' para ', ' com ', ' sem ', ' por ', ' em ',
            # Removido ' de ' para evitar falsos negativos
        ]
        
        for indicator in non_formula_indicators:
            if indicator in cell_value.lower():
                return False
        
        # Se passou em todos os testes, verificar novamente os padrões
        for pattern in valid_formula_patterns:
            if re.search(pattern, cell_value):
                return True
        
        return False
    
    return False

def clean_formula_errors(cell_value):
    """
    Limpa valores de erro comuns de fórmulas do Google Sheets e fórmulas não calculadas.
    Cópia da função do parseRemoteDeck.py para evitar problemas de import.
    """
    if not cell_value or not isinstance(cell_value, str):
        return cell_value

    # Lista de valores de erro comuns do Google Sheets/Excel
    formula_errors = [
        '#NAME?',    # Função ou nome não reconhecido
        '#REF!',     # Referência inválida
        '#VALUE!',   # Tipo de valor incorreto
        '#DIV/0!',   # Divisão por zero
        '#N/A',      # Valor não disponível
        '#NULL!',    # Intersecção inválida
        '#NUM!',     # Erro numérico
        '#ERROR!',   # Erro genérico
    ]
    
    cell_value_stripped = cell_value.strip()
    
    # Verificar se o valor é um erro de fórmula
    if cell_value_stripped in formula_errors:
        return ""  # Retornar string vazia para valores de erro
    
    # Verificar se começa com # (possível erro não listado)
    if cell_value_stripped.startswith('#') and cell_value_stripped.endswith('!'):
        return ""  # Tratar como erro de fórmula
    
    # Verificar se é uma fórmula não calculada
    if detect_formula_content(cell_value_stripped):
        return ""  # Tratar fórmula não calculada como vazio
    
    return cell_value

def clean_formula_errors_with_logging(cell_value, field_name="", row_num=None):
    """
    Limpa valores de erro de fórmulas com logging para debug.
    Cópia simplificada da função do parseRemoteDeck.py.
    """
    if not cell_value or not isinstance(cell_value, str):
        return cell_value
    
    original_value = cell_value
    cleaned_value = clean_formula_errors(cell_value)
    
    # Se o valor foi alterado (erro de fórmula ou fórmula detectada), registrar
    if original_value.strip() != cleaned_value:
        location_info = ""
        if field_name:
            location_info += f"campo '{field_name}'"
        if row_num:
            location_info += f" linha {row_num}" if location_info else f"linha {row_num}"
        
        # Determinar tipo de problema
        problem_type = "erro de fórmula"
        if detect_formula_content(original_value.strip()):
            problem_type = "fórmula não calculada"
        
        print(f"⚠️  {problem_type.title()} detectado e limpo: '{original_value.strip()}' → '' ({location_info})")
    
    return cleaned_value

def test_gemini_formula():
    """Testa o comportamento com a fórmula GEMINI específica do usuário."""
    
    print("🧪 Testando comportamento com fórmula GEMINI 2.5 Flash...")
    print("=" * 80)
    
    # Fórmula fornecida pelo usuário
    formula = '=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")'
    
    # Resultado da fórmula
    result = 'Imagine \'conceito 1\' como a função de busca (\'tópico 1\') em um site, onde o usuário digita algo e o sistema encontra resultados relevantes.'
    
    print(f"📝 Fórmula original:")
    print(f"   {formula}")
    print()
    
    print(f"📝 Resultado calculado:")
    print(f"   {result}")
    print()
    
    # Teste 1: Detecção de fórmula
    print("🔍 Teste 1: Detecção de fórmula...")
    is_formula = detect_formula_content(formula)
    print(f"   detect_formula_content(formula) = {is_formula}")
    
    # Teste 2: Limpeza da fórmula
    print("🧹 Teste 2: Limpeza da fórmula...")
    cleaned_formula = clean_formula_errors(formula)
    print(f"   clean_formula_errors(formula) = '{cleaned_formula}'")
    
    # Teste 3: Limpeza do resultado
    print("🧹 Teste 3: Limpeza do resultado...")
    cleaned_result = clean_formula_errors(result)
    print(f"   clean_formula_errors(result) = '{cleaned_result}'")
    
    # Teste 4: Teste com logging
    print("📊 Teste 4: Limpeza com logging...")
    print("   Fórmula:")
    cleaned_formula_log = clean_formula_errors_with_logging(formula, "EXEMPLO", 1)
    print(f"   Resultado: '{cleaned_formula_log}'")
    
    print("   Resultado:")
    cleaned_result_log = clean_formula_errors_with_logging(result, "RESPOSTA", 1)
    print(f"   Resultado: '{cleaned_result_log}'")
    
    print()
    print("=" * 80)
    print("📋 RESUMO DO COMPORTAMENTO:")
    print("=" * 80)
    
    if is_formula:
        print("✅ A fórmula seria DETECTADA como fórmula não calculada")
        print("✅ A fórmula seria REMOVIDA (substituída por string vazia)")
    else:
        print("❌ A fórmula NÃO seria detectada como fórmula")
        print("❌ A fórmula seria MANTIDA no card do Anki")
    
    if cleaned_result == result:
        print("✅ O resultado calculado seria PRESERVADO")
        print("✅ O resultado apareceria normalmente no card do Anki")
    else:
        print("❌ O resultado calculado seria REMOVIDO")
        print("❌ O resultado não apareceria no card do Anki")
    
    print()
    print("🎯 CONCLUSÃO:")
    if is_formula and cleaned_result == result:
        print("✅ COMPORTAMENTO CORRETO: Fórmula removida, resultado preservado")
    elif not is_formula and cleaned_result == result:
        print("⚠️  COMPORTAMENTO PARCIAL: Fórmula não detectada, resultado preservado")
    else:
        print("❌ COMPORTAMENTO PROBLEMÁTICO: Possível perda de dados")
    
    return is_formula, cleaned_formula, cleaned_result

if __name__ == "__main__":
    test_gemini_formula()
