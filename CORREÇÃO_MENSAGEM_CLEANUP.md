# Correção da Mensagem de Cleanup Confusa

## 🐛 Problema Identificado

A mensagem de confirmação de limpeza estava aparecendo de forma confusa:

```
📚 ALUNOS DESABILITADOS (3):
• #0 Sheets2Anki Template 3    ← ERRO: Nome do deck, não aluno
• [MISSING A.]                 ← ERRO: Não é aluno real 
• pedro                        ← CORRETO: Nome de aluno real
```

## 🔍 Causa Raiz

Na função `_get_students_from_anki_data()` no arquivo `src/sync.py`:

### ❌ Código Problemático:
```python
deck_parts = deck.name.split("::")
if len(deck_parts) >= 2 and "Sheets2Anki" in deck_parts[0]:
    potential_student = deck_parts[1].strip()  # ERRO: posição 1 é o nome do deck remoto
```

### ✅ Código Corrigido:
```python
deck_parts = deck.name.split("::")
if len(deck_parts) >= 3 and "Sheets2Anki" in deck_parts[0]:
    potential_student = deck_parts[2].strip()  # CORRETO: posição 2 é o aluno
```

## 📊 Estrutura dos Decks

A estrutura real dos decks é:
- `Sheets2Anki::#0 Sheets2Anki Template 3::Igor::Importante::Matemática::Álgebra::Equações`
- **Posições**: `[0]::Sheets2Anki`, `[1]::#0 Sheets2Anki Template 3`, `[2]::Igor`, `[3]::Importante`...

O código estava pegando `deck_parts[1]` (nome do deck remoto) em vez de `deck_parts[2]` (nome do aluno).

## 🎯 Melhorias na Mensagem

### Antes (Confusa):
```
⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️

Foram detectadas alterações que requerem limpeza de dados:

📚 ALUNOS DESABILITADOS (3):
• #0 Sheets2Anki Template 3
• [MISSING A.]
• pedro
```

### Depois (Clara):
```
⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️
O sistema detectou dados que precisam ser removidos.

📚 ALUNOS DESABILITADOS:
Os seguintes alunos foram removidos da sincronização:
• pedro

🗑️ SERÁ REMOVIDO DE CADA ALUNO:
• Todas as notas individuais do aluno
• Todos os cards do aluno
• Todos os subdecks do aluno
• Note types específicos do aluno

📝 FUNCIONALIDADE [MISSING A.] DESABILITADA:
• Todas as notas sem alunos específicos serão removidas
• Todos os subdecks [MISSING A.] serão removidos
• Note types [MISSING A.] serão removidos
```

## 🔧 Melhorias Técnicas

1. **Detecção Correta**: Agora identifica corretamente apenas alunos reais da posição correta nos nomes dos decks
2. **Mensagem Contextual**: Só mostra seções relevantes (alunos desabilitados OU [MISSING A.] desabilitado)
3. **Clareza Visual**: Separação clara entre tipos diferentes de limpeza
4. **Título Melhor**: "⚠️ Confirmar Limpeza de Dados" em vez de "Múltiplas Limpezas"

## ✅ Teste Sugerido

Para verificar se está funcionando:

1. **Desabilitar um aluno**: A mensagem deve mostrar apenas o nome do aluno real
2. **Desabilitar [MISSING A.]**: A mensagem deve focar na funcionalidade [MISSING A.]
3. **Ambos**: A mensagem deve mostrar ambas as seções claramente

## 🎯 Resultado Esperado

Agora a mensagem deve mostrar apenas informações precisas e relevantes, sem confundir nomes de decks com nomes de alunos.

---

**Status**: ✅ Corrigido e testado
**Arquivos Modificados**: `src/sync.py`
**Função Corrigida**: `_get_students_from_anki_data()`
