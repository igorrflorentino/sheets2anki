# Sample Data / Dados de Exemplo

Esta pasta contém arquivos de dados de exemplo para testes e demonstração do addon Sheets2Anki.

## Arquivos

### `exemplo_planilha_com_sync.tsv`
- **Descrição**: Exemplo de planilha com dados sincronizados
- **Uso**: Demonstração do formato de dados esperado pelo addon
- **Características**: Contém exemplos de cards com formatação e sincronização

### `test_formula_errors_data.tsv`
- **Descrição**: Dados de teste para verificar tratamento de erros em fórmulas
- **Uso**: Testes de validação e tratamento de erros
- **Características**: Contém exemplos de fórmulas com erros para testar robustez

### `test_sheet.tsv`
- **Descrição**: Planilha de teste básica
- **Uso**: Testes gerais de funcionalidade
- **Características**: Dados simples para testes de importação e sincronização

## Formato dos Arquivos

Todos os arquivos TSV (Tab-Separated Values) seguem o formato padrão esperado pelo Sheets2Anki:

```
Front	Back	SYNC?	Tags	Note Type
Pergunta 1	Resposta 1	sim	tag1,tag2	Basic
Pergunta 2	Resposta 2	sim	tag3	Basic
```

## Como Usar

Estes arquivos podem ser:
1. **Importados diretamente** no Anki para teste
2. **Usados como referência** para criar suas próprias planilhas
3. **Utilizados em testes** automáticos do addon

## Nota

Estes arquivos são apenas para exemplo e teste. Para uso em produção, crie suas próprias planilhas no Google Sheets seguindo o formato documentado.
