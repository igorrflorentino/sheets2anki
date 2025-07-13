#!/usr/bin/env python3
"""
Teste para validar a funcionalidade de sincronização seletiva com SYNC?

Este teste valida:
1. Função should_sync_question() com diferentes valores
2. Estrutura atualizada das colunas
3. Comportamento da filtragem de questões
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_should_sync_question():
    """Testa a função should_sync_question com diferentes valores."""
    from column_definitions import should_sync_question, SYNC
    
    print("🧪 Testando função should_sync_question()...")
    
    # Testes com valores positivos
    positive_tests = [
        ('true', True),
        ('1', True),
        ('sim', True),
        ('yes', True),
        ('verdadeiro', True),
        ('v', True),
        ('TRUE', True),  # Case insensitive
        ('SIM', True),   # Case insensitive
        ('', True),      # Valor vazio deve sincronizar (compatibilidade)
        ('valor_nao_reconhecido', True)  # Valor não reconhecido sincroniza
    ]
    
    for value, expected in positive_tests:
        fields = {SYNC: value}
        result = should_sync_question(fields)
        status = "✅" if result == expected else "❌"
        print(f"  {status} SYNC?='{value}' -> {result} (esperado: {expected})")
    
    # Testes com valores negativos
    negative_tests = [
        ('false', False),
        ('0', False),
        ('não', False),
        ('nao', False),
        ('no', False),
        ('falso', False),
        ('f', False),
        ('FALSE', False),  # Case insensitive
        ('NÃO', False),    # Case insensitive
    ]
    
    for value, expected in negative_tests:
        fields = {SYNC: value}
        result = should_sync_question(fields)
        status = "✅" if result == expected else "❌"
        print(f"  {status} SYNC?='{value}' -> {result} (esperado: {expected})")
    
    print()

def test_column_structure():
    """Testa se a estrutura de colunas foi atualizada corretamente."""
    from column_definitions import REQUIRED_COLUMNS, SYNC, FILTER_FIELDS
    
    print("🧪 Testando estrutura de colunas...")
    
    # Verificar se SYNC está nas colunas obrigatórias
    sync_in_required = SYNC in REQUIRED_COLUMNS
    status = "✅" if sync_in_required else "❌"
    print(f"  {status} SYNC? está nas colunas obrigatórias: {sync_in_required}")
    
    # Verificar se SYNC NÃO está nos campos de filtro (é apenas controle interno)
    sync_not_in_filter = SYNC not in FILTER_FIELDS
    status = "✅" if sync_not_in_filter else "❌"
    print(f"  {status} SYNC? não está nos campos de filtro (controle interno): {sync_not_in_filter}")
    
    # Verificar se a constante SYNC está definida corretamente
    sync_correct = SYNC == 'SYNC?'
    status = "✅" if sync_correct else "❌"
    print(f"  {status} Constante SYNC definida corretamente: {sync_correct}")
    
    print()

def test_column_validation():
    """Testa a validação de colunas com a nova coluna SYNC?."""
    from column_definitions import validate_required_columns
    
    print("🧪 Testando validação de colunas...")
    
    # Teste com todas as colunas necessárias
    complete_columns = [
        'ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'SYNC?', 'INFO COMPLEMENTAR',
        'INFO DETALHADA', 'EXEMPLO 1', 'EXEMPLO 2', 'EXEMPLO 3',
        'TOPICO', 'SUBTOPICO', 'CONCEITO', 'BANCAS', 'ULTIMO ANO EM PROVA', 'TAGS ADICIONAIS'
    ]
    
    is_valid, missing = validate_required_columns(complete_columns)
    status = "✅" if is_valid else "❌"
    print(f"  {status} Validação com todas as colunas: {is_valid}")
    if missing:
        print(f"      Colunas faltando: {missing}")
    
    # Teste sem a coluna SYNC?
    incomplete_columns = [
        'ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'INFO COMPLEMENTAR',
        'INFO DETALHADA', 'EXEMPLO 1', 'EXEMPLO 2', 'EXEMPLO 3',
        'TOPICO', 'SUBTOPICO', 'CONCEITO', 'BANCAS', 'ULTIMO ANO EM PROVA', 'TAGS ADICIONAIS'
    ]
    
    is_valid, missing = validate_required_columns(incomplete_columns)
    status = "✅" if not is_valid and 'SYNC?' in missing else "❌"
    print(f"  {status} Validação sem SYNC? detecta erro: {not is_valid}")
    if missing:
        print(f"      Colunas faltando: {missing}")
    
    print()

def test_field_category():
    """Testa a categorização do campo SYNC?."""
    from column_definitions import get_field_category, is_filter_field
    
    print("🧪 Testando categorização do campo SYNC?...")
    
    # Verificar categoria do campo SYNC? (deve ser 'unknown' pois não é filtro nem essencial)
    category = get_field_category('SYNC?')
    expected_category = 'unknown'
    status = "✅" if category == expected_category else "❌"
    print(f"  {status} Categoria do SYNC?: {category} (esperado: {expected_category})")
    
    # Verificar se NÃO é campo de filtro (é apenas controle interno)
    is_filter = is_filter_field('SYNC?')
    status = "✅" if not is_filter else "❌"
    print(f"  {status} SYNC? não é campo de filtro: {not is_filter}")
    
    print()

def main():
    """Função principal do teste."""
    print("🔄 Iniciando testes da funcionalidade de sincronização seletiva...\n")
    
    try:
        test_should_sync_question()
        test_column_structure()
        test_column_validation()
        test_field_category()
        
        print("✅ Todos os testes concluídos!")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
