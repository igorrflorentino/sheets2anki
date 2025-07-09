# Correção do Erro de Importação - sheets2anki

## Problema Original
```
Erro ao importar módulos do plugin sheets2anki:
No module named 'sheet2anki-v2.remote_decks'
```

## Causa do Problema
O arquivo `__init__.py` estava tentando importar módulos de uma pasta chamada `remote_decks` que não existia no projeto. A estrutura real do projeto usa a pasta `src` para o código principal.

## Correções Aplicadas

### 1. Caminho das Bibliotecas
**Antes:**
```python
libs_path = os.path.join(addon_path, 'remote_decks', 'libs')
```

**Depois:**
```python
libs_path = os.path.join(addon_path, 'libs')
```

### 2. Imports das Funções Principais
**Antes:**
```python
from .remote_decks.main import import_test_deck
from .remote_decks.main import addNewDeck
from .remote_decks.main import syncDecksWithSelection as sDecks
from .remote_decks.main import removeRemoteDeck as rDecks
```

**Depois:**
```python
from .src.main import import_test_deck
from .src.main import addNewDeck
from .src.main import syncDecksWithSelection as sDecks
from .src.main import removeRemoteDeck as rDecks
```

### 3. Import da Função Utils
**Antes:**
```python
from .remote_decks.libs.org_to_anki.utils import getAnkiPluginConnector as getConnector
```

**Depois:**
```python
from .libs.org_to_anki.utils import getAnkiPluginConnector as getConnector
```

### 4. Configuração Pyright
O arquivo `pyrightconfig.json` foi atualizado para refletir a estrutura correta:

**Antes:**
```json
"include": [
    "remote_decks",
    "tests",
    "stubs"
]
```

**Depois:**
```json
"include": [
    "src",
    "tests", 
    "stubs"
]
```

## Estrutura Correta do Projeto
```
sheets2anki/
├── __init__.py          # Módulo principal corrigido
├── src/                 # Código principal
│   ├── main.py         # Funções principais
│   ├── parseRemoteDeck.py
│   └── ...
├── libs/               # Bibliotecas externas
│   ├── org_to_anki/
│   │   ├── utils.py    # Função getAnkiPluginConnector
│   │   └── ...
│   └── ...
├── stubs/              # Stubs para desenvolvimento
└── tests/              # Testes
```

## Verificação
O script `test_structure.py` foi criado para verificar que todas as correções foram aplicadas corretamente. Todas as verificações passaram:
- ✓ Arquivos principais existem
- ✓ Funções foram encontradas nos arquivos corretos
- ✓ Imports foram corrigidos no `__init__.py`
- ✓ Todas as referências a `remote_decks` foram removidas

## Status
🎉 **PROBLEMA RESOLVIDO!** 

O erro `No module named 'sheet2anki-v2.remote_decks'` foi corrigido. O plugin agora pode ser carregado corretamente no Anki.

## Organização dos Testes

Os arquivos de teste foram organizados na pasta `tests/`:
- `tests/test_structure.py` - Verifica a estrutura do projeto
- `tests/test_imports.py` - Testa importações (pode falhar fora do ambiente Anki)
- `tests/README.md` - Documentação dos testes
- `run_tests.py` - Script para executar todos os testes

Para executar os testes: `python run_tests.py`
