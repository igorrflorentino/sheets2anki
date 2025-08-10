# Sample Data - Sheets2Anki

Este diretório contém dados de exemplo para testes do addon Sheets2Anki.

## sample_sheet.tsv

Arquivo consolidado contendo dados de teste no formato TSV (Tab-Separated Values) que segue o padrão esperado pelo addon.

### Estrutura das Colunas

O arquivo possui as seguintes colunas obrigatórias:

- **ID**: Identificador único da questão
- **PERGUNTA**: Texto principal da questão/frente do cartão  
- **LEVAR PARA PROVA**: Resposta sucinta e atômica da pergunta
- **SYNC?**: Campo de controle de sincronização (true/false/1/0)
- **ALUNOS**: Indica quais alunos têm interesse em estudar esta nota
- **INFO COMPLEMENTAR**: Informação complementar básica
- **INFO DETALHADA**: Informação detalhada adicional
- **EXEMPLO 1**, **EXEMPLO 2**, **EXEMPLO 3**: Exemplos relacionados à questão
- **TOPICO**: Tópico principal da questão
- **SUBTOPICO**: Subtópico específico
- **CONCEITO**: Conceito atômico sendo perguntado
- **BANCAS**: Bancas organizadoras relacionadas
- **ULTIMO ANO EM PROVA**: Último ano em que apareceu em prova
- **CARREIRA**: Carreira ou área profissional relacionada
- **IMPORTANCIA**: Nível de importância da questão
- **TAGS ADICIONAIS**: Tags adicionais para organização

### Casos de Teste Incluídos

O arquivo contém diferentes cenários de teste:

1. **Teste básico de sincronização**: Questões com diferentes valores de SYNC?
2. **Teste de alunos**: Questões com e sem alunos específicos
3. **Teste de erros**: Tratamento de erros de fórmula (#NAME?, #REF!, etc.)
4. **Teste de case insensitive**: Diferentes formas de especificar valores booleanos
5. **Teste de workflow completo**: Dados para testar todo o fluxo do addon

### Uso

Este arquivo pode ser usado para:

- Testes de desenvolvimento do addon
- Validação de funcionalidades
- Demonstração de casos de uso
- Depuração de problemas

Para usar em testes, publique este conteúdo como uma planilha no Google Sheets e use a URL de publicação TSV no addon.
