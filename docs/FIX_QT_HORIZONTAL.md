# Resumo de Correção - Erro Qt.Horizontal

## ✅ **Problema Identificado**
O erro `type object 'Qt' has no attribute 'Horizontal'` ocorreu porque:
1. A constante `Qt.Horizontal` não estava sendo importada/exportada no módulo de compatibilidade
2. As diferentes versões do Qt (Qt5 vs Qt6) têm namespaces diferentes para essas constantes

## ✅ **Solução Implementada**

### 1. **Adicionadas constantes de orientação no `src/compat.py`**:
```python
# Constantes de orientação
if QT_VERSION >= 6:
    Horizontal = Qt.Orientation.Horizontal
    Vertical = Qt.Orientation.Vertical
else:
    Horizontal = Qt.Horizontal
    Vertical = Qt.Vertical
```

### 2. **Corrigido import no `src/global_student_config_dialog.py`**:
```python
from .compat import (
    ..., Horizontal
)
```

### 3. **Substituído uso direto**:
```python
# Antes:
splitter = QSplitter(Qt.Horizontal)

# Depois:
splitter = QSplitter(Horizontal)
```

## ✅ **Como Funciona**
- **Qt5**: `Horizontal = Qt.Horizontal`
- **Qt6**: `Horizontal = Qt.Orientation.Horizontal` 
- **Compatibilidade**: Funciona em ambas as versões automaticamente

## ✅ **Estado Atual**
- ✅ Constantes de orientação adicionadas ao compat.py
- ✅ Import corrigido no global_student_config_dialog.py  
- ✅ Uso da constante compatível implementado
- ✅ Compilação sem erros confirmada

## ✅ **Resultado**
O menu **Tools → Sheets2Anki → Configurar Alunos Globalmente** deve abrir corretamente agora, sem o erro `Qt.Horizontal`.

## 🔧 **Teste no Anki**
Para verificar se o problema foi resolvido:
1. Reinicie o Anki
2. Vá em Tools → Sheets2Anki → Configurar Alunos Globalmente  
3. A janela de configuração deve abrir normalmente
4. Interface com listas de alunos disponíveis/selecionados deve aparecer
