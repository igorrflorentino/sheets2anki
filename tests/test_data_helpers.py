"""
Funções helper para trabalhar com dados de teste consolidados
"""

import csv
import os
from pathlib import Path

def get_consolidated_data_path():
    """Retorna o caminho para o arquivo consolidado"""
    current_dir = Path(__file__).parent
    return current_dir / ".." / "sample data" / "test_data_consolidated.tsv"

def load_test_data(filter_type=None):
    """
    Carrega dados de teste consolidados
    
    Args:
        filter_type: Tipo de filtro ('basic', 'formula_errors', 'sync_tests', 'all')
    
    Returns:
        Lista de dicionários com dados filtrados
    """
    data_path = get_consolidated_data_path()
    
    with open(data_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        all_data = list(reader)
    
    if filter_type == 'basic':
        # Primeiras 5 linhas para testes básicos
        return all_data[:5]
    elif filter_type == 'formula_errors':
        # Linhas 009-013 que contêm erros de fórmula
        return [row for row in all_data if row['ID'] in ['009', '010', '011', '012', '013']]
    elif filter_type == 'sync_tests':
        # Linhas com diferentes tipos de SYNC?
        return [row for row in all_data if row['SYNC?'].strip()]
    elif filter_type == 'examples':
        # Linhas 001-008 dos exemplos originais
        return [row for row in all_data if row['ID'].startswith('00') and row['ID'] <= '008']
    else:
        # Todos os dados
        return all_data

def get_sync_variations():
    """Retorna todas as variações de SYNC? encontradas nos dados"""
    all_data = load_test_data()
    sync_values = set()
    
    for row in all_data:
        sync_value = row['SYNC?'].strip()
        if sync_value:
            sync_values.add(sync_value)
    
    sync_values = list(sync_values)
    
    true_values = [v for v in sync_values if str(v).lower() in ['true', '1', 'sim', 'yes', 'verdadeiro']]
    false_values = [v for v in sync_values if str(v).lower() in ['false', '0', 'f', 'nao', 'no']]
    
    return {
        'true_values': true_values,
        'false_values': false_values,
        'all_values': sync_values
    }

def get_formula_errors():
    """Retorna exemplos de erros de fórmula encontrados nos dados"""
    formula_data = load_test_data('formula_errors')
    
    errors = []
    for row in formula_data:
        for column, value in row.items():
            if '#' in str(value) or str(value).startswith('='):
                errors.append({
                    'error': value,
                    'column': column,
                    'row_id': row['ID']
                })
    
    return errors

def create_test_subset(size=3):
    """Cria um subconjunto pequeno para testes rápidos"""
    basic_data = load_test_data('basic')
    return basic_data[:size]

# Exemplo de uso:
if __name__ == "__main__":
    # Demonstrar uso das funções
    print("📊 Dados de Teste Consolidados")
    print("=" * 50)
    
    # Dados básicos
    basic_data = load_test_data('basic')
    print(f"Dados básicos: {len(basic_data)} linhas")
    
    # Erros de fórmula
    formula_data = load_test_data('formula_errors')
    print(f"Dados com erros de fórmula: {len(formula_data)} linhas")
    
    # Variações de SYNC?
    sync_vars = get_sync_variations()
    print(f"Valores SYNC? verdadeiros: {sync_vars['true_values']}")
    print(f"Valores SYNC? falsos: {sync_vars['false_values']}")
    
    # Erros encontrados
    errors = get_formula_errors()
    print(f"Erros de fórmula encontrados: {len(errors)}")
    
    print("\n✅ Todas as funções helper funcionando corretamente!")
