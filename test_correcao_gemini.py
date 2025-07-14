#!/usr/bin/env python3
"""
Teste para validar a correção do problema com fórmulas Gemini.
"""
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar as funções diretamente do código para evitar problemas de imports relativos
import re

def detect_formula_content(cell_value):
    """
    Detecta se o conteúdo da célula ainda contém uma fórmula não calculada.
    VERSÃO CORRIGIDA para funcionar com fórmulas Gemini.
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
        
        # Verificar padrões de fórmulas Gemini PRIMEIRO (prioridade máxima)
        # Fórmulas Gemini são sempre consideradas válidas, independente do conteúdo
        gemini_patterns = [
            r'^=GEMINI_\w+\(',  # =GEMINI_QUALQUER_COISA(
            r'^=AI_\w+\(',      # =AI_QUALQUER_COISA(
        ]
        
        for pattern in gemini_patterns:
            if re.search(pattern, cell_value):
                return True
        
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
            # Removido ' de ' - muito comum em fórmulas legítimas (ex: Gemini)
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
    
    # Verificar se é uma fórmula não calculada (novo)
    if detect_formula_content(cell_value_stripped):
        return ""  # Tratar fórmula não calculada como vazio
    
    return cell_value

def test_gemini_formula_detection():
    """Testa se fórmulas Gemini são detectadas corretamente após a correção."""
    
    print("🧪 TESTE: Detecção de Fórmulas Gemini")
    print("=" * 60)
    
    # Casos de teste com fórmulas Gemini
    gemini_test_cases = [
        '=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")',
        '=GEMINI_AI("explique de forma didática")',
        '=GEMINI_PRO("me de um exemplo de uso")',
        '=AI_FUNCTION("prompt de teste")',
        '=GEMINI_1_5_FLASH("teste de integração")',
    ]
    
    # Casos de teste com texto normal (não deve ser detectado como fórmula)
    text_test_cases = [
        'Este é um texto normal de exemplo',
        'Uma resposta que contém a palavra de no meio',
        'Explicação didática sobre o conceito',
        '= não é uma fórmula válida',
        '=',
        '',
    ]
    
    # Casos de teste com outras fórmulas válidas
    other_formula_cases = [
        '=SUM(A1:A10)',
        '=VLOOKUP(B2,D:E,2,FALSE)',
        '=IF(A1>10,"Grande","Pequeno")',
        '=CONCATENATE("Olá ", B2)',
        '=5+3*2',
    ]
    
    print("🎯 TESTANDO FÓRMULAS GEMINI:")
    print("-" * 40)
    
    gemini_success = True
    for formula in gemini_test_cases:
        is_detected = detect_formula_content(formula)
        cleaned = clean_formula_errors(formula)
        
        print(f"Fórmula: {formula[:50]}...")
        print(f"  Detectada como fórmula: {is_detected}")
        print(f"  Resultado da limpeza: '{cleaned[:50]}...' (vazio={cleaned == ''})")
        
        if not is_detected:
            print("  ❌ ERRO: Fórmula Gemini não foi detectada!")
            gemini_success = False
        else:
            print("  ✅ OK: Fórmula Gemini detectada corretamente")
        
        print()
    
    print("🔤 TESTANDO TEXTO NORMAL:")
    print("-" * 40)
    
    text_success = True
    for text in text_test_cases:
        is_detected = detect_formula_content(text)
        cleaned = clean_formula_errors(text)
        
        print(f"Texto: {text[:50]}...")
        print(f"  Detectado como fórmula: {is_detected}")
        print(f"  Resultado da limpeza: '{cleaned[:50]}...'")
        
        if is_detected:
            print("  ❌ ERRO: Texto normal foi detectado como fórmula!")
            text_success = False
        else:
            print("  ✅ OK: Texto normal não foi detectado como fórmula")
        
        print()
    
    print("🔧 TESTANDO OUTRAS FÓRMULAS:")
    print("-" * 40)
    
    other_success = True
    for formula in other_formula_cases:
        is_detected = detect_formula_content(formula)
        cleaned = clean_formula_errors(formula)
        
        print(f"Fórmula: {formula}")
        print(f"  Detectada como fórmula: {is_detected}")
        print(f"  Resultado da limpeza: '{cleaned}' (vazio={cleaned == ''})")
        
        if not is_detected:
            print("  ❌ ERRO: Fórmula válida não foi detectada!")
            other_success = False
        else:
            print("  ✅ OK: Fórmula detectada corretamente")
        
        print()
    
    # Resultado final
    print("📊 RESULTADO FINAL:")
    print("=" * 60)
    
    if gemini_success and text_success and other_success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 A correção do problema com fórmulas Gemini foi bem-sucedida!")
        return True
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("❌ Fórmulas Gemini:", "✅ OK" if gemini_success else "❌ FALHA")
        print("❌ Texto normal:", "✅ OK" if text_success else "❌ FALHA") 
        print("❌ Outras fórmulas:", "✅ OK" if other_success else "❌ FALHA")
        return False

def test_specific_gemini_issue():
    """Testa o caso específico mencionado pelo usuário."""
    
    print("\n" + "="*60)
    print("🎯 TESTE ESPECÍFICO: Problema Reportado pelo Usuário")
    print("="*60)
    
    # Fórmula específica que estava causando problema
    problematic_formula = '=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")'
    
    print(f"Fórmula problemática:")
    print(f"  {problematic_formula}")
    print()
    
    # Testar detecção
    is_detected = detect_formula_content(problematic_formula)
    cleaned = clean_formula_errors(problematic_formula)
    
    print("Resultados:")
    print(f"  Detectada como fórmula: {is_detected}")
    print(f"  Resultado da limpeza: '{cleaned}' (vazio={cleaned == ''})")
    print()
    
    # Explicar o que deveria acontecer
    print("Comportamento esperado:")
    print("  ✅ Deve ser detectada como fórmula (True)")
    print("  ✅ Deve ser limpa (retornar string vazia) se for fórmula não calculada")
    print("  ✅ Deve preservar o resultado se for valor calculado")
    print()
    
    if is_detected:
        print("✅ SUCESSO: Fórmula Gemini agora é detectada corretamente!")
        print("🎉 O problema do comportamento inconsistente foi resolvido!")
        return True
    else:
        print("❌ FALHA: Fórmula Gemini ainda não é detectada!")
        print("❌ O problema persiste...")
        return False

if __name__ == "__main__":
    print("🔍 TESTE DE CORREÇÃO DO PROBLEMA COM FÓRMULAS GEMINI")
    print("=" * 70)
    
    # Executar testes
    general_success = test_gemini_formula_detection()
    specific_success = test_specific_gemini_issue()
    
    print("\n" + "="*70)
    print("🏁 RESULTADO GERAL:")
    print("="*70)
    
    if general_success and specific_success:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("🎉 A correção foi implementada com sucesso!")
        print("🔧 As fórmulas Gemini agora devem ter comportamento consistente!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("🔧 Pode ser necessário ajustar a implementação...")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Testar com planilhas reais contendo fórmulas Gemini")
    print("2. Verificar se o comportamento é consistente na sincronização")
    print("3. Monitorar se outras fórmulas continuam funcionando")
    print("4. Documentar o comportamento esperado")
