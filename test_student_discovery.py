#!/usr/bin/env python3
"""
Teste isolado para verificar a descoberta de estudantes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock das dependências do Anki
class MockMW:
    pass

sys.modules['aqt'] = type(sys)('aqt')
sys.modules['anki'] = type(sys)('anki')
sys.modules['anki.collection'] = type(sys)('anki.collection')

# Importar os módulos após os mocks
import json
from src import column_definitions as cols
from src.student_manager import discover_students_from_tsv_url

def test_tsv_parsing():
    """Testa o parsing de TSV com dados simulados."""
    
    print("=== TESTE DE PARSING TSV ===")
    print(f"Procurando pela coluna: '{cols.ALUNOS}'")
    
    # Simular dados TSV
    test_data = f"""PERGUNTA	RESPOSTA	{cols.ALUNOS}	TOPICO	SUBTOPICO
Pergunta 1	Resposta 1	João, Maria	Tópico A	Sub A
Pergunta 2	Resposta 2	Pedro	Tópico B	Sub B
Pergunta 3	Resposta 3	Ana, Carlos, João	Tópico C	Sub C"""
    
    print(f"Dados de teste:\n{test_data}")
    
    # Salvar em arquivo temporário e processar
    with open('test_temp.tsv', 'w', encoding='utf-8') as f:
        f.write(test_data)
    
    # Teste com arquivo local (simular URL)
    import urllib.request
    from unittest.mock import patch
    
    with patch('urllib.request.urlopen') as mock_urlopen:
        # Mock da resposta HTTP
        class MockResponse:
            def read(self):
                return test_data.encode('utf-8')
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        mock_urlopen.return_value = MockResponse()
        
        # Testar descoberta
        students = discover_students_from_tsv_url('http://fake-url.com/test.tsv')
        print(f"\nEstudantes encontrados: {sorted(students)}")
        
        expected = {'João', 'Maria', 'Pedro', 'Ana', 'Carlos'}
        print(f"Esperado: {sorted(expected)}")
        print(f"Teste {'PASSOU' if students == expected else 'FALHOU'}")
    
    # Limpar arquivo temporário
    try:
        os.remove('test_temp.tsv')
    except:
        pass

def test_meta_config():
    """Testa a leitura da configuração meta.json."""
    print("\n=== TESTE DE CONFIGURAÇÃO ===")
    
    try:
        with open('meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        decks = meta.get('decks', {})
        print(f"Decks encontrados no meta.json: {len(decks)}")
        
        for hash_key, deck_info in decks.items():
            print(f"Hash: {hash_key}")
            print(f"Nome remoto: {deck_info.get('remote_deck_name', 'N/A')}")
            print(f"URL remota: {deck_info.get('remote_deck_url', 'N/A')}")
            print("---")
    
    except FileNotFoundError:
        print("Arquivo meta.json não encontrado")
    except Exception as e:
        print(f"Erro ao ler meta.json: {e}")

if __name__ == "__main__":
    test_tsv_parsing()
    test_meta_config()
