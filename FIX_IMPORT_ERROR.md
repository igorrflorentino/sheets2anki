# 🔧 CORREÇÃO DO ERRO DE IMPORTAÇÃO

## ❌ Problema Identificado
```
Erro ao importar módulos do plugin Sheets2Anki:
cannot import name 'show_backup_dialog' from 'sheets2anki.src.backup_system'
```

## ✅ Causa Raiz
Durante a limpeza do código legado, a função `show_backup_dialog` foi movida do arquivo `backup_system.py` para `backup_dialog.py`, mas uma importação no arquivo principal `__init__.py` não foi atualizada.

## 🔧 Correção Aplicada

### Arquivo Modificado: `__init__.py` (linha 60)

**❌ ANTES (importação incorreta):**
```python
from .src.backup_system import show_backup_dialog
```

**✅ DEPOIS (importação corrigida):**
```python
from .src.backup_dialog import show_backup_dialog
```

## 🧪 Validação Completa

**Testes Realizados:**
- ✅ **3/3 testes passaram**
- ✅ `show_backup_dialog` importa corretamente de `backup_dialog.py`
- ✅ `backup_system.py` não contém mais `show_backup_dialog` (apenas `SimplifiedBackupManager`)
- ✅ `backup_dialog.py` contém `show_backup_dialog` e `BackupDialog`
- ✅ Novo pacote `.ankiaddon` gerado com correção

## 📦 Ação Necessária

Para resolver o erro definitivamente:

1. **Desinstale a versão atual** do plugin Sheets2Anki no Anki
2. **Instale a nova versão** usando um dos arquivos gerados:
   - `build/sheets2anki.ankiaddon` (versão AnkiWeb)
   - `build/sheets2anki-standalone.ankiaddon` (versão standalone)

## 🎯 Status
**✅ PROBLEMA CORRIGIDO E VALIDADO**

A importação está agora correta e o novo pacote contém todas as correções aplicadas. O erro não deve mais ocorrer após a reinstalação.
