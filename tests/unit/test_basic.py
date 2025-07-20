"""
Teste básico para verificar se a configuração do pytest está funcionando.
"""
import pytest
import os
from src.column_definitions import should_sync_question, SYNC

def test_environment_setup():
    """Verifica se o ambiente de teste está configurado corretamente."""
    # Definir a variável de ambiente para o teste
    os.environ["SHEETS2ANKI_TEST_MODE"] = "1"
    assert os.environ.get("SHEETS2ANKI_TEST_MODE") == "1"
    
def test_basic_assertion():
    """Teste básico para verificar se as asserções funcionam."""
    assert 1 + 1 == 2
    
def test_pytest_working():
    """Teste para verificar se o pytest está funcionando."""
    assert True
    
def test_sync_true():
    """Teste para verificar se a função should_sync_question funciona corretamente."""
    fields = {SYNC: "true"}
    assert should_sync_question(fields) == True
    
def test_sync_false():
    """Teste para verificar se a função should_sync_question funciona corretamente."""
    fields = {SYNC: "false"}
    assert should_sync_question(fields) == False