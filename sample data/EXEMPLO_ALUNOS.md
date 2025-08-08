# Exemplo de Planilha com Coluna ALUNOS

Este arquivo demonstra como estruturar uma planilha Google Sheets para usar a funcionalidade de gerenciamento de alunos do Sheets2Anki.

## Estrutura da Planilha

A planilha deve conter todas as colunas obrigatórias, incluindo a nova coluna `ALUNOS`:

| ID | PERGUNTA | LEVAR PARA PROVA | SYNC? | ALUNOS | TOPICO | SUBTOPICO | CONCEITO | IMPORTANCIA | ... |
|----|----------|------------------|-------|--------|--------|-----------|----------|-------------|-----|
| 1 | Qual é a definição de contrato? | Acordo de vontades que cria obrigações | 1 | João | Direito Civil | Contratos | Definição | Alta | ... |
| 2 | Como se calcula juros compostos? | J = C × [(1+i)^n - 1] | 1 | Maria | Matemática | Financeira | Fórmulas | Média | ... |
| 3 | O que é mitose? | Divisão celular que produz células idênticas | 1 | João,Maria | Biologia | Citologia | Reprodução | Alta | ... |
| 4 | Defina democracia | Governo do povo pelo povo | 0 | Pedro | História | Política | Sistemas | Baixa | ... |

## Detalhes da Coluna ALUNOS

### Formato Aceito
A coluna ALUNOS pode conter:
- **Um único aluno**: `João`
- **Múltiplos alunos separados por vírgula**: `João, Maria`
- **Múltiplos alunos separados por ponto e vírgula**: `João; Maria; Pedro`
- **Múltiplos alunos separados por pipe**: `João|Maria|Pedro`
- **Combinações**: `João, Maria|Pedro` (será interpretado como três alunos)

### Casos Especiais
- **Célula vazia**: A questão não será associada a nenhum aluno específico
- **Espaços extras**: São automaticamente removidos (`" João , Maria "` vira `["João", "Maria"]`)
- **Case sensitive**: `João` e `joão` são considerados alunos diferentes
- **Caracteres especiais**: Suportados normalmente (`João-Silva`, `Maria_Santos`)

## Exemplo Prático de Colaboração

### Cenário
Uma turma de Direito está preparando questões colaborativamente:
- **João**: Foca em Direito Civil
- **Maria**: Especialista em Direito Penal  
- **Pedro**: Estuda Direito Constitucional
- **Ana**: Contribui em várias áreas

### Planilha Colaborativa

| ID | PERGUNTA | LEVAR PARA PROVA | SYNC? | ALUNO | TOPICO | SUBTOPICO | CONCEITO |
|----|----------|------------------|-------|--------|--------|-----------|----------|
| 1 | O que caracteriza o dolo eventual? | Assumir o risco de produzir o resultado | 1 | Maria | Penal | Dolo | Espécies |
| 2 | Qual o prazo de prescrição aquisitiva? | 15 anos para imóveis | 1 | João | Civil | Usucapião | Prazos |
| 3 | O que é cláusula pétrea? | Norma que não pode ser abolida por emenda | 1 | Pedro | Constitucional | Emendas | Limites |
| 4 | Defina legítima defesa | Repelir agressão injusta, atual ou iminente | 1 | Maria,Ana | Penal | Excludentes | Ilicitude |
| 5 | Como funciona a sucessão testamentária? | Herança segundo vontade do testador | 1 | João,Ana | Civil | Sucessões | Testamento |
| 6 | O que é devido processo legal? | Garantia de processo justo e adequado | 1 | Pedro,Ana | Constitucional | Garantias | Processuais |

### Uso Individual

**João (interessado em Civil e algumas questões gerais):**
- Seleciona: `João`, `Ana`
- Recebe questões: 2, 5, 4, 6 (onde Ana também contribuiu)
- Estrutura de decks:
  ```
  Direito::Questões Colaborativas::João::Alta::Civil::Usucapião::Prazos
  Direito::Questões Colaborativas::João::Média::Civil::Sucessões::Testamento
  Direito::Questões Colaborativas::Ana::Alta::Penal::Excludentes::Ilicitude
  Direito::Questões Colaborativas::Ana::Alta::Constitucional::Garantias::Processuais
  ```

**Maria (focada apenas em Penal):**
- Seleciona apenas: `Maria`
- Recebe questões: 1, 4
- Estrutura de decks:
  ```
  Direito::Questões Colaborativas::Maria::Alta::Penal::Dolo::Espécies
  Direito::Questões Colaborativas::Maria::Alta::Penal::Excludentes::Ilicitude
  ```

**Ana (revisão geral - quer estudar de todos):**
- Seleciona: `João`, `Maria`, `Pedro`, `Ana`
- Recebe todas as questões
- Cada questão fica no subdeck do respectivo autor

## Boas Práticas

### 1. Nomenclatura Consistente
- Use sempre a mesma grafia para o mesmo aluno
- Defina um padrão (ex: primeiro nome, nome completo, etc.)
- Evite abreviações inconsistentes

### 2. Organização Colaborativa
- Estabeleça convenções de nomenclatura em grupo
- Use a coluna IMPORTANCIA para indicar prioridades
- Mantenha a coluna SYNC? sempre como `1` para questões aprovadas

### 3. Revisão e Qualidade
- Questões podem ter múltiplos autores para indicar revisão
- Use `Autor,Revisor` para indicar quem criou e quem aprovou
- Mantenha metadados completos (TOPICO, SUBTOPICO, CONCEITO)

### 4. Evolução da Base
- Novos alunos podem ser adicionados a qualquer momento
- O sistema detecta automaticamente novos nomes na coluna ALUNOS
- A configuração global permite controlar quais alunos sincronizar

## Configuração Global de Alunos (Recomendado)

### Como Configurar
1. **Acesse**: Tools → Sheets2Anki → Configurar Alunos Globalmente (Ctrl+Shift+G)
2. **Ative filtro**: Marque "Aplicar filtro de alunos em todas as sincronizações"
3. **Selecione alunos**: Escolha da lista ou adicione manualmente
4. **Salve**: A configuração se aplica a todos os decks remotos

### Vantagens da Configuração Global
- **Consistência**: Mesma configuração em todos os decks
- **Simplicidade**: Configure uma vez, funciona sempre
- **Persistência**: Configuração salva entre sessões
- **Flexibilidade**: Ative/desative o filtro quando necessário

### Comportamentos
- **Filtro desativo**: Sincroniza todos os alunos (comportamento padrão)
- **Filtro ativo + alunos selecionados**: Sincroniza apenas os selecionados  
- **Filtro ativo + nenhum selecionado**: Não sincroniza nenhuma questão

## Migração de Planilhas Existentes

### Planilhas Sem Coluna ALUNO
- Continue funcionando normalmente
- Todas as questões são sincronizadas (comportamento anterior)
- Pode adicionar a coluna posteriormente para ativar a funcionalidade

### Adicionando Coluna ALUNO a Planilha Existente
1. Insira a coluna `ALUNO` na posição desejada
2. Preencha com nomes dos autores/revisores de cada questão
3. Na próxima sincronização, o sistema detectará automaticamente
4. Dialog de seleção aparecerá na primeira sincronização após a adição

### Dados Existentes
- Questões já sincronizadas permanecerão no deck atual
- Nova organização por aluno será aplicada apenas a atualizações futuras
- Para reorganizar completamente, desconecte e reconecte o deck

Este sistema oferece máxima flexibilidade mantendo compatibilidade total com planilhas e fluxos de trabalho existentes.
