# Correção do Bug de Contagem de Decks Sincronizados

## Problema Identificado

O show info após a sincronização dos decks sempre acusava **2 decks sincronizados**, independentemente do número real de decks que foram sincronizados.

## Causa Raiz

O bug estava na função `syncDecks()` no arquivo `src/main.py`, especificamente nas linhas 540-545:

### Código com Bug (ANTES):
```python
step, decks_synced, current_stats = _sync_single_deck(
    config, deckKey, progress, status_msgs, step
)

# Acumular estatísticas
_accumulate_stats(total_stats, current_stats)
decks_synced += 1  # ❌ BUG: dupla contagem!
```

**Problema:** A função `_sync_single_deck` retorna um valor na segunda posição (`1` para deck sincronizado, `0` para deck removido/não encontrado), mas esse valor estava sendo atribuído diretamente à variável `decks_synced`, sobrescrevendo a contagem acumulativa anterior. Em seguida, o código adicionava `+1` incondicionalmente, causando dupla contagem e sempre resultando em 2.

## Solução Implementada

### Código Corrigido (DEPOIS):
```python
step, deck_sync_increment, current_stats = _sync_single_deck(
    config, deckKey, progress, status_msgs, step
)

# Acumular estatísticas
_accumulate_stats(total_stats, current_stats)
decks_synced += deck_sync_increment  # ✅ CORRIGIDO: soma incremento correto
```

**Correção:** Mudamos a variável para `deck_sync_increment` para deixar claro que é um incremento, e usamos `+=` com esse valor ao invés de sobrescrever e incrementar.

## Comportamento da Função `_sync_single_deck`

A função retorna três valores:
1. `step` (atualizado)
2. **Incremento de decks sincronizados:**
   - `1` se o deck foi sincronizado com sucesso
   - `0` se o deck foi removido/não encontrado
3. `deck_stats` (estatísticas do deck)

## Teste de Validação

Foi criado o arquivo `tests/test_deck_sync_counting.py` que:

1. **Testa a lógica corrigida:** Simula sincronização de 4 decks (3 com sucesso, 1 removido) e verifica se resulta em 3 decks sincronizados
2. **Demonstra o bug anterior:** Mostra como o código anterior sempre resultava em 2, independente do número de decks

### Resultados do Teste:
```
✅ Contagem de decks sincronizados: 3 (correto)
✅ Cards criados: 10
✅ Cards atualizados: 3
✅ Cards deletados: 1

🐛 Resultado final (com bug): 2 decks
   ℹ️  Note que sempre resulta em 2, independente do número de decks
```

## Impacto da Correção

- ✅ **Contagem correta:** Agora mostra o número real de decks sincronizados
- ✅ **Transparência:** Usuário pode distinguir entre 1, 2, 3+ decks sincronizados
- ✅ **Consistência:** Contagem é precisa independente de quantos decks estão configurados
- ✅ **Debugging:** Facilita identificação de problemas durante sincronização

## Status

🎉 **PROBLEMA RESOLVIDO!** A contagem de decks sincronizados agora funciona corretamente.

## Data da Correção

**Data:** 9 de julho de 2025  
**Arquivo afetado:** `src/main.py` (linhas 540-545)  
**Teste criado:** `tests/test_deck_sync_counting.py`
