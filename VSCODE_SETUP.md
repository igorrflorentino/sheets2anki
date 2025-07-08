# Guia Rápido: Eliminando Erros de Sintaxe no VS Code

## Resumo da Solução

Para trabalhar com código Anki no VS Code sem erros de sintaxe, implementamos:

### 1. Stubs do Anki
```
stubs/
├── __init__.py          # Pacote Python vazio
├── aqt.py              # Mock dos módulos aqt (interface)
└── anki.py             # Mock dos módulos anki (core)
```

### 2. Configurações do VS Code
```json
// .vscode/settings.json
{
  "python.analysis.stubPath": "./stubs",
  "python.analysis.extraPaths": ["./stubs"],
  "python.linting.flake8Args": ["--ignore=E501,W503,F401,F841"]
}
```

### 3. Configurações do Pyright
```json
// pyrightconfig.json
{
  "stubPath": "./stubs",
  "reportMissingImports": "none",
  "reportUnusedImport": "none",
  "reportAttributeAccessIssue": "none"
}
```

## O que foi Resolvido

✅ **Imports não resolvidos**: `from aqt import mw`  
✅ **Módulos não encontrados**: `aqt.utils`, `aqt.qt`, `aqt.importing`  
✅ **Atributos desconhecidos**: `mw.col`, `mw.addonManager`, `mw.app`  
✅ **Warnings de imports**: Variáveis não utilizadas, imports desnecessários  
✅ **Autocomplete**: Sugestões de métodos e propriedades  

## Como Verificar se Funcionou

1. Abra `remote_decks/main.py` no VS Code
2. Verifique se não há sublinhados vermelhos nos imports
3. Teste autocomplete digitando `mw.` - deve mostrar sugestões
4. Execute `python -m py_compile remote_decks/main.py` - deve passar sem erros

## Para Novos Módulos/Métodos

Se precisar de novos métodos do Anki não cobertos pelos stubs:

1. Adicione ao arquivo `stubs/aqt.py` ou `stubs/anki.py`
2. Siga o padrão de mock das classes existentes
3. Recarregue a janela do VS Code (`Cmd+Shift+P` > "Developer: Reload Window")

## Troubleshooting

**VS Code ainda mostra erros?**
- Recarregue a janela: `Cmd+Shift+P` > "Developer: Reload Window"
- Verifique o Python interpreter: `Cmd+Shift+P` > "Python: Select Interpreter"

**Autocomplete não funciona?**
- Confirme que `python.analysis.extraPaths` inclui `"./stubs"`
- Verifique se os arquivos em `stubs/` são válidos Python

**Erros de flake8?**
- Adicione códigos de erro ao `--ignore` em `.vscode/settings.json`
- Exemplo: `"--ignore=E501,W503,F401,F841,E402"`

## Notas Importantes

- ⚠️ **Stubs são apenas para desenvolvimento** - não incluir no add-on final
- ✅ **Código funciona normalmente no Anki** - stubs não afetam execução real
- 🔄 **Sempre testar no Anki** após desenvolvimento no VS Code
