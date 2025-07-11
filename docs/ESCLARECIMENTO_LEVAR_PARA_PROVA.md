# Esclarecimento sobre a Coluna 'LEVAR PARA PROVA'

## ⚠️ Correção Importante

A coluna **'LEVAR PARA PROVA'** foi inicialmente mal documentada. Aqui está o **uso correto**:

## ✅ Uso Correto da Coluna 'LEVAR PARA PROVA'

### Propósito
A coluna **'LEVAR PARA PROVA'** deve conter a **resposta sucinta e atômica** da pergunta, representando o núcleo da resposta de forma mais concisa possível.

### Função
- **NÃO é um campo de sim/não**
- **NÃO é um campo de filtro**
- **É um campo de texto** que contém a resposta principal da questão

### Exemplos Corretos

| PERGUNTA | LEVAR PARA PROVA | Explicação |
|----------|------------------|------------|
| Qual é a capital do Brasil? | Brasília | Resposta direta e atômica |
| Quem foi o primeiro presidente do Brasil? | Deodoro da Fonseca | Nome completo da pessoa |
| Qual é a fórmula da água? | H2O | Fórmula química exata |
| Qual é a velocidade da luz? | 299.792.458 m/s | Valor numérico preciso |
| Qual é o símbolo químico do ouro? | Au | Símbolo químico |
| Quantos continentes existem? | 6 continentes | Número + unidade |

### Exemplos Incorretos

| PERGUNTA | ❌ INCORRETO | ✅ CORRETO |
|----------|-------------|------------|
| Qual é a capital do Brasil? | Sim | Brasília |
| Quem foi o primeiro presidente? | Importante | Deodoro da Fonseca |
| Qual é a fórmula da água? | Não | H2O |
| Qual é a velocidade da luz? | Levar | 299.792.458 m/s |

## 🎯 Diferença Entre as Colunas

### PERGUNTA
- **Função**: Texto completo da questão/frente do card
- **Exemplo**: "Qual é a capital do Brasil?"

### LEVAR PARA PROVA
- **Função**: Resposta sucinta e atômica (núcleo da resposta)
- **Exemplo**: "Brasília"

### SYNC?
- **Função**: Controle de sincronização (true/false, 1/0)
- **Exemplo**: "true" ou "false"

## 📋 Estrutura Correta do Card

Com essas informações, um card típico seria:

**Frente (Pergunta):**
```
Qual é a capital do Brasil?
```

**Verso (Resposta):**
```
Brasília

[Informações complementares detalhadas...]
```

## 🔧 Impacto no Sistema

### No Template do Card
A coluna 'LEVAR PARA PROVA' aparece como parte da resposta no verso do card, contendo o núcleo da informação que deve ser lembrada.

### Na Sincronização
- A coluna é tratada como **campo de texto** (não como filtro)
- É incluída nos **TEXT_FIELDS** para processamento adequado
- Faz parte do conteúdo sincronizado entre planilha e Anki

## 🔄 Migração de Planilhas Existentes

Se você tem planilhas com uso incorreto da coluna 'LEVAR PARA PROVA':

1. **Identifique valores inadequados**: "Sim", "Não", "Importante", etc.
2. **Substitua pela resposta real**: A resposta efetiva da pergunta
3. **Mantenha conciso**: Use a forma mais atômica possível
4. **Teste a sincronização**: Verifique se os cards ficaram adequados

## 💡 Dicas de Uso

### Para Respostas Numéricas
- **Pergunta**: "Quantos estados tem o Brasil?"
- **LEVAR PARA PROVA**: "26 estados + 1 DF"

### Para Respostas Conceituais
- **Pergunta**: "O que é fotossíntese?"
- **LEVAR PARA PROVA**: "Processo de produção de energia pelas plantas usando luz solar"

### Para Respostas Factuais
- **Pergunta**: "Quando foi proclamada a República no Brasil?"
- **LEVAR PARA PROVA**: "15 de novembro de 1889"

## ✅ Resumo

A coluna **'LEVAR PARA PROVA'** é fundamentalmente diferente da coluna **'SYNC?'**:

- **'LEVAR PARA PROVA'** = Conteúdo (resposta da pergunta)
- **'SYNC?'** = Controle (sincronizar ou não)

Esta distinção é crucial para o funcionamento correto do sistema de sincronização.
