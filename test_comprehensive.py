#!/usr/bin/env python3
"""
Teste abrangente para verificar se as correções não quebraram outros casos.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar a função corrigida
from parseRemoteDeck import detect_formula_content, clean_formula_errors

def test_comprehensive_formula_detection():
    """Testa vários casos de fórmulas para verificar se as correções funcionam bem."""
    
    print("🧪 TESTE ABRANGENTE DE DETECÇÃO DE FÓRMULAS")
    print("=" * 80)
    
    # Casos de teste: (input, expected_is_formula, description)
    test_cases = [
        # Casos que DEVEM ser detectados como fórmulas
        ('=GEMINI_2_5_FLASH("me de um caso de uso que explica o conceito \'" & F2 & "\' de forma didática, considerando o contexto \'" & D2 & "\'")', True, 'Fórmula GEMINI com "de" dentro'),
        ('=SUM(A1:A10)', True, 'Fórmula SUM básica'),
        ('=VLOOKUP(B2,D:E,2,FALSE)', True, 'Fórmula VLOOKUP'),
        ('=CONCATENATE("texto de exemplo", A1)', True, 'CONCATENATE com "de"'),
        ('=IF(A1>0,"Positivo de verdade","Negativo")', True, 'IF com "de"'),
        ('=PROCV(A1,"tabela de dados",2,0)', True, 'PROCV com "de"'),
        ('=CUSTOM_FUNC("valor de teste")', True, 'Função customizada com "de"'),
        ('=2+2', True, 'Operação matemática simples'),
        ('=A1*B1', True, 'Multiplicação de células'),
        ('=5+3*2', True, 'Operação matemática complexa'),
        
        # Casos que NÃO devem ser detectados como fórmulas
        ('= não é fórmula', False, 'Texto começando com ='),
        ('=', False, 'Apenas sinal de igual'),
        ('Texto normal', False, 'Texto normal'),
        ('Email: user@domain.com', False, 'Email com @'),
        ('Resultado = 10', False, 'Texto com = no meio'),
        ('= isso não é uma fórmula válida', False, 'Texto com "não é"'),
        ('= isso não pode ser fórmula', False, 'Texto com "não pode"'),
        ('= isso não deve funcionar', False, 'Texto com "não deve"'),
        ('= isso não tem sentido', False, 'Texto com "não tem"'),
        ('', False, 'String vazia'),
        ('  ', False, 'Apenas espaços'),
        ('=  ', False, 'Igual seguido de espaços'),
    ]
    
    print(f"📋 Executando {len(test_cases)} casos de teste:\n")
    
    passed = 0
    failed = 0
    
    for i, (input_val, expected, description) in enumerate(test_cases, 1):
        try:
            result = detect_formula_content(input_val)
            
            if result == expected:
                status = "✅"
                passed += 1
            else:
                status = "❌"
                failed += 1
            
            print(f"{status} Teste {i:2d}: {description}")
            print(f"    Input: {repr(input_val)}")
            print(f"    Esperado: {expected} | Obtido: {result}")
            
            if result != expected:
                print(f"    ❌ FALHA!")
            
            print()
            
        except Exception as e:
            print(f"💥 Teste {i:2d}: {description} - ERRO: {e}")
            failed += 1
            print()
    
    print("=" * 80)
    print(f"📊 RESULTADOS FINAIS:")
    print(f"✅ Passaram: {passed}")
    print(f"❌ Falharam: {failed}")
    print(f"📈 Taxa de sucesso: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("🎉 TODOS OS TESTES PASSARAM!")
        return True
    else:
        print(f"⚠️  {failed} teste(s) falharam")
        return False

def test_edge_cases():
    """Testa casos extremos e edge cases."""
    
    print("\n🔍 TESTE DE CASOS EXTREMOS")
    print("=" * 80)
    
    edge_cases = [
        # Parênteses desbalanceados
        ('=SUM(A1:A10', False, 'Parênteses não fechados'),
        ('=SUM)A1:A10)', False, 'Parênteses invertidos'),
        ('=SUM((A1:A10))', True, 'Parênteses duplos válidos'),
        
        # Casos com aspas
        ('=CONCATENATE("texto", "mais texto")', True, 'Aspas duplas válidas'),
        ('=CONCATENATE("texto não fechado', False, 'Aspas não fechadas'),
        
        # Casos mistos
        ('=VLOOKUP(A1,"tabela de referência",2,FALSE)', True, 'VLOOKUP com texto em português'),
        ('=GEMINI_AI_FUNCTION("prompt de teste")', True, 'Função AI com "de"'),
        ('=TRANSLATE("texto de origem", "pt", "en")', True, 'Função TRANSLATE'),
    ]
    
    for i, (input_val, expected, description) in enumerate(edge_cases, 1):
        try:
            result = detect_formula_content(input_val)
            status = "✅" if result == expected else "❌"
            
            print(f"{status} Edge Case {i}: {description}")
            print(f"    Input: {repr(input_val)}")
            print(f"    Esperado: {expected} | Obtido: {result}")
            print()
            
        except Exception as e:
            print(f"💥 Edge Case {i}: {description} - ERRO: {e}")
            print()

if __name__ == "__main__":
    success = test_comprehensive_formula_detection()
    test_edge_cases()
    
    if success:
        print("\n🎉 CORREÇÕES IMPLEMENTADAS COM SUCESSO!")
        print("✅ A fórmula GEMINI agora é detectada corretamente")
        print("✅ Outros casos continuam funcionando como esperado")
    else:
        print("\n⚠️  ALGUMAS CORREÇÕES PRECISAM DE AJUSTES")
