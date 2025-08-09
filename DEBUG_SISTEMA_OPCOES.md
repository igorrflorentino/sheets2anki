# DEBUG: Sistema de Opções de Deck

## Problema Identificado nos Logs

Análise do log de debug `debug_sheets2anki.log` mostrou que:

1. ✅ **Sistema de debug está ativo**: `debug: true` no meta.json
2. ✅ **Sincronização executou corretamente**: 7 notas processadas, sem erros
3. ❌ **Sistema de opções de deck NÃO foi executado**: Nenhuma mensagem `[DECK_OPTIONS]` nos logs

## Problema Identificado

A função `apply_automatic_deck_options_system()` estava sendo chamada no final da sincronização (`_finalize_sync_new`), mas:

- Não havia logs indicando sua execução
- Provavelmente estava falhando silenciosamente
- Sem tratamento adequado de erros e logs informativos

## Melhorias Implementadas

### 1. Logs de Debug Expandidos

**ADICIONADO**:
```python
print("[DECK_OPTIONS_SYSTEM] 🚀 INICIANDO sistema automático de opções de deck...")
print(f"[DECK_OPTIONS_SYSTEM] 📋 Modo atual: '{mode}'")
print("[DECK_OPTIONS_SYSTEM] 🎯 ETAPA 1: Configurando deck raiz...")
print("[DECK_OPTIONS_SYSTEM] 🎯 ETAPA 2: Configurando decks remotos...")  
print("[DECK_OPTIONS_SYSTEM] 🎯 ETAPA 3: Limpeza de grupos órfãos...")
print(f"[DECK_OPTIONS_SYSTEM] 🎉 CONCLUÍDO: {stats['message']}")
```

### 2. Tratamento de Erros Robusto

**ANTES**: Erros silenciosos ou capturas genéricas
**DEPOIS**: 
- Tratamento individual de cada etapa
- Traceback completo para debug
- Logs específicos para cada tipo de erro
- Retorno consistente mesmo em caso de falha

### 3. Verificações de Estado

**ADICIONADO**:
- Verificação de disponibilidade do Anki antes de executar
- Verificação específica do modo de configuração
- Logs informativos de cada resultado individual
- Tratamento específico quando modo é "manual"

### 4. Logs Estruturados por Etapa

Agora cada etapa é claramente identificada:

1. **ETAPA 1**: Configuração do deck raiz ("Sheets2Anki")
2. **ETAPA 2**: Configuração dos decks remotos  
3. **ETAPA 3**: Limpeza de grupos órfãos

### 5. Melhor Tratamento do Modo Manual

**ANTES**: Log simples
**DEPOIS**: Log detalhado e retorno estruturado com informações completas

## Configuração Atual Verificada

No `meta.json`:
```json
{
    "config": {
        "debug": true,
        "deck_options_mode": "shared"
    }
}
```

- ✅ Debug está ativo
- ✅ Modo é "shared" (não manual)  
- ✅ Sistema deveria executar automaticamente

## Próximos Passos para Teste

1. **Executar nova sincronização** no Anki
2. **Verificar logs** em `debug_sheets2anki.log`
3. **Procurar por**:
   - `[DECK_OPTIONS_SYSTEM] 🚀 INICIANDO`
   - Logs das 3 etapas 
   - Mensagem final de conclusão
4. **Verificar no Anki**:
   - Deck "Sheets2Anki" existe
   - Tem grupo "Sheets2Anki - Root Options" aplicado
   - Decks remotos têm grupo "Sheets2Anki - Default Options"

## Depuração Adicional

Se ainda não funcionar após essas melhorias, os logs expandidos vão mostrar exatamente onde está falhando:

- **Etapa 1 falha**: Problema com deck raiz
- **Etapa 2 falha**: Problema com decks remotos  
- **Etapa 3 falha**: Problema com limpeza
- **Nenhum log**: Problema na chamada da função

## Arquivo Atualizado

- ✅ `src/utils.py`: Função `apply_automatic_deck_options_system()` melhorada
- ✅ Logs expandidos em todas as funções relacionadas
- ✅ Tratamento de erros robusto
- ✅ Debug log limpo para próximo teste
