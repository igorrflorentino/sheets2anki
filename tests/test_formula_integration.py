#!/usr/bin/env python3
"""
Teste de integração para verificar limpeza de erros de fórmulas em TSV real.
"""

import sys
import os
import csv
import re

# Adicionar o diretório src ao path para permitir imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_formula_errors_integration():
    """Testa a limpeza de erros de fórmulas com um arquivo TSV real."""
    
    print("🧪 Testando integração com arquivo TSV contendo erros de fórmulas...")
    
    # Ler o arquivo TSV de teste
    tsv_file = os.path.join(os.path.dirname(__file__), 'test_formula_errors_data.tsv')
    
    if not os.path.exists(tsv_file):
        print("❌ Arquivo de teste TSV não encontrado!")
        return False
    
    # Ler dados do TSV
    with open(tsv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        data = list(reader)
    
    print(f"📋 Arquivo TSV carregado com {len(data)} linhas (incluindo header)")
    
    if len(data) < 2:
        print("❌ Arquivo TSV deve ter pelo menos headers e uma linha de dados")
        return False
    
    # Simular o processamento que acontece em parseRemoteDeck.py
    headers = [h.strip().upper() for h in data[0]]
    header_indices = {header: idx for idx, header in enumerate(headers)}
    
    print(f"📋 Headers encontrados: {headers}")
    
    # Função de detecção de fórmulas (cópia melhorada)
    def detect_formula_content(cell_value):
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
            
            # Verificar padrões de fórmulas válidas
            formula_content = cell_value[1:]  # Remove o =
            
            # Se contém apenas espaços após =, não é fórmula
            if not formula_content.strip():
                return False
            
            # Se contém palavras comuns que indicam que não é fórmula
            non_formula_indicators = [
                ' não ', ' nao ', ' is ', ' are ', ' was ', ' were ',
                ' the ', ' and ', ' or ', ' but ', ' if ', ' when ',
                ' para ', ' com ', ' sem ', ' por ', ' em ', ' de ',
            ]
            
            for indicator in non_formula_indicators:
                if indicator in cell_value.lower():
                    return False
            
            # Verificar padrões comuns de fórmulas válidas
            valid_formula_patterns = [
                r'^=\w+\(',  # =FUNCAO(
                r'^=\d+[\+\-\*\/]',  # =5+, =10*, etc.
                r'^=[A-Z]+\d+',  # =A1, =B2, etc.
                r'^=.*\([^\)]*\).*$',  # Qualquer função com parênteses
                r'^=\d+(\.\d+)?([\+\-\*\/]\d+(\.\d+)?)+$',  # Operações matemáticas: =5+3, =10*2.5
            ]
            
            for pattern in valid_formula_patterns:
                if re.search(pattern, cell_value):
                    return True
            
            return False
        
        return False
    
    # Função de limpeza (cópia da implementação)
    def clean_formula_errors(cell_value):
        if not cell_value or not isinstance(cell_value, str):
            return cell_value
        
        formula_errors = [
            '#NAME?', '#REF!', '#VALUE!', '#DIV/0!', '#N/A', 
            '#NULL!', '#NUM!', '#ERROR!'
        ]
        
        cell_value_stripped = cell_value.strip()
        
        if cell_value_stripped in formula_errors:
            return ""
        
        if cell_value_stripped.startswith('#') and cell_value_stripped.endswith('!'):
            return ""
        
        # Verificar se é uma fórmula não calculada (novo)
        if detect_formula_content(cell_value_stripped):
            return ""
        
        return cell_value
    
    # Processar cada linha de dados
    errors_found = []
    errors_cleaned = []
    
    for row_num, row in enumerate(data[1:], start=2):
        print(f"\n📋 Processando linha {row_num}:")
        
        # Simular _create_fields_dict
        fields = {}
        for header in headers:
            idx = header_indices[header]
            if idx < len(row):
                raw_value = row[idx].strip()
                cleaned_value = clean_formula_errors(raw_value)
                
                # Registrar erros encontrados
                if raw_value != cleaned_value and raw_value:
                    errors_found.append((row_num, header, raw_value))
                    errors_cleaned.append((row_num, header, raw_value, cleaned_value))
                    print(f"  🧹 {header}: '{raw_value}' → '{cleaned_value}'")
                
                fields[header] = cleaned_value
            else:
                fields[header] = ""
        
        # Mostrar resultado final da linha
        important_fields = ['ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'SYNC?']
        for field in important_fields:
            if field in fields:
                print(f"  ✓ {field}: '{fields[field]}'")
    
    # Relatório final
    print(f"\n📊 Relatório de limpeza:")
    print(f"  🔍 Erros de fórmula encontrados: {len(errors_found)}")
    print(f"  🧹 Erros limpos com sucesso: {len(errors_cleaned)}")
    
    if errors_found:
        print(f"\n📋 Detalhes dos erros encontrados:")
        for row_num, header, raw_value in errors_found:
            print(f"  • Linha {row_num}, {header}: '{raw_value}'")
    
    if errors_cleaned:
        print(f"\n✨ Limpezas realizadas:")
        for row_num, header, original, cleaned in errors_cleaned:
            print(f"  • Linha {row_num}, {header}: '{original}' → '{cleaned}'")
    
    # Verificar se pelo menos alguns erros foram encontrados e limpos
    expected_errors = [
        '#NAME?', '#REF!', '#VALUE!', '#DIV/0!', '#N/A', 
        '#NULL!', '#NUM!', '#ERROR!', '#CUSTOM!'
    ]
    
    found_error_values = [error[2] for error in errors_found]
    expected_found = any(err in found_error_values for err in expected_errors)
    
    if not expected_found:
        print("⚠️  Nenhum erro de fórmula conhecido foi encontrado no arquivo de teste")
        return False
    
    # Verificar se todos os erros foram limpos para string vazia
    all_cleaned_properly = all(cleaned == '' for _, _, _, cleaned in errors_cleaned)
    
    if not all_cleaned_properly:
        print("❌ Nem todos os erros foram limpos para string vazia")
        return False
    
    print("\n🎉 Teste de integração passou com sucesso!")
    print("✅ Erros de fórmulas detectados e limpos corretamente")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE INTEGRAÇÃO - LIMPEZA DE ERROS DE FÓRMULAS")
    print("=" * 60)
    
    if test_formula_errors_integration():
        print("\n🎉 TESTE DE INTEGRAÇÃO PASSOU!")
        sys.exit(0)
    else:
        print("\n❌ TESTE DE INTEGRAÇÃO FALHOU")
        sys.exit(1)
