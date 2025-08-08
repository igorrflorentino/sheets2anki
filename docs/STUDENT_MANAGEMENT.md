# Funcionalidade de Gerenciamento de Alunos - Sheets2Anki

## Visão Geral

A nova funcionalidade de **Gerenciamento de Alunos** permite que o usuário do addon Sheets2Anki selecione quais alunos deseja sincronizar de uma planilha Google Sheets colaborativa. Esta funcionalidade é especialmente útil quando múltiplos alunos contribuem para a mesma planilha, mas cada usuário do addon deseja estudar apenas as notas de alunos específicos.

## Como Funciona

### 1. Nova Coluna ALUNOS

- Uma nova coluna obrigatória `ALUNOS` foi adicionada às definições de coluna
- Esta coluna deve conter os nomes dos alunos interessados em cada nota específica
- Suporta múltiplos alunos separados por vírgula, ponto e vírgula ou pipe (`,`, `;`, `|`)
- Exemplo: `João, Maria` ou `João|Maria|Pedro`

### 2. Seleção de Alunos

Quando uma planilha contém a coluna ALUNOS:
- O addon detecta automaticamente todos os alunos únicos da planilha
- Se não há seleção prévia, um dialog é apresentado ao usuário
- O usuário pode selecionar quais alunos deseja sincronizar
- A seleção é salva e reutilizada em sincronizações futuras

### 3. Estrutura Hierárquica de Decks

Para alunos selecionados, a estrutura de subdecks segue o padrão:
```
Deck Raiz::Deck Remoto::Aluno::Importância::Tópico::Subtópico::Conceito
```

Exemplo:
```
Meu Deck Principal::Questões de Direito::João::Alta::Civil::Contratos::Formação::Oferta
```

### 4. Note Types Personalizados

Cada aluno recebe seu próprio Note Type seguindo o padrão:
```
Sheets2Anki - {url_hash} - {deck_name} - {aluno} - {Basic|Cloze}
```

Exemplo:
```
Sheets2Anki - a1b2c3d4 - QuestoesDireito - João - Basic
Sheets2Anki - a1b2c3d4 - QuestoesDireito - João - Cloze
```

## Funcionalidades Principais

### 1. Filtragem Automática
- Apenas notas dos alunos selecionados são sincronizadas
- Notas de alunos não selecionados são ignoradas durante a sincronização

### 2. Remoção de Notas Desmarcadas
- Se um aluno for desmarcado, suas notas são automaticamente removidas dos decks locais
- Previne acúmulo de dados desnecessários

### 3. Gerenciamento Flexível
- Dialog de seleção com opções "Selecionar Todos" e "Desmarcar Todos"
- Visualização clara dos alunos disponíveis na planilha
- Informações sobre o que acontecerá com cada opção

### 4. Compatibilidade
- Planilhas sem coluna ALUNO continuam funcionando normalmente
- Modo de compatibilidade preserva o comportamento anterior
- Migração suave para usuários existentes

## Funções Principais Implementadas

### No arquivo `student_manager.py`:
- `StudentSelectionDialog`: Dialog para seleção de alunos
- `extract_students_from_remote_data()`: Extrai alunos únicos da planilha
- `filter_questions_by_selected_students()`: Filtra questões por alunos
- `get_student_subdeck_name()`: Gera nomes de subdecks para alunos
- `remove_notes_for_unselected_students()`: Remove notas de alunos desmarcados

### No arquivo `deck_manager.py`:
- `manage_deck_students()`: Interface para gerenciar alunos de um deck
- `reset_student_selection()`: Remove seleção de alunos de todos os decks

### Modificações em arquivos existentes:
- `column_definitions.py`: Nova coluna ALUNO adicionada
- `note_processor.py`: Lógica de processamento modificada para suportar alunos
- `card_templates.py`: Criação de modelos específicos para alunos
- `utils.py`: Função de nomeação de note types estendida
- `subdeck_manager.py`: Suporte a subdecks por aluno

## Interface do Usuário

### Dialog de Seleção de Alunos
- Lista todos os alunos encontrados na planilha
- Checkboxes para seleção individual
- Botões de seleção rápida (Todos/Nenhum)
- Informações sobre o comportamento da funcionalidade
- Preserva seleções anteriores

### Integração com Menu Principal
- Nova opção "Gerenciar Alunos" para configurar seleção por deck
- Opção "Resetar Seleção de Alunos" para voltar ao comportamento padrão

## Casos de Uso

### 1. Estudo Individual
Um professor cria uma planilha colaborativa onde cada aluno pode adicionar questões. João quer estudar apenas suas próprias questões e as do colega Maria.

### 2. Grupos de Estudo
Membros de um grupo de estudo contribuem para a mesma planilha, mas cada um quer focar em tópicos de interesse específico baseado no autor das questões.

### 3. Revisão Seletiva
Um usuário quer revisar questões de determinados autores que considera mais confiáveis ou relevantes.

## Configuração e Persistência

### Armazenamento
- Seleções são salvas no arquivo `meta.json` do addon
- Estrutura: `meta.decks[url].student_selection = [lista_de_alunos]`
- Persistente entre sessões do Anki

### Formato de Dados
```json
{
  "decks": {
    "https://docs.google.com/spreadsheets/...": {
      "student_selection": ["João", "Maria", "Pedro"]
    }
  }
}
```

## Exemplo de Fluxo de Trabalho

1. **Configuração Inicial**: Usuário adiciona um deck remoto com planilha colaborativa
2. **Primeira Sincronização**: Sistema detecta coluna ALUNO e mostra dialog de seleção
3. **Seleção**: Usuário seleciona João e Maria como alunos de interesse
4. **Sincronização**: Apenas questões de João e Maria são importadas
5. **Organização**: Questões são organizadas em subdecks separados por aluno
6. **Atualizações Futuras**: Novas sincronizações respeitam a seleção salva

## Benefícios

- **Organização**: Estrutura clara por aluno facilita estudos direcionados
- **Eficiência**: Evita importar dados desnecessários
- **Flexibilidade**: Fácil alteração da seleção conforme necessário
- **Colaboração**: Suporte nativo a planilhas colaborativas
- **Compatibilidade**: Não quebra funcionamento existente

## Implementação Técnica

### Detecção Automática
O sistema verifica automaticamente se a planilha contém a coluna ALUNO e ativa o gerenciamento apenas quando necessário.

### Processamento Eficiente
- Filtragem acontece antes do processamento das notas
- Evita criar/processar notas que serão descartadas
- Otimizado para planilhas grandes

### Tratamento de Erros
- Validação robusta de dados de entrada
- Fallbacks para casos edge
- Mensagens informativas para o usuário

Esta funcionalidade representa uma evolução significativa do addon, permitindo uso em cenários colaborativos mais complexos mantendo a simplicidade de uso.
