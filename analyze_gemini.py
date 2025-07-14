#!/usr/bin/env python3
"""
Análise detalhada da fórmula GEMINI para entender por que não é detectada.
"""
import re

def analyze_gemini_formula():
    """Analisa em detalhes por que a fórmula GEMINI não é detectada."""
    
    formula = '=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")'
    
    print("🔍 ANÁLISE DETALHADA DA FÓRMULA GEMINI")
    print("=" * 80)
    print(f"Fórmula: {formula}")
    print(f"Comprimento: {len(formula)}")
    print()
    
    # Verificações básicas
    print("📋 VERIFICAÇÕES BÁSICAS:")
    print(f"✓ Começa com '=': {formula.startswith('=')}")
    print(f"✓ Não é apenas '=': {formula != '='}")
    print(f"✓ Tem mais de 1 caractere: {len(formula) > 1}")
    print()
    
    # Verificar indicadores de não-fórmula
    print("🚫 VERIFICANDO INDICADORES DE NÃO-FÓRMULA:")
    non_formula_indicators = [
        ' não ', ' nao ', ' is ', ' are ', ' was ', ' were ',
        ' the ', ' and ', ' or ', ' but ', ' if ', ' when ',
        ' para ', ' com ', ' sem ', ' por ', ' em ', ' de ',
    ]
    
    found_indicators = []
    for indicator in non_formula_indicators:
        if indicator in formula.lower():
            found_indicators.append(indicator)
    
    if found_indicators:
        print(f"❌ Encontrados indicadores de não-fórmula: {found_indicators}")
        print("   Isso faz com que a fórmula seja considerada como texto comum!")
    else:
        print("✅ Nenhum indicador de não-fórmula encontrado")
    
    print()
    
    # Verificar padrões de fórmulas válidas
    print("🔍 VERIFICANDO PADRÕES DE FÓRMULAS VÁLIDAS:")
    valid_formula_patterns = [
        (r'^=\w+\(', '=FUNCAO('),
        (r'^=\d+[\+\-\*\/]', '=5+, =10*, etc.'),
        (r'^=[A-Z]+\d+', '=A1, =B2, etc.'),
        (r'^=.*\([^\)]*\).*$', 'Qualquer função com parênteses'),
        (r'^=\d+(\.\d+)?([\+\-\*\/]\d+(\.\d+)?)+$', 'Operações matemáticas'),
    ]
    
    matches = []
    for pattern, description in valid_formula_patterns:
        if re.search(pattern, formula):
            matches.append((pattern, description))
    
    if matches:
        print("✅ Padrões que coincidem:")
        for pattern, description in matches:
            print(f"   - {description}: {pattern}")
    else:
        print("❌ Nenhum padrão de fórmula válida encontrado")
    
    print()
    
    # Simulação do algoritmo
    print("🤖 SIMULAÇÃO DO ALGORITMO:")
    print("1. Fórmula começa com '='? SIM")
    print("2. Tem mais de 1 caractere? SIM")
    print("3. Conteúdo após '=' não é só espaços? SIM")
    
    if found_indicators:
        print(f"4. Contém indicadores de não-fórmula? SIM → {found_indicators}")
        print("   RESULTADO: FALSE (não é fórmula)")
        return False
    else:
        print("4. Contém indicadores de não-fórmula? NÃO")
        if matches:
            print("5. Coincide com padrões válidos? SIM")
            print("   RESULTADO: TRUE (é fórmula)")
            return True
        else:
            print("5. Coincide com padrões válidos? NÃO")
            print("   RESULTADO: FALSE (não é fórmula)")
            return False

def test_fix():
    """Testa possíveis correções para detectar a fórmula GEMINI."""
    
    formula = '=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")'
    
    print("\n🔧 TESTANDO POSSÍVEIS CORREÇÕES:")
    print("=" * 80)
    
    # Correção 1: Remover ' de ' da lista de indicadores
    print("💡 CORREÇÃO 1: Remover ' de ' da lista de indicadores")
    non_formula_indicators_fixed = [
        ' não ', ' nao ', ' is ', ' are ', ' was ', ' were ',
        ' the ', ' and ', ' or ', ' but ', ' if ', ' when ',
        ' para ', ' com ', ' sem ', ' por ', ' em ',
        # Removido: ' de '
    ]
    
    found_indicators_fixed = []
    for indicator in non_formula_indicators_fixed:
        if indicator in formula.lower():
            found_indicators_fixed.append(indicator)
    
    if found_indicators_fixed:
        print(f"   Ainda encontra indicadores: {found_indicators_fixed}")
        print("   Resultado: FALSE (não é fórmula)")
    else:
        print("   Nenhum indicador encontrado!")
        
        # Verificar se agora coincide com padrões válidos
        valid_formula_patterns = [
            r'^=\w+\(',  # =FUNCAO(
            r'^=\d+[\+\-\*\/]',  # =5+, =10*, etc.
            r'^=[A-Z]+\d+',  # =A1, =B2, etc.
            r'^=.*\([^\)]*\).*$',  # Qualquer função com parênteses
            r'^=\d+(\.\d+)?([\+\-\*\/]\d+(\.\d+)?)+$',  # Operações matemáticas
        ]
        
        matches = []
        for pattern in valid_formula_patterns:
            if re.search(pattern, formula):
                matches.append(pattern)
        
        if matches:
            print(f"   Coincide com padrões: {matches}")
            print("   Resultado: TRUE (é fórmula) ✅")
        else:
            print("   Não coincide com padrões válidos")
            print("   Resultado: FALSE (não é fórmula)")
    
    print()
    
    # Correção 2: Adicionar padrão específico para GEMINI
    print("💡 CORREÇÃO 2: Adicionar padrão específico para funções do Google Sheets")
    gemini_pattern = r'^=\w+_\w+_\w+\('  # =PALAVRA_PALAVRA_PALAVRA(
    
    if re.search(gemini_pattern, formula):
        print(f"   Padrão GEMINI coincide: {gemini_pattern}")
        print("   Resultado: TRUE (é fórmula) ✅")
    else:
        print(f"   Padrão GEMINI não coincide: {gemini_pattern}")
        print("   Resultado: FALSE (não é fórmula)")

if __name__ == "__main__":
    is_formula = analyze_gemini_formula()
    test_fix()
