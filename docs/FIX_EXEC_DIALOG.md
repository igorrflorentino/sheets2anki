# Correção do Erro exec_() - Qt Compatibility

## ✅ **Problema Identificado**
O erro `'GlobalStudentConfigDialog' object has no attribute 'exec_'` ocorreu porque:
- **Qt5**: Usa `dialog.exec_()`  
- **Qt6**: Usa `dialog.exec()` (sem underscore)

## ✅ **Solução Implementada**

### 1. **Função de compatibilidade já existia em `compat.py`**:
```python
def safe_exec_dialog(dialog) -> int:
    """
    Executa um diálogo de forma compatível entre versões do Qt.
    """
    if hasattr(dialog, "exec"):
        # Qt6 style
        return dialog.exec()
    else:
        # Qt5 style  
        return dialog.exec_()
```

### 2. **Corrigido import no `global_student_config_dialog.py`**:
```python
from .compat import (
    ..., safe_exec_dialog, DialogAccepted
)
```

### 3. **Substituído uso direto**:
```python
# Antes:
return dialog.exec_() == QDialog.Accepted

# Depois:  
return safe_exec_dialog(dialog) == DialogAccepted
```

## ✅ **Estado Atual**
- ✅ Função de compatibilidade para execução de diálogos implementada
- ✅ Import corrigido no global_student_config_dialog.py
- ✅ Uso da função compatível implementado
- ✅ Constantes de resultado de diálogo compatíveis (DialogAccepted)
- ✅ Compilação sem erros confirmada

## ✅ **Como Funciona**
- **Qt5**: Chama `dialog.exec_()` automaticamente
- **Qt6**: Chama `dialog.exec()` automaticamente
- **Compatibilidade**: Detecção automática da versão e método correto

## ✅ **Resultado**
O menu **Tools → Sheets2Anki → Configurar Alunos Globalmente** agora deve abrir e funcionar corretamente em ambas as versões do Qt.

## 🔧 **Próximo Teste**
Para verificar se ambos os problemas foram resolvidos:
1. Reiniciar o Anki
2. Ir em Tools → Sheets2Anki → Configurar Alunos Globalmente
3. A janela deve abrir sem erros de Qt.Horizontal nem exec_()
4. Interface deve ser funcional com listas drag-and-drop
