# Sincronização Seletiva para Novos Decks

## Problema Identificado
Quando um usuário cadastrava uma nova planilha para sincronização, o sistema sincronizava automaticamente TODOS os decks já configurados, não apenas o novo deck recém-cadastrado.

## Solução Implementada
Modificamos o comportamento das funções `addNewDeck()` e `import_test_deck()` para que sincronizem apenas o deck recém-cadastrado/importado.

### Mudanças Realizadas

#### 1. Função `addNewDeck()`
- **Antes**: Chamava `syncDecks()` sem parâmetros, sincronizando todos os decks
- **Depois**: Chama `syncDecks(selected_deck_urls=[url])` para sincronizar apenas o deck recém-cadastrado

#### 2. Função `import_test_deck()`
- **Antes**: Chamava `syncDecks()` sem parâmetros, sincronizando todos os decks
- **Depois**: Chama `syncDecks(selected_deck_urls=[url])` para sincronizar apenas o deck de teste importado

#### 3. Função `syncDecks()`
- **Modificada**: Adicionado parâmetro `selected_deck_urls` para permitir sincronização por URL
- **Benefício**: Elimina problemas de mapeamento de nomes de deck no momento da criação

#### 4. Documentação Atualizada
- Adicionadas notas nas documentações das funções explicando que apenas o novo deck será sincronizado
- Esclarecimento sobre o comportamento não afetar outros decks previamente configurados

## Funcionalidade Preservada
- A função `syncDecksWithSelection()` continua funcionando normalmente
- Quando há apenas um deck configurado, ainda é sincronizado diretamente
- A sincronização manual de decks selecionados não foi alterada

## Benefícios
1. **Performance**: Reduz o tempo de sincronização ao cadastrar novos decks
2. **Controle**: Usuário tem controle sobre quais decks sincronizar
3. **Experiência**: Melhora a experiência do usuário ao cadastrar novos decks
4. **Previsibilidade**: Comportamento mais previsível e intuitivo

## Arquivos Modificados
- `src/deck_manager.py`: Alteração nas funções `addNewDeck()` e `import_test_deck()`
- `src/sync.py`: Adição do parâmetro `selected_deck_urls` à função `syncDecks()`
- `docs/SINCRONIZACAO_SELETIVA.md`: Documentação da mudança (este arquivo)

## Correção de Bug
Durante a implementação, foi identificado um problema de timing onde o mapeamento de nomes de deck para URLs não funcionava corretamente logo após a criação do deck. A solução foi modificar a função `syncDecks()` para aceitar URLs diretamente, eliminando a necessidade de mapeamento de nomes no momento da criação.
