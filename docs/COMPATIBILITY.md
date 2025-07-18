# Notas de Compatibilidade - Sheets2Anki

Este documento descreve problemas de compatibilidade conhecidos e suas soluções no projeto Sheets2Anki.

## Compatibilidade com Qt/PyQt/PySide

### Problema: QAbstractItemView.MultiSelection

**Descrição do problema:**
Em versões mais recentes do Qt (Qt6+), as constantes de seleção como `MultiSelection` foram movidas para dentro de uma classe enum chamada `SelectionMode`. Isso causa erros em código que usa diretamente `QAbstractItemView.MultiSelection`.

**Erro típico:**
```
O erro foi: type object 'QAbstractItemView' has no attribute 'MultiSelection'.
```

**Solução implementada:**
Foi criado um módulo de compatibilidade (`src/fix_multiselection.py`) que detecta a versão do Qt e fornece constantes compatíveis:

```python
# Importar constantes de seleção compatíveis
from .fix_multiselection import MULTI_SELECTION

# Usar a constante compatível
self.deck_list.setSelectionMode(MULTI_SELECTION)
```

### Problema: dialog.exec_() vs dialog.exec()

**Descrição do problema:**
Em versões mais recentes do Qt (Qt6+), o método `exec_()` foi substituído por `exec()`. Isso causa erros em código que usa diretamente `dialog.exec_()`.

**Erro típico:**
```
O erro foi: 'BackupDialog' object has no attribute 'exec_'.
```

**Solução implementada:**
Foi criado um módulo de compatibilidade (`src/fix_exec.py`) que fornece uma função para executar diálogos de forma compatível:

```python
# Importar função de compatibilidade
from .fix_exec import safe_exec

# Usar a função compatível
result = safe_exec(dialog)
```

### Problema: QFrame.HLine e QFrame.Sunken

**Descrição do problema:**
Similar ao problema anterior, em versões mais recentes do Qt, as constantes de QFrame foram movidas para classes enum.

**Solução implementada:**
O código já contém tratamento para isso com fallbacks:

```python
try:
    # Tentar Qt6+ primeiro (enums tipados)
    FRAME_HLINE = QFrame.Shape.HLine
    FRAME_SUNKEN = QFrame.Shadow.Sunken
except AttributeError:
    try:
        # Tentar Qt5 (constantes de classe)
        FRAME_HLINE = QFrame.HLine
        FRAME_SUNKEN = QFrame.Sunken
    except AttributeError:
        # Fallback para valores numéricos
        FRAME_HLINE = 4
        FRAME_SUNKEN = 2
```

## Compatibilidade com Anki

### Versões suportadas

- Anki 2.1.35+
- Anki 2.1.40+
- Anki 2.1.50+
- Anki 23.10+
- Anki 23.12+
- Anki 24.04+

### Problemas conhecidos

- Em versões muito antigas do Anki (anteriores a 2.1.35), algumas funcionalidades podem não funcionar corretamente.
- Em versões muito recentes do Anki, podem surgir novos problemas de compatibilidade que ainda não foram tratados.

## Como testar compatibilidade

Para verificar se as soluções de compatibilidade estão funcionando:

```bash
# Teste de compatibilidade de QAbstractItemView.MultiSelection
python test_fix_multiselection.py

# Teste de compatibilidade de QFrame
python test_qframe.py
```

## Adicionando novas soluções de compatibilidade

Se você encontrar novos problemas de compatibilidade:

1. Crie um módulo de compatibilidade em `src/` (ex: `fix_newproblem.py`)
2. Implemente detecção de versão e fallbacks
3. Exporte constantes ou funções compatíveis
4. Atualize o código para usar essas constantes/funções
5. Adicione testes para verificar a solução
6. Documente o problema e a solução neste arquivo