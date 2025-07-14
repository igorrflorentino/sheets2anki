#!/usr/bin/env python3
"""
Script para atualizar testes para usar o arquivo consolidado test_data_consolidated.tsv
"""

import os
import sys
import shutil
from pathlib import Path

def get_project_root():
    """Retorna o diretório raiz do projeto"""
    return Path(__file__).parent.parent

def backup_old_files():
    """Faz backup dos arquivos antigos"""
    project_root = get_project_root()
    backup_dir = project_root / "backup_tsv_files"
    
    if not backup_dir.exists():
        backup_dir.mkdir()
    
    # Arquivos para backup
    old_files = [
        "test_sheet.tsv",
        "docs/exemplo_planilha_com_sync.tsv",
        "tests/test_formula_errors_data.tsv"
    ]
    
    print("📦 Fazendo backup dos arquivos antigos...")
    
    for file_path in old_files:
        full_path = project_root / file_path
        if full_path.exists():
            backup_path = backup_dir / full_path.name
            shutil.copy2(full_path, backup_path)
            print(f"✅ Backup: {file_path} -> backup_tsv_files/{full_path.name}")
    
    return backup_dir

def update_test_files():
    """Atualiza os arquivos de teste para usar o arquivo consolidado"""
    project_root = get_project_root()
    tests_dir = project_root / "tests"
    
    # Mapear arquivos de teste que precisam ser atualizados
    test_updates = {
        "test_real_csv.py": {
            "old_path": "test_sheet.tsv",
            "new_path": "tests/test_data_consolidated.tsv"
        },
        "test_formula_errors_simple.py": {
            "old_path": "tests/test_formula_errors_data.tsv",
            "new_path": "tests/test_data_consolidated.tsv"
        },
        "test_debug_sync.py": {
            "old_path": "test_sheet.tsv",
            "new_path": "tests/test_data_consolidated.tsv"
        }
    }
    
    print("🔄 Atualizando arquivos de teste...")
    
    for test_file, paths in test_updates.items():
        test_path = tests_dir / test_file
        
        if test_path.exists():
            print(f"📝 Processando: {test_file}")
            
            # Ler conteúdo do arquivo
            with open(test_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir referências ao arquivo antigo
            old_ref = paths["old_path"]
            new_ref = paths["new_path"]
            
            # Diferentes padrões de referência
            patterns_to_replace = [
                (f'"{old_ref}"', f'"{new_ref}"'),
                (f"'{old_ref}'", f"'{new_ref}'"),
                (f'os.path.join(os.path.dirname(__file__), "..", "{old_ref}")', 
                 f'os.path.join(os.path.dirname(__file__), "test_data_consolidated.tsv")'),
                (f'os.path.join(os.path.dirname(__file__), "{old_ref}")', 
                 f'os.path.join(os.path.dirname(__file__), "test_data_consolidated.tsv")'),
            ]
            
            updated = False
            for old_pattern, new_pattern in patterns_to_replace:
                if old_pattern in content:
                    content = content.replace(old_pattern, new_pattern)
                    updated = True
            
            if updated:
                # Escrever arquivo atualizado
                with open(test_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Atualizado: {test_file}")
            else:
                print(f"ℹ️  Nenhuma mudança necessária: {test_file}")
        else:
            print(f"⚠️  Arquivo não encontrado: {test_file}")

def create_helper_functions():
    """Cria funções helper para trabalhar com dados consolidados"""
    helper_content = '''"""
Funções helper para trabalhar com dados de teste consolidados
"""

import pandas as pd
import os
from pathlib import Path

def get_consolidated_data_path():
    """Retorna o caminho para o arquivo consolidado"""
    current_dir = Path(__file__).parent
    return current_dir / "test_data_consolidated.tsv"

def load_test_data(filter_type=None):
    """
    Carrega dados de teste consolidados
    
    Args:
        filter_type: Tipo de filtro ('basic', 'formula_errors', 'sync_tests', 'all')
    
    Returns:
        DataFrame com dados filtrados
    """
    data_path = get_consolidated_data_path()
    df = pd.read_csv(data_path, sep='\\t')
    
    if filter_type == 'basic':
        # Primeiras 5 linhas para testes básicos
        return df.head(5)
    elif filter_type == 'formula_errors':
        # Linhas 009-013 que contêm erros de fórmula
        return df[df['ID'].astype(str).isin(['009', '010', '011', '012', '013'])]
    elif filter_type == 'sync_tests':
        # Linhas com diferentes tipos de SYNC?
        return df[df['SYNC?'].notna()]
    elif filter_type == 'examples':
        # Linhas 001-008 dos exemplos originais
        return df[df['ID'].astype(str).str.match(r'^00[1-8]$')]
    else:
        # Todos os dados
        return df

def get_sync_variations():
    """Retorna todas as variações de SYNC? encontradas nos dados"""
    df = load_test_data()
    sync_values = df['SYNC?'].dropna().unique()
    return {
        'true_values': [v for v in sync_values if str(v).lower() in ['true', '1', 'sim', 'yes', 'verdadeiro']],
        'false_values': [v for v in sync_values if str(v).lower() in ['false', '0', 'f', 'nao', 'no']],
        'all_values': list(sync_values)
    }

def get_formula_errors():
    """Retorna exemplos de erros de fórmula encontrados nos dados"""
    df = load_test_data('formula_errors')
    
    errors = []
    for _, row in df.iterrows():
        for column in df.columns:
            value = str(row[column])
            if '#' in value or value.startswith('='):
                errors.append({
                    'error': value,
                    'column': column,
                    'row_id': row['ID']
                })
    
    return errors

def create_test_subset(size=3):
    """Cria um subconjunto pequeno para testes rápidos"""
    df = load_test_data('basic')
    return df.head(size)

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
    
    print("\\n✅ Todas as funções helper funcionando corretamente!")
'''
    
    tests_dir = Path(__file__).parent
    helper_path = tests_dir / "test_data_helpers.py"
    
    with open(helper_path, 'w', encoding='utf-8') as f:
        f.write(helper_content)
    
    print(f"✅ Criado: {helper_path}")

def main():
    """Função principal de migração"""
    print("🚀 MIGRAÇÃO PARA DADOS CONSOLIDADOS")
    print("=" * 50)
    
    try:
        # 1. Fazer backup dos arquivos antigos
        backup_dir = backup_old_files()
        
        # 2. Atualizar arquivos de teste
        update_test_files()
        
        # 3. Criar funções helper
        create_helper_functions()
        
        print("\\n" + "=" * 50)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 50)
        
        print("📋 Próximos passos:")
        print("1. Testar os arquivos atualizados")
        print("2. Validar que todos os testes passam")
        print("3. Remover arquivos antigos após confirmação")
        print("4. Usar test_data_helpers.py para novos testes")
        
        print(f"\\n📦 Backup dos arquivos antigos: {backup_dir}")
        print("🆕 Novo arquivo consolidado: tests/test_data_consolidated.tsv")
        print("🔧 Funções helper: tests/test_data_helpers.py")
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
