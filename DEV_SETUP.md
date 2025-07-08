# Configuração de Desenvolvimento - Sheets2Anki

Este documento explica como configurar o ambiente de desenvolvimento para trabalhar com o código do Sheets2Anki fora do ambiente Anki.

## Problema

O VS Code acusa erros de sintaxe para imports do Anki (`aqt`, `anki`) quando estamos desenvolvendo fora do ambiente Anki, pois esses módulos não estão disponíveis no sistema.

## Soluções Implementadas

### 1. Stubs/Mocks dos Módulos Anki

**Localização**: `stubs/aqt.py` e `stubs/anki.py`

Criamos simulações (stubs) dos principais módulos e classes do Anki:
- `aqt.mw` (main window)
- `aqt.utils` (showInfo, qconnect)
- `aqt.qt` (componentes Qt: QDialog, QPushButton, etc.)
- `aqt.importing` (ImportDialog)
- Classes de coleção e modelos do Anki

### 2. Configuração do VS Code

**Arquivo**: `.vscode/settings.json`

```json
{
  "python.analysis.extraPaths": [
    "/Applications/Anki.app/Contents/Resources",
    "./stubs"
  ],
  "python.analysis.stubPath": "./stubs",
  "python.analysis.typeCheckingMode": "basic",
  "python.linting.flake8Args": [
    "--ignore=E501,W503,F401,F841"
  ]
}
```

### 3. Configuração do Pyright

**Arquivo**: `pyrightconfig.json`

Configura o language server Python para usar os stubs com configurações tolerantes:
```json
{
  "stubPath": "./stubs",
  "extraPaths": ["./stubs"],
  "typeCheckingMode": "basic",
  "reportMissingImports": "none",
  "reportUnusedImport": "none",
  "reportUnusedVariable": "none",
  "reportAttributeAccessIssue": "none"
}
```

### 4. Imports com Fallback

**Nos arquivos Python**:

```python
# Anki imports
try:
    from aqt import mw  # type: ignore
    from aqt.utils import showInfo, qconnect  # type: ignore
except ImportError:
    # Fallback para desenvolvimento fora do ambiente Anki
    import sys
    import os
    stubs_path = os.path.join(os.path.dirname(__file__), '..', 'stubs')
    if os.path.exists(stubs_path):
        sys.path.insert(0, stubs_path)
        from aqt import mw  # type: ignore
```

## Como Usar

### Para Desenvolvimento Local

1. **Abra o projeto no VS Code**
2. **Instale a extensão Python** se ainda não tiver
3. **Recarregue a janela** (Ctrl+Shift+P → "Developer: Reload Window")
4. **Os erros de import devem desaparecer**

### Para Executar Testes

```bash
# Executar testes (usam os stubs automaticamente)
python -m pytest tests/

# Executar arquivo específico
python -m unittest tests.test_main
```

### Para Produção (Anki)

O código funciona normalmente no Anki pois:
- Os imports reais do Anki têm prioridade
- O fallback para stubs só acontece se os módulos reais não existirem
- Os comentários `# type: ignore` não afetam a execução

## Benefícios

✅ **Eliminação de erros**: Sem mais erros vermelhos no VS Code  
✅ **Intellisense funcional**: Autocompletar e sugestões funcionam  
✅ **Análise estática**: Verificação de tipos e linting  
✅ **Compatibilidade**: Funciona tanto no desenvolvimento quanto na produção  
✅ **Facilita testes**: Permite rodar testes fora do Anki  

## Estrutura de Arquivos

```
sheets2anki/
├── .vscode/
│   └── settings.json          # Configuração do VS Code
├── stubs/
│   ├── __init__.py           # Torna stubs um módulo
│   └── aqt.py                # Simulações dos módulos Anki
├── remote_decks/             # Código principal
├── tests/                    # Testes unitários
├── pyrightconfig.json        # Configuração do Pyright
└── DEV_SETUP.md             # Este arquivo
```

## Troubleshooting

### Erros ainda aparecem

1. **Recarregue o VS Code**: Ctrl+Shift+P → "Developer: Reload Window"
2. **Verifique o Python interpreter**: Ctrl+Shift+P → "Python: Select Interpreter"
3. **Limpe o cache**: Ctrl+Shift+P → "Python: Clear Cache and Reload Window"

### Autocompletar não funciona

1. **Verifique se os stubs estão no path**: `.vscode/settings.json`
2. **Confirme a configuração do Pyright**: `pyrightconfig.json`
3. **Reinstale a extensão Python** se necessário

### Problemas nos testes

1. **Use imports relativos** nos testes: `from remote_decks import main`
2. **Adicione o path** se necessário: `sys.path.insert(0, ...)`
