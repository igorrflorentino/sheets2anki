# 📚 Sheets2Anki

# 📚 Sheets2Anki

**Sheets2Anki** é um add-on profissional para Anki que sincroniza decks com planilhas do Google Sheets publicadas em formato TSV. Suas planilhas do Google Sheets servem como fonte da verdade: quando você sincroniza, os cards são criados, atualizados ou removidos no seu deck do Anki para refletir o conteúdo da planilha.

## ✨ Principais Funcionalidades

### � **Sistema de Gestão de Alunos**
- **Configuração global**: Configure quais alunos devem ser sincronizados
- **Seleção por deck**: Escolha alunos específicos para cada deck
- **Subdecks personalizados**: Cada aluno tem seu próprio subdeck hierárquico
- **Note types individuais**: Cada aluno recebe modelos de nota personalizados

### �🔄 **Sincronização Seletiva Avançada**
- **Controle granular**: Coluna `SYNC?` permite escolher quais questões sincronizar
- **Case insensitive**: Aceita `TRUE`, `true`, `SIM`, `sim`, `1`, `false`, `0`, `f`, etc.
- **Filtro de alunos**: Sincroniza apenas alunos selecionados globalmente
- **Comportamento inteligente**: Notas existentes não marcadas permanecem intactas

### 🌐 **Sincronização AnkiWeb Automática**
- **Configuração flexível**: Desabilitado ou Sincronizar automaticamente
- **Integração perfeita**: Sincroniza com AnkiWeb após atualizar decks remotos
- **Múltiplos métodos**: Compatível com diferentes versões do Anki
- **Timing inteligente**: Sincroniza apenas após usuário fechar resumo

### 🏷️ **Sistema de Tags Hierárquico Completo**
- **8 categorias organizadas**: Alunos, Tópicos, Subtópicos, Conceitos, Bancas, Anos, Carreiras, Importância
- **Estrutura hierárquica**: `Sheets2Anki::Topicos::topico::subtopico::conceito`
- **Limpeza automática**: Remove caracteres especiais e normaliza texto
- **Múltiplos valores**: Suporta valores separados por vírgula

### � **Sistema de Backup Completo**
- **Backup automático**: Backup antes de operações importantes
- **Backup manual**: Interface gráfica para criar/restaurar backups
- **Configurações completas**: Backup de decks remotos, preferências e configurações
- **Versionamento**: Sistema de backup com rotação automática

### 📂 **Subdecks Automáticos por Aluno**
- **Estrutura hierárquica**: `DeckRemoto::Aluno::Importância::Tópico::Subtópico::Conceito`
- **Limpeza automática**: Remove subdecks vazios após sincronização
- **Valores padrão**: `[MISSING X.]` para campos vazios
- **Gestão inteligente**: Mantém organização limpa

### 🌐 **Suporte Completo a URLs**
- **URLs normais**: `https://docs.google.com/spreadsheets/d/ID/edit`
- **URLs publicadas**: `https://docs.google.com/spreadsheets/d/e/ID/pub`
- **Validação automática**: Converte automaticamente para formato correto

### ⚙️ **Configurações Avançadas**
- **Opções de deck**: Configuração automática de opções de deck
- **Gestão global**: Configuração centralizada de alunos
- **Sistema de debug**: Logging detalhado para troubleshooting

## 📋 Estrutura da Planilha

Sua planilha do Google Sheets deve ter exatamente as seguintes **18 colunas obrigatórias**:

| # | Coluna | Obrigatória | Descrição |
|---|--------|-------------|-----------|
| 1 | **ID** | ✅ | Identificador único para cada questão |
| 2 | **PERGUNTA** | ✅ | Texto da questão/frente do card |
| 3 | **LEVAR PARA PROVA** | ✅ | Resposta sucinta e atômica |
| 4 | **SYNC?** | ✅ | Controle de sincronização (`true`/`false`) |
| 5 | **ALUNOS** | ✅ | Lista de alunos interessados (separados por vírgula) |
| 6 | **INFO COMPLEMENTAR** | ✅ | Informações complementares |
| 7 | **INFO DETALHADA** | ✅ | Informações detalhadas |
| 8 | **EXEMPLO 1** | ✅ | Primeiro exemplo |
| 9 | **EXEMPLO 2** | ✅ | Segundo exemplo |
| 10 | **EXEMPLO 3** | ✅ | Terceiro exemplo |
| 11 | **TOPICO** | ✅ | Categoria principal |
| 12 | **SUBTOPICO** | ✅ | Subcategoria |
| 13 | **CONCEITO** | ✅ | Conceito abordado |
| 14 | **BANCAS** | ✅ | Bancas organizadoras |
| 15 | **ULTIMO ANO EM PROVA** | ✅ | Ano da última ocorrência |
| 16 | **CARREIRA** | ✅ | Área/carreira da questão |
| 17 | **IMPORTANCIA** | ✅ | Nível de importância |
| 18 | **TAGS ADICIONAIS** | ✅ | Tags extras separadas por vírgula |

### 👥 **Campo ALUNOS (Novo!)**
O campo **ALUNOS** é uma das principais funcionalidades do sistema:

**✅ Formato aceito:**
- `João, Maria, Pedro` (separados por vírgula)
- `João; Maria; Pedro` (separados por ponto e vírgula)  
- `João|Maria|Pedro` (separados por pipe)
- `João` (aluno único)

**🎯 Comportamento:**
- **Notas com alunos específicos**: Aparecem apenas nos subdecks dos alunos listados
- **Notas sem alunos**: Marcadas como `[MISSING A.]` e aparecem em deck especial
- **Filtro global**: Apenas alunos habilitados globalmente são sincronizados

### 🔄 **Controle de Sincronização (SYNC?)**

A coluna **SYNC?** é **completamente case insensitive** e aceita:

**✅ Para sincronizar:**
- `true`, `1`, `sim`, `yes`, `verdadeiro`, `SIM`, `TRUE`, `v`
- Campo vazio (padrão é sincronizar)

**❌ Para NÃO sincronizar:**
- `false`, `0`, `não`, `nao`, `no`, `falso`, `f`, `FALSE`, `NÃO`

## 🚀 Instalação

1. **Baixe o add-on** do AnkiWeb ou instale manualmente
2. **Reinicie o Anki**
3. **Acesse o menu**: "Ferramentas → Sheets2Anki"

## 📖 Como Usar

### 1. **Preparar sua Planilha**
1. Crie uma planilha no Google Sheets com as **18 colunas obrigatórias**
   - Modelo exemplo: [Template Google Sheets](https://docs.google.com/spreadsheets/d/1urrp2t8xA2C0f3vLTdQyQblVu5ur0lirFCN9KyCVLlY/edit?usp=sharing)
2. Preencha suas questões seguindo o formato
3. **Inclua alunos** na coluna ALUNOS conforme necessário
4. **Publique a planilha:**
   - Vá em `Arquivo → Compartilhar → Publicar na web`
   - Escolha `Valores separados por tabulação (.tsv)`
   - Copie o link gerado

### 2. **Configurar Alunos Globalmente**
1. No Anki: `Ferramentas → Sheets2Anki → Configurar Alunos Globalmente` (Ctrl+Shift+G)
2. Selecione quais alunos devem ser sincronizados em todos os decks
3. Alunos não selecionados não aparecerão em nenhum deck
4. Use "Selecionar Todos" ou "Desmarcar Todos" para facilitar

### 3. **Configurar Sincronização AnkiWeb (Opcional)**
1. No Anki: `Ferramentas → Sheets2Anki → Configurar Sincronização AnkiWeb` (Ctrl+Shift+W)
2. Escolha entre:
   - **🚫 Desabilitado**: Sem sincronização automática
   - **🔄 Sincronizar**: Sincroniza automaticamente após atualizar decks remotos
3. Configure timeout e notificações
4. Use **"Testar Conexão"** para verificar conectividade

### 4. **Adicionar Deck Remoto**
1. No Anki: `Ferramentas → Sheets2Anki → Adicionar Novo Deck Remoto` (Ctrl+Shift+A)
2. Cole a URL da planilha publicada
3. Digite um nome para seu deck
4. **Selecione alunos específicos** para este deck (opcional)
5. O add-on criará automaticamente o deck e sincronizará

### 5. **Sincronizar**
- **Manual**: `Ferramentas → Sheets2Anki → Sincronizar Decks` (Ctrl+Shift+S)
- **Seletiva**: `Ferramentas → Sheets2Anki → Sincronizar com Seleção`
- **AnkiWeb**: Se configurado, sincroniza automaticamente após fechar resumo

### 6. **Gerenciar Sistema**
- **Desconectar**: `Ferramentas → Sheets2Anki → Desconectar um Deck Remoto` (Ctrl+Shift+D)
- **Backup**: `Ferramentas → Sheets2Anki → Backup de Decks Remotos`
- **Opções de Deck**: `Ferramentas → Sheets2Anki → Configurar Opções de Deck` (Ctrl+Shift+O)

## ⌨️ Atalhos de Teclado

| Ação | Atalho |
|------|--------|
| Adicionar Novo Deck Remoto | `Ctrl+Shift+A` |
| Sincronizar Decks | `Ctrl+Shift+S` |
| Desconectar Deck Remoto | `Ctrl+Shift+D` |
| Configurar Alunos Globalmente | `Ctrl+Shift+G` |
| Configurar Opções de Deck | `Ctrl+Shift+O` |
| Configurar Sincronização AnkiWeb | `Ctrl+Shift+W` |
| Importar Deck de Teste | `Ctrl+Shift+T` |

## 💡 Recursos Avançados

### 👥 **Sistema Completo de Gestão de Alunos**

**🎯 Funcionalidades:**
- **Configuração Global**: Define quais alunos são sincronizados em todos os decks
- **Seleção por Deck**: Permite escolher alunos específicos para cada deck
- **Subdecks Personalizados**: Cada aluno tem sua própria hierarquia
- **Note Types Únicos**: Cada aluno recebe modelos personalizados

**📂 Estrutura de Subdecks:**
```
Sheets2Anki::NomeDoDeck::
├── Aluno1::
│   ├── Importancia1::Topico1::Subtopico1::Conceito1
│   └── Importancia2::Topico2::Subtopico2::Conceito2
├── Aluno2::
│   └── ...
└── [MISSING A.]:: (para notas sem alunos específicos)
    └── ...
```

**🔧 Note Types Personalizados:**
- Formato: `Sheets2Anki - NomeDeck - NomeAluno - TipoCard`
- Campos específicos para cada aluno
- Templates personalizados baseados no tipo de card (Basic/Cloze)

### 🧪 **Cards Cloze**
Se sua coluna `PERGUNTA` contém:
```
A capital do Brasil é {{c1::Brasília}}
```
O add-on criará automaticamente um card Cloze personalizado para cada aluno.

### 🏷️ **Sistema de Tags Hierárquico Avançado**
Tags são geradas automaticamente com estrutura completa sob `Sheets2Anki`:

**🎯 8 Categorias Principais:**

1. **👥 Alunos:** `Sheets2Anki::Alunos::nome_aluno`
2. **📚 Tópicos:** `Sheets2Anki::Topicos::topico::subtopico::conceito`
3. **� Subtópicos:** `Sheets2Anki::Subtopicos::subtopico`
4. **💡 Conceitos:** `Sheets2Anki::Conceitos::conceito`
5. **🏛️ Bancas:** `Sheets2Anki::Bancas::nome_banca`
6. **� Anos:** `Sheets2Anki::Anos::ano`
7. **� Carreiras:** `Sheets2Anki::Carreiras::carreira`
8. **⭐ Importância:** `Sheets2Anki::Importancia::nivel`

**🔧 Características Avançadas:**
- **Limpeza automática**: Remove caracteres especiais, espaços extras
- **Normalização**: Substitui espaços por underscores
- **Múltiplos valores**: Suporta separação por vírgula
- **Valores padrão**: `[MISSING X.]` para campos vazios
- **Hierarquia completa**: Estrutura aninhada `topico::subtopico::conceito`

### 💾 **Sistema de Backup Profissional**

**🔧 Backup Automático:**
- Executado antes de operações importantes
- Rotação automática (mantém últimos 10 backups)
- Armazenamento em `user_files/backups/`

**🎯 Backup Manual:**
- Interface gráfica completa
- Seleção de componentes para backup
- Visualização de conteúdo dos backups
- Restauração seletiva

**📦 Componentes do Backup:**
- Configurações de decks remotos
- Preferências do usuário
- Configurações de alunos
- Opções de deck
- Configurações de sincronização AnkiWeb

### 🌐 **Sincronização AnkiWeb Inteligente**

**⚙️ Configuração:**
- **Modo Desabilitado**: Sem sincronização automática
- **Modo Sincronizar**: Sincroniza após updates de decks remotos

**🔧 Funcionalidades:**
- **Timing inteligente**: Sincroniza apenas APÓS usuário fechar resumo
- **Múltiplos métodos**: 3 APIs diferentes para compatibilidade
- **Diagnóstico avançado**: Teste de conexão com informações técnicas
- **Feedback detalhado**: Status na janela de resumo

**� APIs Suportadas:**
1. `mw.sync.sync()` (método moderno)
2. `mw.onSync()` (compatibilidade)
3. `mw.form.actionSync.trigger()` (fallback)

### 🔧 **Configurações Avançadas**

**🎛️ Opções de Deck:**
- Configuração automática de opções de deck
- Aplicação em lote para múltiplos decks
- Personalização por tipo de deck

**👥 Gestão Global de Alunos:**
- Configuração centralizada
- Aplicação automática a todos os decks
- Interface intuitiva com seleção rápida

**📊 Sistema de Debug:**
- Log detalhado em `debug_sheets2anki.log`
- Categorias específicas (SYNC, ANKIWEB_SYNC, BACKUP, etc.)
- Informações técnicas para troubleshooting

### 🧹 **Limpeza Automática Avançada**

**🔍 Detecção Automática:**
- **Erros de fórmula**: `#NAME?`, `#REF!`, `#VALUE!`, `#DIV/0!`
- **Fórmulas Excel/Sheets**: `=SOMA()`, `=VLOOKUP()`, `=IF()`, etc.
- **Caracteres especiais**: Formatação problemática
- **Espaços extras**: Normalização de texto

**📊 Relatórios:**
- Estatísticas de limpeza na sincronização
- Log detalhado de operações

## 🛠️ Solução de Problemas

### ❌ **Problemas com Alunos**
**� Soluções:**
- **Alunos não aparecem**: Verifique configuração global em Ctrl+Shift+G
- **Subdecks vazios**: Certifique-se que alunos estão listados na coluna ALUNOS
- **Nomes inconsistentes**: Use nomes exatos (case-sensitive) na planilha

### ❌ **Problemas de Sincronização AnkiWeb**
**💡 Soluções:**
- Use **"Testar Conexão"** (Ctrl+Shift+W) para diagnóstico completo
- Verifique se AnkiWeb está configurado em `Ferramentas → Sincronizar`
- Consulte informações de debug na janela de teste
- Certifique-se de usar versão atual do Anki

### ❌ **Erro de Estrutura da Planilha**
**💡 Soluções:**
- Certifique-se de ter exatamente **18 colunas obrigatórias**
- Verifique se a planilha está **publicada** (não apenas compartilhada)
- Use template fornecido como base
- Confirme que coluna ALUNOS está presente

### ❌ **Cards não aparecem**
**💡 Soluções:**
- Verifique se o campo `ID` tem valores únicos
- Certifique-se de que `SYNC?` está marcado como `true`
- Confirme que aluno está habilitado globalmente
- Consulte log `debug_sheets2anki.log` para detalhes

### ❌ **Problemas de Tags**
**💡 Soluções:**
- Tags são geradas automaticamente durante sincronização
- Caracteres especiais são limpos automaticamente
- Verifique se campos TOPICO, SUBTOPICO, CONCEITO estão preenchidos
- Use valores separados por vírgula para múltiplas tags

## 📊 Requisitos e Compatibilidade

### ✅ **Requisitos Mínimos**
- **Anki**: Versão 2.1.50 ou superior (testado até 2.1.66)
- **Internet**: Conexão estável para sincronização
- **Google Sheets**: Planilha publicada com 18 colunas obrigatórias
- **Sistema**: Windows, macOS, Linux

### ✅ **Funcionalidades Testadas**
- ✅ Sistema de gestão de alunos (100% funcionando)
- ✅ Sincronização seletiva (100% funcionando)
- ✅ Sistema de tags hierárquico (100% funcionando)
- ✅ Sincronização AnkiWeb (100% funcionando)
- ✅ Sistema de backup (100% funcionando)
- ✅ Limpeza automática (100% funcionando)
- ✅ Configurações avançadas (100% funcionando)

### 🔧 **APIs Suportadas**
**Sincronização AnkiWeb:**
- ✅ `mw.sync.sync()` (método moderno - Anki 2.1.50+)
- ✅ `mw.onSync()` (compatibilidade - versões anteriores)
- ✅ `mw.form.actionSync.trigger()` (fallback universal)

## 🔒 Limitações Conhecidas

- **Sem sincronização reversa**: Mudanças no Anki não afetam a planilha
- **Estrutura fixa**: Deve usar exatamente as 18 colunas especificadas
- **Gestão de alunos**: Nomes devem ser consistentes (case-sensitive)
- **Dependência de internet**: Requer conexão para sincronizar com planilhas

## 🏆 Status do Projeto

### ✅ **v2.1 - Sistema Completo de Alunos (Atual)**
- 👥 **Sistema de gestão de alunos** completo e funcional
- 📂 **Subdecks personalizados** para cada aluno
- 🏷️ **Note types individuais** para cada aluno
- ⚙️ **Configuração global** de alunos
- 🔄 **Sincronização seletiva** por aluno
- 🌐 **Sincronização AnkiWeb** inteligente e configurável
- 💾 **Sistema de backup** profissional
- 🏷️ **Tags hierárquicas** com 8 categorias
- 🧹 **Limpeza automática** avançada

### 📈 **Melhorias da v2.1**
- 🆕 **Campo ALUNOS**: Nova coluna obrigatória para gestão de alunos
- 👥 **Configuração Global**: Interface para selecionar alunos globalmente
- � **Subdecks por Aluno**: Hierarquia personalizada para cada aluno
- 🏷️ **Note Types Únicos**: Modelos personalizados por aluno
- ⚡ **Performance otimizada**: Sincronização inteligente por aluno
- � **Configurações avançadas**: Opções de deck e debug melhorados

## 📚 Documentação Técnica

### 📁 **Estrutura de Arquivos**
```
sheets2anki/
├── README.md                    # ← Guia principal (este arquivo)
├── __init__.py                  # Módulo principal de integração
├── src/                         # Código principal do add-on
│   ├── student_manager.py      # Sistema de gestão de alunos
│   ├── data_processor.py       # Processamento e tags hierárquicas
│   ├── sync.py                 # Lógica de sincronização
│   ├── ankiweb_sync.py         # Sistema AnkiWeb
│   ├── backup_system.py        # Sistema de backup
│   ├── templates_and_definitions.py  # Constantes e templates
│   └── [outros módulos]
├── sample data/                 # Dados de exemplo
├── scripts/                     # Scripts de build
└── build/                       # Pacotes compilados
```

### 🔧 **Para Desenvolvedores**
- **Modular**: Código organizado em módulos específicos
- **Extensível**: Sistema de alunos facilmente expandível
- **Debug**: Logging detalhado em múltiplas categorias
- **Testável**: Estrutura preparada para testes automatizados

### 🧪 **Sistema de Debug**
- **Arquivo de log**: `debug_sheets2anki.log` no diretório do add-on
- **Categorias**: SYSTEM, SYNC, ANKIWEB_SYNC, BACKUP, STUDENT, etc.
- **Níveis**: Info, warning, error com timestamps
- **Integração**: Debug automático durante todas as operações

## 🔄 Histórico de Versões

### **v2.1 - Sistema Completo de Alunos (2025)**
- � **Campo ALUNOS**: Nova coluna obrigatória (agora 18 colunas)
- 👥 **Gestão de Alunos**: Sistema completo com configuração global
- � **Subdecks Personalizados**: Hierarquia específica por aluno
- 🏷️ **Note Types Únicos**: Modelos personalizados para cada aluno
- ⚡ **Sincronização Inteligente**: Filtragem automática por aluno
- � **Configurações Avançadas**: Opções de deck e debug melhorados

### **v2.0 - Base Profissional (2024)**
- 🌐 **Sincronização AnkiWeb**: Automática configurável
- 🏷️ **Tags hierárquicas**: 8 categorias organizadas
- 💾 **Sistema de backup**: Manual e automático
- 🧹 **Código otimizado**: Remoção de legado
- 🔍 **Diagnóstico avançado**: Teste de conexão melhorado

## 🤝 Contribuição

### 📝 **Como Contribuir**
1. **Fork do projeto** no GitHub
2. **Foque no sistema de alunos** - área principal de desenvolvimento
3. **Teste com dados reais** usando 18 colunas obrigatórias
4. **Documente mudanças** especialmente relacionadas a gestão de alunos
5. **Submeta pull request** com descrição detalhada

### 🧪 **Desenvolvimento Local**
```bash
# Estrutura de teste recomendada
# 1. Crie planilha com 18 colunas (incluindo ALUNOS)
# 2. Configure alunos globalmente
# 3. Teste sincronização seletiva por aluno
# 4. Verifique criação de subdecks personalizados
```

### 📚 **Áreas Prioritárias**
- **Sistema de alunos**: Expansão e melhorias
- **Performance**: Otimização para muitos alunos
- **Interface**: Melhorias na seleção de alunos
- **Backup**: Integração com sistema de alunos

## 📧 Suporte

**🔍 Para resolver problemas:**
1. **Verifique configuração de alunos**: Ctrl+Shift+G para configuração global
2. **Consulte logs**: `debug_sheets2anki.log` com informações detalhadas
3. **Use diagnósticos**: "Testar Conexão" (Ctrl+Shift+W) para AnkiWeb
4. **Confirme estrutura**: 18 colunas obrigatórias incluindo ALUNOS

**🌐 Recursos:**
- **Template atualizado**: [Google Sheets com 18 colunas](https://docs.google.com/spreadsheets/d/1urrp2t8xA2C0f3vLTdQyQblVu5ur0lirFCN9KyCVLlY/edit?usp=sharing)
- **Log de debug**: Arquivo detalhado para troubleshooting
- **Sistema de backup**: Restauração em caso de problemas