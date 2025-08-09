# Refatoração: Nova Lógica de Identificação Única de Notas por Aluno

## Resumo das Alterações

Esta refatoração implementa a lógica correta para criar e gerenciar notas individuais por aluno, onde cada nota tem um identificador único no formato `{aluno}_{id}`.

## Principais Mudanças Implementadas

### 1. **Função `create_or_update_notes()` - Lógica Central Refatorada**
- **Arquivo**: `src/data_processor.py`
- **Mudança Principal**: Cada linha da planilha remota agora gera uma nota separada para cada aluno na coluna ALUNOS
- **ID Único**: Cada nota usa o formato `{aluno}_{id}` como identificador único
- **Controle de Alunos**: Apenas alunos habilitados no sistema têm suas notas sincronizadas

### 2. **Função `get_existing_notes_by_student_id()` - Nova Função**
- **Arquivo**: `src/data_processor.py`
- **Funcionalidade**: Busca notas existentes e mapeia por `student_note_id` (formato `{aluno}_{id}`)
- **Lógica**: Extrai o aluno do nome do subdeck onde a nota está localizada
- **Retorno**: Dicionário `{student_note_id: note_object}`

### 3. **Função `fill_note_fields_for_student()` - Nova Função**
- **Arquivo**: `src/data_processor.py`
- **Funcionalidade**: Preenche campos da nota com identificador único por aluno
- **ID Único**: Campo ID da nota é preenchido com `{aluno}_{id}`
- **Imutabilidade**: O ID nunca deve ser modificado após a criação da nota

### 4. **Função `note_fields_need_update()` - Lógica Atualizada**
- **Arquivo**: `src/data_processor.py`
- **Mudança**: Não compara mais o campo ID (pois é derivado e imutável)
- **Foco**: Compara apenas campos de conteúdo da planilha

### 5. **Função `extract_students_from_remote_data()` - Atualizada**
- **Arquivo**: `src/student_manager.py`
- **Mudança**: Usa nova estrutura `RemoteDeck.notes` ao invés de `remote_deck.questions`
- **Parsing**: Extrai alunos da coluna ALUNOS de cada nota

## Como Funciona a Nova Lógica

### Fluxo de Sincronização:

1. **Obtenção de Alunos Habilitados**
   - Sistema consulta configuração global de alunos habilitados
   - Apenas esses alunos terão suas notas sincronizadas

2. **Processamento de Cada Linha da Planilha**
   - Para cada linha com ID único na planilha remota
   - Extrai lista de alunos da coluna ALUNOS
   - Cria uma nota para cada aluno habilitado da lista

3. **Criação do ID Único**
   - Formato: `{nome_do_aluno}_{id_da_planilha}`
   - Exemplo: Se aluno é "João" e ID da planilha é "ABC123", o ID da nota será "João_ABC123"
   - Este ID nunca muda após a criação

4. **Organização em Subdecks**
   - Cada aluno tem seu próprio subdeck
   - Estrutura: `Sheets2Anki::Remote::Aluno::Importancia::Topico::Subtopico::Conceito`

5. **Controle de Notas Obsoletas**
   - Notas de alunos desabilitados são automaticamente removidas
   - Notas que não existem mais na planilha são removidas

## Benefícios da Refatoração

### ✅ **Identificação Única e Consistente**
- Cada combinação aluno-nota tem ID único e imutável
- Facilita rastreamento e atualização de notas específicas

### ✅ **Controle Granular por Aluno**
- Usuário pode habilitar/desabilitar alunos individualmente
- Sistema sincroniza apenas alunos selecionados

### ✅ **Sincronização Precisa**
- Detecta mudanças apenas no conteúdo relevante
- Mantém integridade dos identificadores únicos

### ✅ **Limpeza Automática**
- Remove automaticamente notas de alunos desabilitados
- Remove notas que não existem mais na fonte remota

## Exemplo Prático

### Planilha Remota:
| ID   | PERGUNTA           | ALUNOS      | SYNC? |
|------|--------------------|-------------|-------|
| A001 | Qual a capital?    | João,Maria  | true  |
| B002 | Como funciona?     | Maria,Pedro | true  |

### Alunos Habilitados:
- João: ✅ Habilitado
- Maria: ✅ Habilitado  
- Pedro: ❌ Desabilitado

### Notas Criadas:
1. **ID**: `João_A001` - Pergunta: "Qual a capital?" (para João)
2. **ID**: `Maria_A001` - Pergunta: "Qual a capital?" (para Maria)
3. **ID**: `Maria_B002` - Pergunta: "Como funciona?" (para Maria)

**Nota**: A nota para Pedro em B002 não é criada pois ele está desabilitado.

## Arquivos Modificados

- `src/data_processor.py` - Lógica principal refatorada
- `src/student_manager.py` - Função de extração de alunos atualizada
- `test_syntax.py` - Script de teste de sintaxe (novo)

## Código Limpo

A refatoração removeu código legado e manteve apenas a versão mais recente da lógica, resultando em uma codebase mais limpa, enxuta e organizada, conforme solicitado.
