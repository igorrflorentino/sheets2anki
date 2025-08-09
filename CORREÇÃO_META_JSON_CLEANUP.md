# Correção: Atualização do meta.json Após Cleanup

## 🐛 Problema Identificado

**Sintoma**: Quando o usuário confirma a remoção de dados (clica "SIM, DELETAR DADOS"), os dados são corretamente removidos do Anki (notas, note types, decks), mas o dicionário `note_types` no `meta.json` não é atualizado para refletir o novo estado.

**Resultado**: `meta.json` mantém referências a note types que já foram deletados do Anki.

## 🔍 Análise do Problema

### Estado Antes da Correção:

1. **Usuário confirma remoção** de aluno "pedro"
2. **Anki é limpo com sucesso**:
   - ✅ Notas removidas
   - ✅ Note types removidos
   - ✅ Decks removidos
3. **meta.json NÃO atualizado**:
   - ❌ Ainda contém `"1754712999217": "Sheets2Anki - #0 Template - pedro - Basic"`
   - ❌ Ainda contém `"1754712999218": "Sheets2Anki - #0 Template - pedro - Cloze"`

### Causa Raiz:

As funções de cleanup (`cleanup_disabled_students_data` e `cleanup_missing_students_data`) removem dados do Anki mas não atualizam o arquivo `meta.json` que mantém o mapeamento de IDs para nomes dos note types.

## ✅ Solução Implementada

### 1. Nova Função: `_update_meta_after_cleanup()`

```python
def _update_meta_after_cleanup(disabled_students: Set[str], deck_names: List[str]) -> None:
    """
    Atualiza o meta.json removendo referências de note types que foram deletados.
    """
    meta = get_meta()
    updates_made = False
    
    # Para cada deck configurado
    for deck_info in meta.get('decks', {}).values():
        deck_name = deck_info.get('remote_deck_name', '')
        if deck_name in deck_names:
            note_types_dict = deck_info.get('note_types', {})
            note_types_to_remove = []
            
            # Encontrar note types dos alunos desabilitados
            for note_type_id, note_type_name in note_types_dict.items():
                for student in disabled_students:
                    student_pattern_basic = f"Sheets2Anki - {deck_name} - {student} - Basic"
                    student_pattern_cloze = f"Sheets2Anki - {deck_name} - {student} - Cloze"
                    
                    if note_type_name == student_pattern_basic or note_type_name == student_pattern_cloze:
                        note_types_to_remove.append(note_type_id)
            
            # Remover os note types encontrados
            for note_type_id in note_types_to_remove:
                if note_type_id in note_types_dict:
                    del note_types_dict[note_type_id]
                    updates_made = True
    
    # Salvar meta.json atualizado
    if updates_made:
        save_meta(meta)
```

### 2. Nova Função: `_update_meta_after_missing_cleanup()`

```python
def _update_meta_after_missing_cleanup(deck_names: List[str]) -> None:
    """
    Atualiza o meta.json removendo referências de note types [MISSING A.] deletados.
    """
    # Lógica similar, mas específica para [MISSING A.]
```

### 3. Integração nos Processos de Cleanup:

```python
# Em cleanup_disabled_students_data():
cleanup_disabled_students_data(disabled_students, deck_names)
_update_meta_after_cleanup(disabled_students, deck_names)  # NOVO
col.save()

# Em cleanup_missing_students_data():
# ... limpeza dos dados ...
_update_meta_after_missing_cleanup(deck_names)  # NOVO
return stats
```

## 🎯 Comportamento Corrigido

### Antes (INCONSISTENTE):
```json
// meta.json após remoção do aluno "pedro"
{
  "note_types": {
    "1754712999217": "Sheets2Anki - #0 Template - pedro - Basic",    // ❌ ÓRFÃO
    "1754712999218": "Sheets2Anki - #0 Template - pedro - Cloze",     // ❌ ÓRFÃO  
    "1754712999215": "Sheets2Anki - #0 Template - Belle - Basic",     // ✅ OK
    "1754712999216": "Sheets2Anki - #0 Template - Belle - Cloze"      // ✅ OK
  }
}
```

### Depois (CONSISTENTE):
```json
// meta.json após remoção do aluno "pedro"
{
  "note_types": {
    "1754712999215": "Sheets2Anki - #0 Template - Belle - Basic",     // ✅ OK
    "1754712999216": "Sheets2Anki - #0 Template - Belle - Cloze"      // ✅ OK
  }
}
```

## 📊 Logs de Debug

Para verificar o funcionamento, observar logs:

```
🗑️ CLEANUP: Iniciando limpeza de dados para alunos: ['pedro']
🧹 CLEANUP: Processando aluno 'pedro'...
🗑️ Note type 'Sheets2Anki - #0 Template - pedro - Basic' removido
🗑️ Note type 'Sheets2Anki - #0 Template - pedro - Cloze' removido
📝 META UPDATE: Atualizando meta.json após limpeza de 1 alunos
🗑️ META: Removendo referência do note type 'Sheets2Anki - #0 Template - pedro - Basic' (ID: 1754712999217)
🗑️ META: Removendo referência do note type 'Sheets2Anki - #0 Template - pedro - Cloze' (ID: 1754712999218)
✅ META UPDATE: meta.json atualizado com 4 note types restantes
```

## 🧪 Casos de Teste

### Teste 1: Remoção de Aluno
1. Desabilitar aluno "pedro"
2. Confirmar remoção 
3. **Verificar**: `meta.json` não deve conter referências a note types de "pedro"

### Teste 2: Remoção de [MISSING A.]
1. Desabilitar funcionalidade [MISSING A.]
2. Confirmar remoção
3. **Verificar**: `meta.json` não deve conter referências a note types [MISSING A.]

### Teste 3: Cancelamento
1. Desabilitar aluno
2. **Cancelar** remoção
3. **Verificar**: `meta.json` deve permanecer inalterado

## ⚠️ Benefícios da Correção

- **Consistência**: meta.json sempre reflete o estado real do Anki
- **Limpeza**: Elimina referências órfãs a note types deletados
- **Confiabilidade**: Evita confusão entre estado do arquivo e do Anki
- **Debug**: Facilita troubleshooting com dados consistentes

---

**Status**: ✅ IMPLEMENTADO
**Arquivos Modificados**: `src/student_manager.py`
**Funções Adicionadas**: `_update_meta_after_cleanup()`, `_update_meta_after_missing_cleanup()`
**Integração**: Chamadas automáticas após cada processo de cleanup
