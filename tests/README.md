# Testes do Sheets2Anki

Este diretório contém os testes automatizados para o projeto Sheets2Anki, utilizando o framework pytest.

## Estrutura de Testes

```
tests/
├── conftest.py           # Configurações globais e fixtures
├── unit/                 # Testes unitários
│   ├── test_sync_selective.py
│   ├── test_formula_cleaning.py
│   ├── test_url_validation.py
│   └── test_subdeck_manager.py
└── integration/          # Testes de integração
    └── test_deck_creation.py
```

## Como Executar os Testes

### Usando o script run_pytest.py

```bash
# Executar todos os testes
python run_pytest.py

# Executar apenas testes rápidos
python run_pytest.py quick
```

### Usando pytest diretamente

```bash
# Executar todos os testes
pytest

# Executar apenas testes unitários
pytest tests/unit

# Executar apenas testes de integração
pytest tests/integration

# Executar um teste específico
pytest tests/unit/test_sync_selective.py

# Executar com saída detalhada
pytest -v

# Executar com saída detalhada e parar no primeiro erro
pytest -xvs
```

## Fixtures Disponíveis

- `sample_tsv_data`: Fornece dados TSV de exemplo para testes
- `formula_error_data`: Fornece exemplos de erros de fórmula para testes

## Marcadores (Markers)

- `@pytest.mark.unit`: Testes unitários
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.slow`: Testes lentos (pulados no modo rápido)

## Adicionando Novos Testes

1. Crie um novo arquivo na pasta apropriada (unit/ ou integration/)
2. Nomeie o arquivo como `test_*.py`
3. Crie classes de teste com nome iniciando com `Test`
4. Crie métodos de teste com nome iniciando com `test_`
5. Use fixtures conforme necessário
6. Adicione marcadores apropriados