#!/usr/bin/env python3
"""
Teste específico para validar que a coluna SYNC? é case insensitive.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_case_insensitive():
    """Testa especificamente se a coluna SYNC? é case insensitive."""
    from column_definitions import should_sync_question, SYNC
    
    print("🧪 Testando se SYNC? é case insensitive...")
    
    # Testes de valores positivos em diferentes cases
    positive_tests = [
        # Valores básicos
        ('true', True), ('TRUE', True), ('True', True), ('tRuE', True),
        ('1', True),
        ('sim', True), ('SIM', True), ('Sim', True), ('sIm', True),
        ('yes', True), ('YES', True), ('Yes', True), ('yEs', True),
        ('verdadeiro', True), ('VERDADEIRO', True), ('Verdadeiro', True), ('vErDaDeIrO', True),
        ('v', True), ('V', True),
    ]
    
    # Testes de valores negativos em diferentes cases
    negative_tests = [
        # Valores básicos
        ('false', False), ('FALSE', False), ('False', False), ('fAlSe', False),
        ('0', False),
        ('não', False), ('NÃO', False), ('Não', False), ('nÃo', False),
        ('nao', False), ('NAO', False), ('Nao', False), ('nAo', False),
        ('no', False), ('NO', False), ('No', False), ('nO', False),
        ('falso', False), ('FALSO', False), ('Falso', False), ('fAlSo', False),
        ('f', False), ('F', False),
    ]
    
    # Testar valores positivos
    print("\n  📋 Testando valores positivos (devem sincronizar):")
    all_positive_passed = True
    for value, expected in positive_tests:
        fields = {SYNC: value}
        result = should_sync_question(fields)
        status = "✅" if result == expected else "❌"
        print(f"    {status} SYNC?='{value}' -> {result} (esperado: {expected})")
        if result != expected:
            all_positive_passed = False
    
    # Testar valores negativos
    print("\n  📋 Testando valores negativos (não devem sincronizar):")
    all_negative_passed = True
    for value, expected in negative_tests:
        fields = {SYNC: value}
        result = should_sync_question(fields)
        status = "✅" if result == expected else "❌"
        print(f"    {status} SYNC?='{value}' -> {result} (esperado: {expected})")
        if result != expected:
            all_negative_passed = False
    
    # Testar valores com espaços
    print("\n  📋 Testando valores com espaços (devem ser tratados):")
    space_tests = [
        (' true ', True), ('  TRUE  ', True), ('\ttrue\t', True),
        (' false ', False), ('  FALSE  ', False), ('\tfalse\t', False),
        (' 1 ', True), ('  0  ', False),
        (' sim ', True), ('  não  ', False),
    ]
    
    all_space_passed = True
    for value, expected in space_tests:
        fields = {SYNC: value}
        result = should_sync_question(fields)
        status = "✅" if result == expected else "❌"
        print(f"    {status} SYNC?='{repr(value)}' -> {result} (esperado: {expected})")
        if result != expected:
            all_space_passed = False
    
    # Resumo
    all_passed = all_positive_passed and all_negative_passed and all_space_passed
    
    print(f"\n  📊 Resultados:")
    print(f"    {'✅' if all_positive_passed else '❌'} Valores positivos: {len(positive_tests)} testes")
    print(f"    {'✅' if all_negative_passed else '❌'} Valores negativos: {len(negative_tests)} testes")
    print(f"    {'✅' if all_space_passed else '❌'} Valores com espaços: {len(space_tests)} testes")
    
    return all_passed

def test_example_csv_values():
    """Testa os valores específicos do exemplo CSV."""
    from column_definitions import should_sync_question, SYNC
    
    print("\n🧪 Testando valores do exemplo CSV...")
    
    # Valores do exemplo CSV atual
    csv_values = [
        ('true', True),       # Linha 001
        ('1', True),          # Linha 002  
        ('false', False),     # Linha 003
        ('0', False),         # Linha 004
        ('verdadeiro', True), # Linha 005
        ('f', False),         # Linha 006
        ('SIM', True),        # Linha 007
        ('', True),           # Linha 008 (vazio = sincronizar)
    ]
    
    all_passed = True
    for value, expected in csv_values:
        fields = {SYNC: value}
        result = should_sync_question(fields)
        status = "✅" if result == expected else "❌"
        print(f"  {status} SYNC?='{value}' -> {result} (esperado: {expected})")
        if result != expected:
            all_passed = False
    
    return all_passed

def main():
    """Função principal do teste."""
    print("🔄 Iniciando teste de case insensitive para SYNC?...\n")
    
    try:
        test1 = test_case_insensitive()
        test2 = test_example_csv_values()
        
        success = test1 and test2
        
        print(f"\n{'✅' if success else '❌'} Resultado final: {'SYNC? É TOTALMENTE CASE INSENSITIVE!' if success else 'PROBLEMAS ENCONTRADOS!'}")
        
        if success:
            print("\n🎉 Confirmação:")
            print("   ✅ Todos os valores são tratados como case insensitive")
            print("   ✅ Espaços em branco são removidos automaticamente")
            print("   ✅ Valores do exemplo CSV funcionam corretamente")
            print("   ✅ Implementação robusta e completa")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
