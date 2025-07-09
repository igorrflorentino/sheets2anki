# Testes - Sheets2Anki

Esta pasta contém os testes para o add-on Sheets2Anki.

## Arquivos de Teste

### `test_structure.py`
- **Descrição:** Teste de verificação da estrutura do projeto
- **Função:** Verifica se todos os arquivos estão no local correto e se as correções de import foram aplicadas
- **Como executar:** `python tests/test_structure.py`

### `test_imports.py`
- **Descrição:** Teste de importação de módulos
- **Função:** Verifica se os módulos podem ser importados corretamente
- **Como executar:** `python tests/test_imports.py`

## Como Executar os Testes

### Do diretório raiz do projeto:
```bash
# Teste de estrutura
python tests/test_structure.py

# Teste de imports
python tests/test_imports.py
```

### Executar todos os testes:
```bash
# Executar ambos os testes
python tests/test_structure.py && python tests/test_imports.py
```

## O que os Testes Verificam

1. **Estrutura de Arquivos:**
   - Existência dos arquivos principais (`src/main.py`, `libs/org_to_anki/utils.py`, `__init__.py`)
   - Presença das funções necessárias nos arquivos corretos

2. **Correções de Import:**
   - Verificação de que os imports foram corrigidos para apontar para `src/` ao invés de `remote_decks/`
   - Confirmação de que o caminho das bibliotecas está correto

3. **Integridade do Código:**
   - Presença das funções principais: `import_test_deck`, `addNewDeck`, `syncDecksWithSelection`, `removeRemoteDeck`
   - Presença da função `getAnkiPluginConnector` no utils

## Status dos Testes

✅ **Todos os testes passando** - A estrutura do projeto está correta e o erro de importação foi resolvido.

## Notas Importantes

- Os testes são executados a partir do diretório raiz do projeto
- Alguns testes podem mostrar avisos sobre dependências ausentes (como `requests`) durante o desenvolvimento, mas isso é normal
- Os testes verificam a estrutura e imports, não a funcionalidade completa do add-on (que requer o ambiente Anki)
