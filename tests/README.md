# Testes do Sheets2Anki

Esta pasta contém todos os testes do projeto Sheets2Anki, organizados para facilitar a manutenção e execução.

## Estrutura de Testes

### Testes Unitários
- **`test_main.py`**: Testes para o módulo principal (`main.py`)
  - Validação de URLs
  - Criação de modelos de cards
  - Sincronização de decks
  - Gerenciamento de decks remotos

- **`test_parseRemoteDeck.py`**: Testes para análise de decks remotos (`parseRemoteDeck.py`)
  - Parsing de dados TSV
  - Validação de headers
  - Criação de tags hierárquicas
  - Detecção de cards cloze

### Testes de Interface
- **`test_selection_dialog.py`**: Testes para interface de seleção de decks
  - Funcionalidades de seleção
  - Interface com checkboxes
  - Integração com sincronização

## Como Executar os Testes

### Usando pytest (recomendado)
```bash
# Instalar pytest se não tiver
pip install pytest

# Executar todos os testes
python -m pytest tests/

# Executar testes com output detalhado
python -m pytest tests/ -v

# Executar um arquivo específico
python -m pytest tests/test_main.py
```

### Usando unittest (built-in)
```bash
# Executar todos os testes
python -m unittest discover tests/

# Executar um arquivo específico
python -m unittest tests.test_main
python -m unittest tests.test_parseRemoteDeck

# Executar com output detalhado
python -m unittest tests.test_main -v
```

## Cobertura de Testes

Os testes cobrem as principais funcionalidades:

- ✅ Validação de URLs e dados TSV
- ✅ Criação e gerenciamento de modelos de cards
- ✅ Processamento de tags hierárquicas
- ✅ Detecção de cards cloze
- ✅ Sincronização de decks
- ✅ Interface de seleção de decks

## Adicionando Novos Testes

Ao adicionar novos testes:

1. Siga a convenção de nomes `test_*.py`
2. Use a estrutura de imports padrão com `sys.path.insert()`
3. Organize testes por funcionalidade
4. Adicione docstrings descritivas
5. Use mocks para dependências externas (Anki, rede, etc.)

## Dependências para Testes

- `unittest` (built-in)
- `unittest.mock` (built-in)
- `pytest` (opcional, mas recomendado)

## Notas Importantes

- Os testes são independentes do ambiente Anki
- Mocks são usados para simular funcionalidades do Anki
- Testes de rede usam mocks para evitar dependências externas
- A estrutura permite execução tanto no VS Code quanto linha de comando
