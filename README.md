# Sheets2Anki

**Sheets2Anki** é um add-on para Anki que sincroniza- **Notas existentes não marcadas**: Permanecem intactas no Anki (não são excluídas)
- 🚫 **Notas novas não marcadas**: Não são criadas no Anki

### 📋 Exemplo de Planilha

Um exemplo completo de planilha com a nova funcionalidade está disponível em [`docs/exemplo_planilha_com_sync.tsv`](docs/exemplo_planilha_com_sync.tsv).

## Instalaçãos decks com planilhas do Google Sheets publicadas em formato TSV. Suas planilhas do Google Sheets servem como fonte da verdade: quando você sincroniza, os cards são criados, atualizados ou removidos no seu deck do Anki para refletir o conteúdo da planilha.

## Funcionalidades

- **Google Sheets como Fonte da Verdade:**  
  Sua planilha publicada do Google Sheets determina os cards presentes no Anki.

- **Estrutura Específica de Planilha:**  
  O add-on utiliza uma estrutura predefinida de colunas em português, otimizada para questões de estudo:
  - `ID`: Identificador único da questão
  - `PERGUNTA`: Texto principal da questão (frente do card)
  - `LEVAR PARA PROVA`: Campo de filtro para seleção de questões
  - `INFO COMPLEMENTAR`: Informação complementar básica
  - `INFO DETALHADA`: Informação detalhada adicional
  - `EXEMPLO 1`, `EXEMPLO 2`, `EXEMPLO 3`: Exemplos relacionados
  - `TOPICO`: Tópico principal da questão
  - `SUBTOPICO`: Subtópico específico
  - `BANCAS`: Bancas organizadoras relacionadas
  - `ULTIMO ANO EM PROVA`: Último ano em que apareceu em prova
  - `TAGS ADICIONAIS`: Tags adicionais para organização

- **Suporte a Cards Básicos e Cloze:**  
  Detecta automaticamente formatação Cloze (`{{c1::...}}`) no campo pergunta para criar cards Cloze. Outras questões se tornam cards básicos.

- **Atribuição Automática de Tags:**  
  Tags são automaticamente geradas baseadas nos campos `TOPICO`, `SUBTOPICO`, `BANCAS` e `TAGS ADICIONAIS`.

- **Manutenção de Deck:**  
  - **Removido na Planilha → Removido no Anki:** Se um card desaparecer da planilha, é removido do Anki na próxima sincronização.
  - **Removido no Anki → Não Removido na Planilha:** Não há sincronização reversa. Deletar um card no Anki não afeta a planilha; o card pode reaparecer se você sincronizar novamente, a menos que seja removido da planilha.

- **Interface em Português:**  
  Menus e mensagens em português brasileiro para facilitar o uso.

## Estrutura da Planilha

Para usar o Sheets2Anki, sua planilha do Google Sheets deve ter exatamente as seguintes colunas (na ordem que preferir):

| Coluna | Obrigatória | Descrição |
|--------|-------------|-----------|
| ID | ✅ | Identificador único para cada questão |
| PERGUNTA | ✅ | Texto da questão/frente do card |
| LEVAR PARA PROVA | ✅ | **Resposta sucinta e atômica** - núcleo da resposta da pergunta |
| SYNC? | ✅ | **Controle de sincronização** - true/1 para sincronizar, false/0 para não sincronizar |
| INFO COMPLEMENTAR | ✅ | Informações complementares |
| INFO DETALHADA | ✅ | Informações detalhadas |
| EXEMPLO 1 | ✅ | Primeiro exemplo |
| EXEMPLO 2 | ✅ | Segundo exemplo |
| EXEMPLO 3 | ✅ | Terceiro exemplo |
| TOPICO | ✅ | Categoria principal |
| SUBTOPICO | ✅ | Subcategoria |
| BANCAS | ✅ | Bancas relacionadas |
| ULTIMO ANO EM PROVA | ✅ | Ano da última ocorrência |
| TAGS ADICIONAIS | ✅ | Tags extras separadas por vírgula |

### 🔄 Controle de Sincronização com SYNC?

A coluna **SYNC?** permite controlar individualmente quais questões são sincronizadas:

- **Para sincronizar**: `true`, `1`, `sim`, `yes`, `verdadeiro`, `v` ou qualquer valor não reconhecido
- **Para NÃO sincronizar**: `false`, `0`, `não`, `nao`, `no`, `falso`, `f`

**✨ A coluna SYNC? é completamente case insensitive** - você pode usar `TRUE`, `True`, `SIM`, `False`, `NÃO`, etc.

**Comportamento da sincronização:**
- ✅ **Checkbox marcado (true/1)**: Nota é sincronizada normalmente
- ❌ **Checkbox desmarcado (false/0)**: Nota é ignorada durante a sincronização
- 🔒 **Notas existentes não marcadas**: Permanecem intactas no Anki (não são excluídas)
- 🚫 **Notas novas não marcadas**: Não são criadas no Anki

## Instalação

1. Baixe o add-on do AnkiWeb ou instale manualmente
2. Reinicie o Anki
3. O menu "Gerenciar Decks sheets2anki" aparecerá no menu Ferramentas

## Como Usar

### 1. Preparar sua Planilha
1. Crie uma planilha no Google Sheets com a estrutura de colunas descrita acima
2. Preencha suas questões seguindo o formato
3. **Publique a planilha:**
   - Vá em Arquivo → Compartilhar → Publicar na web
   - Escolha "Valores separados por tabulação (.tsv)"
   - Copie o link gerado

### 2. Adicionar Deck Remoto
1. No Anki, vá em **Ferramentas → Gerenciar Decks sheets2anki → Adicionar Novo Deck Remoto** (Ctrl+Shift+A)
2. Cole a URL da planilha publicada
3. Digite um nome para seu deck
4. O add-on criará automaticamente o deck e sincronizará

### 3. Sincronizar
- **Sincronização Manual:** **Ferramentas → Gerenciar Decks sheets2anki → Sincronizar Decks** (Ctrl+Shift+S)
- **Sincronização Automática:** Execute sempre que quiser atualizar com a planilha

### 4. Gerenciar Decks
- **Desconectar Deck:** **Ferramentas → Gerenciar Decks sheets2anki → Desconectar um Deck Remoto** (Ctrl+Shift+D)

## Atalhos de Teclado

| Ação | Atalho |
|------|--------|
| Adicionar Novo Deck Remoto | Ctrl+Shift+A |
| Sincronizar Decks | Ctrl+Shift+S |
| Desconectar Deck Remoto | Ctrl+Shift+D |
| Importar Deck de Teste | Ctrl+Shift+T |

## Requisitos

- Anki
- Planilha do Google Sheets publicada em formato TSV
- Conexão com internet para sincronização

## Exemplo de Uso (Cards Cloze)

Se sua coluna `PERGUNTA` contém:
```
A capital do Brasil é {{c1::Brasília}}
```

O add-on criará automaticamente um card Cloze no Anki.

## Solução de Problemas

### Erro de URL
- Certifique-se de que a planilha está **publicada** (não apenas compartilhada)
- Use o link de **valores separados por vírgula/tabulação**, não o link normal da planilha

### Cards não aparecem
- Verifique se todas as colunas obrigatórias estão presentes
- Certifique-se de que o campo `ID` tem valores únicos
- Verifique se há dados na coluna `PERGUNTA`

### Erro de sincronização
- Verifique sua conexão com internet
- Confirme se a URL da planilha ainda está válida
- Use **Ferramentas → Gerenciar Decks sheets2anki → Desconectar um Deck Remoto** e reconecte se necessário

## Limitações

- **Sem sincronização reversa:** Mudanças no Anki não afetam a planilha
- **Estrutura fixa:** Deve usar exatamente as colunas especificadas
- **Idioma:** Interface e estrutura otimizadas para português brasileiro
- **Dependência de internet:** Requer conexão para sincronizar

## Status de Desenvolvimento

Este add-on é mantido ativamente. A estrutura de colunas foi projetada especificamente para questões de estudo em português brasileiro, oferecendo uma solução robusta para sincronização unidirecional com Google Sheets.

## Documentação Técnica

Para desenvolvedores e informações técnicas:
- **Scripts de Build:** [`scripts/README.md`](scripts/README.md) - Como compilar e fazer build do add-on
- **Testes:** [`tests/README.md`](tests/README.md) - Informações sobre como executar testes
- **Documentação:** [`docs/README.md`](docs/README.md) - Índice da documentação técnica

## Desenvolvimento

### Scripts de Build

O projeto inclui scripts Python para automatizar o build e empacotamento:

```bash
# Menu interativo unificado (recomendado)
python scripts/build_packages.py

# Script específico para AnkiWeb
python scripts/prepare_ankiweb.py

# Script para pacote standalone
python scripts/create_standalone_package.py

# Validação de pacotes
python scripts/validate_ankiaddon.py build/sheets2anki.ankiaddon
```

Os scripts criam arquivos `.ankiaddon` prontos para upload no AnkiWeb ou distribuição independente. Consulte `scripts/README.md` para detalhes completos sobre cada script.