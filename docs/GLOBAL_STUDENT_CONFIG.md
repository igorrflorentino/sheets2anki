# Configuração Global de Alunos - Sheets2Anki

## Visão Geral

O sistema de configuração global de alunos permite ao usuário definir, de forma centralizada, quais alunos devem ser sincronizados em **todos** os decks remotos. Esta configuração é persistente e aplicada automaticamente a todas as sincronizações futuras.

## Funcionalidades

### 1. Configuração Centralizada
- Define uma vez, aplica em todos os decks
- Configuração persistente entre sessões do Anki
- Interface amigável para seleção de alunos

### 2. Descoberta Automática de Alunos
- Analisa todos os decks remotos cadastrados
- Extrai automaticamente os nomes de alunos das colunas ALUNOS
- Suporte a múltiplos alunos por nota (separados por vírgula)

### 3. Filtro Global
- Ativa/desativa o filtro de alunos globalmente
- Quando ativo, sincroniza apenas alunos selecionados
- Quando desativo, sincroniza todos os alunos

## Como Usar

### Acessando a Configuração
1. No Anki, vá ao menu **Tools → Sheets2Anki → Configurar Alunos Globalmente**
2. Ou use o atalho **Ctrl+Shift+G**

### Interface da Configuração
A janela de configuração apresenta:

#### Checkbox "Aplicar filtro de alunos"
- **Marcado**: O filtro está ativo - apenas alunos selecionados serão sincronizados
- **Desmarcado**: Todos os alunos serão sincronizados (comportamento padrão)

#### Painel "Alunos Disponíveis"
- Lista todos os alunos encontrados nos decks remotos
- Duplo clique ou botão "Adicionar →" move para lista de selecionados

#### Painel "Alunos Selecionados"  
- Mostra os alunos que serão sincronizados
- Duplo clique ou botão "← Remover" move para lista de disponíveis

#### Botão "Adicionar Aluno..."
- Permite adicionar manualmente um aluno não listado automaticamente
- Útil para alunos que ainda não têm notas nas planilhas

### Salvando a Configuração
1. Selecione os alunos desejados
2. Marque/desmarque o filtro conforme necessário  
3. Clique em **OK** para salvar
4. A configuração será aplicada imediatamente às próximas sincronizações

## Comportamento Durante a Sincronização

### Com Filtro Ativo
- **Alunos selecionados**: Apenas suas notas são sincronizadas
- **Nenhum aluno selecionado**: Nenhuma nota é sincronizada
- **Logs**: Mostra quantas questões foram filtradas

### Com Filtro Desativo
- Todos os alunos são sincronizados normalmente
- Comportamento idêntico às versões anteriores do addon

## Estrutura Hierárquica de Decks

Quando alunos específicos são sincronizados, a estrutura hierárquica permanece:
```
Deck Raiz::Deck Remoto::Aluno::Importância::Tópico::Subtópico::Conceito
```

Apenas os alunos selecionados terão seus subdecks criados/atualizados.

## Arquivo de Configuração

As configurações são armazenadas em `meta.json`:

```json
{
    "students": {
        "enabled_students": ["João", "Maria", "Pedro"],
        "student_sync_enabled": true,
        "last_updated": 1640995200
    }
}
```

### Campos
- `enabled_students`: Lista de alunos selecionados
- `student_sync_enabled`: Se o filtro está ativo  
- `last_updated`: Timestamp da última modificação

## Casos de Uso

### 1. Professor com Turma Específica
Um professor que quer sincronizar apenas notas de alunos de uma turma específica:
1. Ativa o filtro
2. Seleciona apenas os alunos da turma desejada
3. Todas as sincronizações futuras filtram automaticamente

### 2. Estudo Individual  
Um aluno que quer sincronizar apenas suas próprias notas:
1. Ativa o filtro
2. Seleciona apenas seu próprio nome
3. Ignora notas de outros colaboradores na planilha

### 3. Revisão Coletiva
Para sincronizar notas de todos os colaboradores:
1. Desativa o filtro
2. Sincronização incluirá todos os alunos automaticamente

## Troubleshooting

### Aluno não aparece na lista
**Causa**: O aluno ainda não tem notas em nenhum deck remoto
**Solução**: Use "Adicionar Aluno..." para incluir manualmente

### Nenhuma nota sincronizada
**Causa**: Filtro ativo mas nenhum aluno selecionado
**Solução**: Selecione alunos ou desative o filtro

### Configuração não persiste
**Causa**: Problemas de permissão no arquivo `meta.json`
**Solução**: Verifique permissões de escrita no diretório do addon

## Compatibilidade

- **Versão mínima**: Sheets2Anki 2.0+
- **Anki**: 2.1.50+ (Qt5/Qt6)
- **Planilhas**: Requer coluna `ALUNOS` nas planilhas do Google Sheets

## Migração de Versões Anteriores

Ao atualizar de versões que usavam seleção por deck:
1. A configuração global inicia vazia (filtro desativo)
2. Comportamento inicial é idêntico à versão anterior  
3. Configure globalmente quando desejar o novo comportamento
4. Configurações antigas por deck são desconsideradas
