"""
Configurações globais para os testes do Sheets2Anki usando pytest.
"""
import os
import sys
import pytest

# Adicionar o diretório raiz do projeto ao path para importações
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_tsv_data():
    """Fixture que fornece dados TSV de exemplo para testes."""
    return [
        # Headers
        ['ID', 'PERGUNTA', 'LEVAR PARA PROVA', 'SYNC?', 'INFO COMPLEMENTAR', 
         'INFO DETALHADA', 'EXEMPLO 1', 'EXEMPLO 2', 'EXEMPLO 3', 
         'TOPICO', 'SUBTOPICO', 'CONCEITO', 'BANCAS', 'ULTIMO ANO EM PROVA', 
         'CARREIRA', 'IMPORTANCIA', 'TAGS ADICIONAIS'],
        
        # Dados
        ['001', 'Qual é a capital do Brasil?', 'Brasília', 'true', 'Info complementar', 
         'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 
         'VUNESP', '2023', 'PC', 'Alta', 'brasil'],
        
        ['002', 'Qual é a capital da França?', 'Paris', 'false', 'Info complementar', 
         'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 
         'VUNESP', '2023', 'PC', 'Alta', 'frança'],
        
        ['003', 'Qual é a capital da Alemanha?', 'Berlim', 'true', 'Info complementar', 
         'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Geografia', 'Capitais', 'Capital', 
         'VUNESP', '2023', 'PC', 'Alta', 'alemanha'],
    ]

@pytest.fixture
def formula_error_data():
    """Fixture que fornece exemplos de erros de fórmula para testes."""
    return [
        ('#NAME?', ''),
        ('#REF!', ''),
        ('#VALUE!', ''),
        ('#DIV/0!', ''),
        ('=SUM(A1:A10)', ''),
        ('=VLOOKUP(A1, B1:C10, 2, FALSE)', ''),
        ('Texto normal', 'Texto normal'),
        ('123', '123'),
        ('', ''),
    ]