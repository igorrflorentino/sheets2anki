# Funcionalidade de Sincronização Seletiva com SYNC?

## Visão Geral

A funcionalidade de sincronização seletiva permite controlar individualmente quais questões são sincronizadas entre a planilha do Google Sheets e o Anki através da coluna **SYNC?**.

## Como Funciona

### 1. Nova Coluna SYNC?

A planilha agora deve incluir uma coluna chamada **SYNC?** que funciona como um checkbox:

- **Valores para sincronizar**: `true`, `1`, `sim`, `yes`, `verdadeiro`, `v`
- **Valores para NÃO sincronizar**: `false`, `0`, `não`, `nao`, `no`, `falso`, `f`
- **Valores não reconhecidos**: Por padrão, são considerados como "sincronizar" para manter compatibilidade

**✨ IMPORTANTE: A coluna SYNC? é completamente case insensitive!**
Você pode usar `TRUE`, `False`, `SIM`, `NÃO`, etc. Espaços também são ignorados.

### 2. Comportamento da Sincronização

#### Questões Marcadas para Sincronização (true/1)
- ✅ **Novas questões**: São criadas no Anki
- ✅ **Questões existentes**: São atualizadas com dados da planilha
- ✅ **Questões removidas da planilha**: São excluídas do Anki

#### Questões NÃO Marcadas para Sincronização (false/0)
- 🚫 **Novas questões**: São ignoradas, não são criadas no Anki
- 🔒 **Questões existentes**: Permanecem intactas no Anki, não são atualizadas
- 🔒 **Questões desmarcadas**: Não são excluídas do Anki, apenas param de ser sincronizadas

## Cenários de Uso

### Cenário 1: Questão Nova
```
Planilha: ID=001, PERGUNTA="Qual é a capital do Brasil?", LEVAR PARA PROVA="Brasília", SYNC?=true
Anki: Questão não existe
Resultado: ✅ Questão é criada no Anki
```

### Cenário 2: Questão Existente Atualizada
```
Planilha: ID=001, PERGUNTA="Qual é a capital do Brasil?", LEVAR PARA PROVA="Brasília", SYNC?=true
Anki: Questão existe com resposta antiga
Resultado: ✅ Questão é atualizada no Anki
```

### Cenário 3: Questão Desmarcada
```
Planilha: ID=001, PERGUNTA="Qual é a capital do Brasil?", LEVAR PARA PROVA="Brasília", SYNC?=false
Anki: Questão existe
Resultado: 🔒 Questão permanece intacta no Anki (não é atualizada nem excluída)
```

### Cenário 4: Questão Nova Desmarcada
```
Planilha: ID=001, PERGUNTA="Qual é a capital do Brasil?", LEVAR PARA PROVA="Brasília", SYNC?=false
Anki: Questão não existe
Resultado: 🚫 Questão é ignorada, não é criada no Anki
```

### Cenário 5: Questão Removida da Planilha
```
Planilha: Questão não existe mais
Anki: Questão existe
Resultado: ❌ Questão é excluída do Anki
```

## Implementação Técnica

### Arquivos Modificados

1. **`src/column_definitions.py`**
   - Adicionada constante `SYNC = 'SYNC?'`
   - Incluída na lista `REQUIRED_COLUMNS`
   - Adicionada função `should_sync_question()`

2. **`src/parseRemoteDeck.py`**
   - Modificada função `_process_tsv_row()` para filtrar questões não sincronizáveis
   - Questões com `SYNC?=false` são ignoradas durante o processamento

3. **`src/note_processor.py`**
   - Modificada função `create_or_update_notes()` para preservar notas existentes
   - Adicionada função `_get_all_question_keys_from_sheet()` para identificar questões ainda presentes na planilha
   - Lógica de exclusão modificada para não remover notas apenas desmarcadas

4. **`src/card_templates.py`**
   - Adicionado campo `SYNC?` no template dos cards
   - Campo aparece junto com `LEVAR PARA PROVA` no verso do card

### Lógica de Exclusão Inteligente

A implementação inclui uma lógica especial para exclusão que:

1. **Identifica todas as questões na planilha** (incluindo as não sincronizadas)
2. **Compara com questões existentes no Anki**
3. **Exclui apenas questões que foram completamente removidas da planilha**
4. **Preserva questões que existem na planilha mas não estão marcadas para sincronização**

## Compatibilidade

### Planilhas Existentes

- **Planilhas sem a coluna SYNC?**: Validação falhará até que a coluna seja adicionada
- **Planilhas com valores vazios**: Considerados como "sincronizar" (true)
- **Planilhas com valores não reconhecidos**: Considerados como "sincronizar" (true)

### Migração

Para migrar planilhas existentes:

1. Adicione a coluna **SYNC?** na planilha
2. Preencha com `true` ou `1` para todas as questões existentes
3. Use `false` ou `0` para questões que não devem ser sincronizadas

## Benefícios

- **Controle granular**: Sincronização individual por questão
- **Preservação de dados**: Notas existentes não são perdidas
- **Flexibilidade**: Permite diferentes estratégias de sincronização
- **Segurança**: Evita exclusões acidentais de questões apenas desmarcadas

## Exemplo de Uso

```csv
ID,PERGUNTA,LEVAR PARA PROVA,SYNC?,INFO COMPLEMENTAR,...
001,"Qual é a capital do Brasil?","Brasília",true,"Brasília é a capital",...
002,"Qual é a capital da França?","Paris",false,"Questão desatualizada",...
003,"Qual é a capital da Alemanha?","Berlim",1,"Berlim é a capital",...
004,"Qual é a capital da Espanha?","Madrid",0,"Questão em revisão",...
```

Neste exemplo:
- Questões 001 e 003 serão sincronizadas
- Questões 002 e 004 serão ignoradas, mas se já existirem no Anki, não serão excluídas
