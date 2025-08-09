# Correção Crítica: Remoção Indevida de Notas

## 🚨 Problema Crítico Identificado

**Sintoma**: Quando o usuário clica "NÃO, MANTER DADOS" no diálogo de confirmação de limpeza, as notas dos alunos desabilitados eram deletadas mesmo assim.

**Gravidade**: ALTA - Perda de dados mesmo com negativa explícita do usuário.

## 🔍 Análise da Causa Raiz

### Local do Problema:
`src/data_processor.py`, função `create_or_update_notes()`, linhas 649-655

### Fluxo Problemático:

1. **Usuário desabilita aluno "pedro"** na configuração
2. **Sync é executado** normalmente
3. **Durante sync**: `expected_student_note_ids` é construído apenas com alunos habilitados
4. **Notas de "pedro" NÃO aparecem** em `expected_student_note_ids` 
5. **Sistema considera notas de "pedro" como "obsoletas"**
6. **Notas são REMOVIDAS automaticamente** na linha 649-655
7. **Diálogo de confirmação aparece DEPOIS** (para note types e decks)
8. **Mesmo clicando "NÃO"**, as notas já foram deletadas

### Código Problemático:

```python
# Linha 649: REMOÇÃO AUTOMÁTICA sem confirmação
notes_to_delete = set(existing_notes.keys()) - expected_student_note_ids
add_debug_msg(f"Removendo {len(notes_to_delete)} notas obsoletas")

for student_note_id in notes_to_delete:
    # DELETANDO NOTAS SEM CONFIRMAÇÃO!
    if delete_note_by_id(col, existing_notes[student_note_id]):
        stats['deleted'] += 1
```

## ✅ Solução Implementada

### Lógica Corrigida:

1. **Verificar se auto-remove está ativo**
2. **Se ativo**: Preservar notas de alunos conhecidos (mesmo desabilitados)
3. **Só remover**: Notas de alunos verdadeiramente desconhecidos
4. **Deixar limpeza de alunos desabilitados**: Para o processo com confirmação

### Código da Correção:

```python
# Filtrar para não remover notas de alunos desabilitados se auto-remove estiver ativo
from .config_manager import is_auto_remove_disabled_students
if is_auto_remove_disabled_students():
    # Preservar notas de alunos conhecidos para processo de confirmação
    filtered_notes_to_delete = set()
    all_known_students = enabled_students.union(available_students)
    
    for student_note_id in notes_to_delete:
        student = student_note_id.split('_')[0] 
        # Só remover se não for de nenhum aluno conhecido
        if student not in all_known_students and student != "[MISSING A.]":
            filtered_notes_to_delete.add(student_note_id)
        else:
            # PRESERVAR nota de aluno conhecido
            add_debug_msg(f"Nota {student_note_id}: preservada (aluno conhecido)")
```

## 🎯 Comportamento Corrigido

### Antes (PROBLEMÁTICO):
```
1. Usuário desabilita "pedro"
2. Sync executa
3. Notas de "pedro" são DELETADAS automaticamente
4. Diálogo aparece para note types
5. Usuário clica "NÃO, MANTER DADOS"  
6. Note types são preservados, mas NOTAS JÁ FORAM DELETADAS
```

### Depois (CORRETO):
```
1. Usuário desabilita "pedro" 
2. Sync executa
3. Notas de "pedro" são PRESERVADAS (não são obsoletas)
4. Diálogo aparece para limpeza completa
5. Usuário clica "NÃO, MANTER DADOS"
6. TODOS os dados (notas + note types + decks) são preservados
```

## 🧪 Casos de Teste

### Caso 1: Auto-remove ATIVO + Usuário cancela
- **Resultado**: Nenhuma nota deve ser removida
- **Verificar**: Contar notas antes/depois da negativa

### Caso 2: Auto-remove INATIVO 
- **Resultado**: Comportamento normal (remove notas obsoletas reais)
- **Verificar**: Notas de planilhas antigas são removidas

### Caso 3: Auto-remove ATIVO + Usuário confirma
- **Resultado**: Limpeza completa após confirmação
- **Verificar**: Notas + note types + decks removidos

## 📊 Logs de Debug

Para identificar o comportamento, observar logs:

```
# ANTES da correção:
"Removendo 15 notas obsoletas"  ← PROBLEMA: Removendo sem confirmação

# DEPOIS da correção:
"Auto-remove ativo: preservando notas de alunos conhecidos, removendo apenas 0 realmente obsoletas"
"Nota pedro_123: preservada (aluno conhecido)"
```

## ⚠️ Impacto da Correção

- **Segurança**: Elimina perda acidental de dados
- **Consistência**: Diálogo de confirmação agora reflete ação real
- **Confiabilidade**: Usuário tem controle total sobre remoção de dados
- **Compatibilidade**: Mantém funcionalidade normal para casos sem auto-remove

---

**Status**: ✅ CORRIGIDO - Problema crítico resolvido
**Arquivos Modificados**: `src/data_processor.py`  
**Função Corrigida**: `create_or_update_notes()`
**Prioridade**: CRÍTICA - Deploy imediato recomendado
