#!/usr/bin/env python3
"""
Teste direto da URL do TSV para verificar se há dados de alunos.
"""

import urllib.request
import csv
from io import StringIO
import json

def test_tsv_download():
    """Testa download e parsing da URL TSV real."""
    print("=== TESTE DE DOWNLOAD E PARSING TSV ===")
    
    # Obter URL do meta.json
    try:
        with open('meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        decks = meta.get('decks', {})
        if not decks:
            print("❌ Nenhum deck configurado")
            return False
        
        # Pegar o primeiro deck
        deck_info = list(decks.values())[0]
        url = deck_info.get('remote_deck_url')
        deck_name = deck_info.get('remote_deck_name', 'N/A')
        
        print(f"Testando deck: {deck_name}")
        print(f"URL: {url}")
        
        # Fazer download
        print("\n📥 Fazendo download...")
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
        
        print(f"✅ Download concluído: {len(data)} characters")
        print(f"🔍 Primeiros 300 chars:")
        print(repr(data[:300]))
        
        # Parse CSV/TSV
        print("\n📋 Analisando cabeçalhos...")
        csv_reader = csv.DictReader(StringIO(data), delimiter='\t')
        
        fieldnames = csv_reader.fieldnames
        print(f"Cabeçalhos encontrados: {fieldnames}")
        
        # Verificar se existe coluna ALUNOS
        alunos_column = 'ALUNOS'
        if alunos_column not in fieldnames:
            print(f"❌ PROBLEMA: Coluna '{alunos_column}' não encontrada!")
            print(f"Colunas disponíveis: {[col for col in fieldnames if col]}")
            return False
        
        print(f"✅ Coluna '{alunos_column}' encontrada!")
        
        # Analisar dados
        print(f"\n📊 Analisando conteúdo da coluna '{alunos_column}'...")
        students = set()
        row_count = 0
        rows_with_students = 0
        
        for row in csv_reader:
            row_count += 1
            
            if row_count <= 5:  # Mostrar primeiras 5 linhas
                print(f"Linha {row_count}: {dict(row)}")
            
            alunos_value = row.get(alunos_column, '').strip()
            if alunos_value:
                rows_with_students += 1
                print(f"  🎓 Linha {row_count} tem alunos: '{alunos_value}'")
                
                # Processar alunos (separados por vírgula)
                for aluno in alunos_value.split(','):
                    aluno = aluno.strip()
                    if aluno:
                        students.add(aluno)
                        print(f"    ➕ Adicionado: '{aluno}'")
        
        print(f"\n📈 RESUMO:")
        print(f"Total de linhas processadas: {row_count}")
        print(f"Linhas com dados de alunos: {rows_with_students}")
        print(f"Total de estudantes únicos: {len(students)}")
        print(f"Lista de estudantes: {sorted(students)}")
        
        if len(students) == 0:
            print("❌ PROBLEMA: Nenhum estudante encontrado na coluna ALUNOS!")
            print("Verifique se a planilha tem dados na coluna ALUNOS.")
            return False
        
        print("✅ SUCESSO: Estudantes encontrados!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tsv_download()
    if success:
        print("\n🎉 TESTE PASSOU - O problema deve estar na integração com o Anki")
    else:
        print("\n❌ TESTE FALHOU - Corrija o problema identificado")
