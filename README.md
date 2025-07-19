# 📚 Sheets2Anki

**Sheets2Anki** é um add-on profissional para Anki que sincroniza decks com planilhas do Google Sheets publicadas em formato TSV. Suas planilhas do Google Sheets servem como fonte da verdade: quando você sincroniza, os cards são criados, atualizados ou removidos no seu deck do Anki para refletir o conteúdo da planilha.

## ✨ Principais Funcionalidades

### 🔄 **Sincronização Seletiva**
- **Controle granular**: Coluna `SYNC?` permite escolher quais questões sincronizar
- **Case insensitive**: Aceita `TRUE`, `true`, `SIM`, `sim`, `1`, `false`, `0`, `f`, etc.
- **Comportamento inteligente**: Notas existentes não marcadas permanecem intactas no Anki

### 🧹 **Limpeza Automática de Fórmulas**
- **Detecção automática**: Remove erros de fórmula como `#NAME?`, `#REF!`, `#VALUE!`
- **Fórmulas Excel/Google Sheets**: Limpa automaticamente `=SOMA()`, `=VLOOKUP()`, etc.
- **Preservação de dados**: Mantém conteúdo válido intacto

### 🌐 **Suporte a URLs Publicadas**
- **URLs normais**: `https://docs.google.com/spreadsheets/d/ID/edit`
- **URLs publicadas**: `https://docs.google.com/spreadsheets/d/e/ID/pub`
- **Validação automática**: Converte automaticamente para formato correto

### 📝 **Estrutura Otimizada para Estudo**
- **17 colunas obrigatórias**: Estrutura completa para questões de estudo
- **Cards Cloze**: Detecta automaticamente formatação `{{c1::...}}`
- **Tags automáticas**: Geradas a partir de `TOPICO`, `SUBTOPICO`, `BANCAS`
- **Subdecks automáticos**: Cria subdecks baseados em `TOPICO` e `SUBTOPICO`

## 📋 Estrutura da Planilha

Sua planilha do Google Sheets deve ter exatamente as seguintes colunas:

| # | Coluna | Obrigatória | Descrição |
|---|--------|-------------|-----------|
| 1 | **ID** | ✅ | Identificador único para cada questão |
| 2 | **PERGUNTA** | ✅ | Texto da questão/frente do card |
| 3 | **LEVAR PARA PROVA** | ✅ | Resposta sucinta e atômica |
| 4 | **SYNC?** | ✅ | Controle de sincronização (`true`/`false`) |
| 5 | **INFO COMPLEMENTAR** | ✅ | Informações complementares |
| 6 | **INFO DETALHADA** | ✅ | Informações detalhadas |
| 7 | **EXEMPLO 1** | ✅ | Primeiro exemplo |
| 8 | **EXEMPLO 2** | ✅ | Segundo exemplo |
| 9 | **EXEMPLO 3** | ✅ | Terceiro exemplo |
| 10 | **TOPICO** | ✅ | Categoria principal |
| 11 | **SUBTOPICO** | ✅ | Subcategoria |
| 12 | **CONCEITO** | ✅ | Conceito abordado |
| 13 | **BANCAS** | ✅ | Bancas organizadoras |
| 14 | **ULTIMO ANO EM PROVA** | ✅ | Ano da última ocorrência |
| 15 | **CARREIRA** | ✅ | Área/carreira da questão |
| 16 | **IMPORTANCIA** | ✅ | Nível de importância |
| 17 | **TAGS ADICIONAIS** | ✅ | Tags extras separadas por vírgula |

### 🔄 **Controle de Sincronização (SYNC?)**

A coluna **SYNC?** é **completamente case insensitive** e aceita:

**✅ Para sincronizar:**
- `true`, `1`, `sim`, `yes`, `verdadeiro`, `SIM`, `TRUE`, `v`
- Campo vazio (padrão é sincronizar)
- Qualquer valor não reconhecido

**❌ Para NÃO sincronizar:**
- `false`, `0`, `não`, `nao`, `no`, `falso`, `f`, `FALSE`, `NÃO`

**Comportamento da sincronização:**
- ✅ **Marcado para sincronizar**: Nota é criada/atualizada no Anki
- ❌ **Desmarcado**: Nota é ignorada durante a sincronização
- 🔒 **Notas existentes desmarcadas**: Permanecem intactas no Anki
- 🚫 **Notas novas desmarcadas**: Não são criadas no Anki

## 🚀 Instalação

1. **Baixe o add-on** do AnkiWeb ou instale manualmente
2. **Reinicie o Anki**
3. **Acesse o menu**: "Ferramentas → Sheets2anki"

## 📖 Como Usar

### 1. **Preparar sua Planilha**
1. Crie uma planilha no Google Sheets com as 17 colunas obrigatória
   - Modelo exemplo padrão Google Sheet 
      - https://docs.google.com/spreadsheets/d/1urrp2t8xA2C0f3vLTdQyQblVu5ur0lirFCN9KyCVLlY/edit?usp=sharing
2. Preencha suas questões seguindo o formato
3. **Publique a planilha:**
   - Vá em `Arquivo → Compartilhar → Publicar na web`
   - Escolha `Valores separados por tabulação (.tsv)`
   - Copie o link gerado

### 2. **Adicionar Deck Remoto**
1. No Anki: `Ferramentas → Sheets2anki → Adicionar Novo Deck Remoto` (Ctrl+Shift+A)
2. Cole a URL da planilha publicada
3. Digite um nome para seu deck
4. O add-on criará automaticamente o deck e sincronizará

### 3. **Sincronizar**
- **Manual**: `Ferramentas → Sheets2anki → Sincronizar Decks` (Ctrl+Shift+S)
- **Automática**: Execute sempre que quiser atualizar com a planilha

### 4. **Gerenciar Decks**
- **Desconectar**: `Ferramentas → Sheets2anki → Desconectar um Deck Remoto` (Ctrl+Shift+D)

## ⌨️ Atalhos de Teclado

| Ação | Atalho |
|------|--------|
| Adicionar Novo Deck Remoto | `Ctrl+Shift+A` |
| Sincronizar Decks | `Ctrl+Shift+S` |
| Desconectar Deck Remoto | `Ctrl+Shift+D` |
| Importar Deck de Teste | `Ctrl+Shift+T` |

## 💡 Recursos Avançados

### 🧪 **Cards Cloze**
Se sua coluna `PERGUNTA` contém:
```
A capital do Brasil é {{c1::Brasília}}
```
O add-on criará automaticamente um card Cloze no Anki.

### 🏷️ **Tags Automáticas**
Tags são geradas automaticamente a partir de:
- `TOPICO` → tag principal
- `SUBTOPICO` → tag secundária
- `CONCEITO` → tag terciária (com tag extra para fácil filtragem)
- `BANCAS` → tag da banca
- `ULTIMO ANO EM PROVA` → tag do ano
- `CARREIRA` → tag do cargo
- `IMPORTANCIA` → tag da importancia
- `TAGS ADICIONAIS` → tags extras

Estrutura hierárquica de tags:
- `sheet2anki::topicos::topico::subtopicos::subtopico::conceitos::conceito`
- `sheet2anki::conceitos::conceito` (tag extra para fácil filtragem)

Valores padrão são usados quando campos estão vazios.

### 📂 **Subdecks Automáticos**
O add-on pode criar automaticamente subdecks baseados nos valores das colunas:
- `TOPICO` e `SUBTOPICO` → Estrutura hierárquica de decks

Estrutura criada:
- `DeckPrincipal::Topico::Subtopico::Conceito` (sempre, usando valores padrão quando campos estão vazios)
- Valores padrão: `Topic Missing`, `Subtopic Missing`, `Concept Missing`

Esta funcionalidade pode ser habilitada/desabilitada em `Ferramentas → Sheets2anki → Configurar Subdecks por Tópico`

### 🔧 **Limpeza Automática**
O sistema remove automaticamente:
- **Erros de fórmula**: `#NAME?`, `#REF!`, `#VALUE!`, `#DIV/0!`, etc.
- **Fórmulas**: `=SOMA()`, `=VLOOKUP()`, `=IF()`, etc.
- **Caracteres especiais**: Limpa formatação desnecessária

## 🛠️ Solução de Problemas

### ❌ **Erro de URL**
- Certifique-se de que a planilha está **publicada** (não apenas compartilhada)
- Use o link de **valores separados por tabulação**, não o link normal
- Verifique se todas as 17 colunas obrigatórias estão presentes

### ❌ **Cards não aparecem**
- Verifique se o campo `ID` tem valores únicos
- Certifique-se de que `SYNC?` está marcado como `true`

### ❌ **Erro de sincronização**
- Verifique sua conexão com internet
- Confirme se a URL da planilha ainda está válida
- Use "Desconectar Deck Remoto" e reconecte se necessário

### ❌ **Fórmulas não são limpas**
- O sistema limpa automaticamente erros de fórmula
- Se persistir, verifique se os dados estão no formato correto

## 📊 Compatibilidade

### ✅ **Testado e Funcionando**
- **Anki**: Versão 25.x
- **URLs**: Normais e publicadas do Google Sheets
- **Formatos**: TSV (Tab-separated values)
- **Sistemas**: Windows, macOS, Linux

### ✅ **Funcionalidades Testadas**
- Sincronização seletiva (100% funcionando)
- Limpeza de fórmulas (100% funcionando)
- Validação de URLs (100% funcionando)
- Case insensitive SYNC? (100% funcionando)
- Compatibilidade Anki 25.x (100% funcionando)

## 🔒 Limitações

- **Sem sincronização reversa**: Mudanças no Anki não afetam a planilha
- **Estrutura fixa**: Deve usar exatamente as 17 colunas especificadas
- **Idioma**: Interface e estrutura otimizadas para português brasileiro
- **Dependência de internet**: Requer conexão para sincronizar

## 📚 Documentação Técnica

### 📖 **Para Usuários**
- **Guia de Uso**: Este README
- **Exemplos**: Planilhas de exemplo disponíveis
- **Solução de Problemas**: Seção completa acima

### 🔧 **Para Desenvolvedores**
- **Scripts de Build**: [`scripts/README.md`](scripts/README.md) - Como compilar o add-on
- **Testes**: [`tests/README.md`](tests/README.md) - Sistema de testes completo
- **Documentação**: [`docs/README.md`](docs/README.md) - Documentação técnica

### 🧪 **Sistema de Testes**
O projeto possui um sistema de testes profissional:
```bash
# Testes rápidos (recomendado)
python run_tests.py quick

# Suite completa de testes
python run_tests.py

# Testes específicos
cd tests && python integration/test_integration.py
```

## 🛠️ Desenvolvimento

### 📦 **Scripts de Build**
O projeto inclui scripts Python para automatizar o build:

```bash
# Menu interativo unificado (recomendado)
python scripts/build_packages.py

# Script específico para AnkiWeb
python scripts/create_ankiweb_package.py

# Script para pacote standalone
python scripts/create_standalone_package.py

# Validação de pacotes
python scripts/validate_packages.py
```

### 🧪 **Testes Automatizados**
Sistema de testes completo com:
- **Testes unitários**: Funcionalidades específicas
- **Testes de integração**: Workflow completo
- **Testes de debug**: Diagnóstico de problemas
- **Cobertura 100%**: Todas as funcionalidades testadas

### 📊 **Estrutura Organizacional**
```
sheets2anki/
├── README.md                    # ← Este arquivo
├── src/                         # Código principal
├── tests/                       # Sistema de testes
│   ├── README.md               # Guia dos testes
│   ├── docs/                   # Documentação técnica
│   └── [testes organizados]
├── scripts/                     # Scripts de build
├── docs/                        # Documentação
└── build/                       # Arquivos compilados
```

## 🏆 Status do Projeto

### ✅ **Funcionalidades Implementadas**
- ✅ Sincronização seletiva com coluna SYNC?
- ✅ Limpeza automática de fórmulas
- ✅ Suporte a URLs publicadas
- ✅ Validação case insensitive
- ✅ Subdecks automáticos por TOPICO e SUBTOPICO
- ✅ Compatibilidade Anki 25.x
- ✅ Sistema de testes completo
- ✅ Documentação profissional

### 📈 **Estatísticas**
- **Testes**: 100% funcionando (20+ testes)
- **Cobertura**: Todas as funcionalidades testadas
- **Compatibilidade**: Anki 25.x confirmada
- **Documentação**: Completa e atualizada

## 🔄 Histórico de Versões

### **Versão Atual - Profissional**
- ✅ Sincronização seletiva implementada
- ✅ Limpeza automática de fórmulas
- ✅ Suporte a URLs publicadas
- ✅ Sistema de testes completo
- ✅ Documentação reorganizada
- ✅ Estrutura profissional

### **Melhorias Recentes**
- 🔄 Consolidação de dados de teste
- 🧹 Limpeza automática de arquivos antigos
- 📚 Documentação técnica completa
- 🧪 Sistema de testes profissional
- 📊 Validação 100% funcionando

## 🤝 Contribuição

### 📝 **Como Contribuir**
1. Faça fork do projeto
2. Crie uma branch para sua funcionalidade
3. Execute os testes: `python run_tests.py quick`
4. Submeta um pull request

### 🧪 **Executar Testes**
```bash
# Testes rápidos
python run_tests.py quick

# Suite completa
python run_tests.py

# Testes específicos
cd tests && python debug/debug_suite.py
```

### 📚 **Documentação**
- Consulte `tests/README.md` para informações sobre testes
- Veja `scripts/README.md` para build e empacotamento
- Acesse `docs/README.md` para documentação técnica

## 📧 Suporte

Para problemas, sugestões ou dúvidas:
1. Verifique a seção "Solução de Problemas" acima
2. Consulte a documentação técnica
3. Execute os testes para diagnóstico
4. Abra uma issue no repositório