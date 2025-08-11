# 📚 Sheets2Anki

**Transforme suas planilhas do Google Sheets em poderosos decks do Anki!**

O **Sheets2Anki** é um add-on profissional que sincroniza automaticamente seus decks do Anki com planilhas do Google Sheets. Sua planilha funciona como a fonte principal dos seus cards - todas as mudanças, adições e remoções são refletidas automaticamente no Anki quando você sincroniza.

🎯 **Ideal para:** Professores, estudantes, criadores de conteúdo educacional e qualquer pessoa que precise organizar grandes quantidades de flashcards de forma colaborativa e eficiente.

## 🌟 Por que usar o Sheets2Anki?

### ✅ **Vantagens Únicas**
- **📊 Interface Familiar:** Use o Google Sheets que você já conhece para criar cards
- **👥 Colaboração:** Múltiplas pessoas podem editar a mesma planilha
- **🎯 Gestão Individual:** Cada aluno pode ter seus próprios cards e subdecks
- **🏷️ Organização Inteligente:** Tags automáticas e hierarquia de subdecks
- **🔄 Sincronização Bidirecional:** AnkiWeb + Sheets = Sempre atualizado
- **💾 Backup Automático:** Nunca perca suas configurações

## ✨ Principais Funcionalidades

### 👥 **Sistema Avançado de Gestão de Alunos**
- **Configuração Global:** Defina uma vez quais alunos sincronizar em todos os decks
- **Subdecks Personalizados:** Cada aluno tem sua própria hierarquia organizada
- **Note Types Únicos:** Modelos de card personalizados para cada aluno
- **Filtragem Inteligente:** Sincronize apenas os alunos que você escolher

### 🔄 **Sincronização Seletiva e Inteligente**
- **Controle Total:** Coluna `SYNC?` permite escolher quais cards sincronizar
- **Múltiplos Formatos:** Aceita `true`, `false`, `sim`, `não`, `1`, `0` e variações
- **Sincronização AnkiWeb:** Automática após atualizar seus decks
- **Backup de Segurança:** Proteção automática antes de restaurações

### 🏷️ **Sistema de Tags Hierárquico Completo**
Organização automática em 8 categorias:
- **👥 Alunos:** `Sheets2Anki::Alunos::nome_aluno`
- **📚 Tópicos:** `Sheets2Anki::Topicos::topico::subtopico::conceito`
- **🏛️ Bancas:** `Sheets2Anki::Bancas::nome_banca`
- **📅 Anos:** `Sheets2Anki::Anos::2024`
- **💼 Carreiras:** `Sheets2Anki::Carreiras::carreira`
- **⭐ Importância:** `Sheets2Anki::Importancia::alta`
- **🔖 Tags Extras:** Suporte a tags personalizadas

### 💾 **Sistema de Backup Profissional**
- **Backup Manual:** Interface completa para criar/restaurar backups
- **Backup de Segurança:** Automático antes de restaurações
- **Versionamento:** Mantém histórico de backups
- **Configurações Completas:** Decks, alunos, preferências e note types

### 🧪 **Suporte Completo a Cards Cloze**
- **Detecção Automática:** Reconhece padrões `{{c1::texto}}`
- **Note Types Personalizados:** Um para cada aluno automaticamente
- **Flexibilidade Total:** Misture cards básicos e cloze na mesma planilha
## 📋 Como Configurar sua Planilha

Sua planilha do Google Sheets deve ter exatamente **18 colunas obrigatórias**. Use nosso [**modelo pronto**](https://docs.google.com/spreadsheets/d/1urrp2t8xA2C0f3vLTdQyQblVu5ur0lirFCN9KyCVLlY/edit?usp=sharing) como base!

### 📊 **Estrutura das Colunas**

| # | Coluna | Descrição | Exemplo |
|---|--------|-----------|---------|
| 1 | **ID** | Identificador único | `Q001`, `Q002` |
| 2 | **PERGUNTA** | Texto do card/frente | `Qual é a capital do Brasil?` |
| 3 | **LEVAR PARA PROVA** | Resposta principal/verso | `Brasília` |
| 4 | **SYNC?** | Controle de sincronização | `true`, `false`, `sim` |
| 5 | **ALUNOS** | Lista de alunos (separados por vírgula) | `João, Maria, Pedro` |
| 6 | **INFO COMPLEMENTAR** | Informações extras | `Fundada em 1960` |
| 7 | **INFO DETALHADA** | Detalhes expandidos | `Planejada por Oscar Niemeyer` |
| 8 | **EXEMPLO 1** | Primeiro exemplo | `Também é sede do governo` |
| 9 | **EXEMPLO 2** | Segundo exemplo | `Localizada no Distrito Federal` |
| 10 | **EXEMPLO 3** | Terceiro exemplo | `Patrimônio da Humanidade` |
| 11 | **TOPICO** | Categoria principal | `Geografia` |
| 12 | **SUBTOPICO** | Subcategoria | `Capitais` |
| 13 | **CONCEITO** | Conceito específico | `Brasil` |
| 14 | **BANCAS** | Bancas organizadoras | `CESPE, FCC` |
| 15 | **ULTIMO ANO EM PROVA** | Ano da última questão | `2024` |
| 16 | **CARREIRA** | Área/carreira | `Concursos Públicos` |
| 17 | **IMPORTANCIA** | Nível de relevância | `Alta`, `Média`, `Baixa` |
| 18 | **TAGS ADICIONAIS** | Tags extras | `fundamental, básico` |

### 👥 **Campo ALUNOS - Funcionalidade Principal**

O campo **ALUNOS** é o coração do sistema de gestão individualizada:

**✅ Formatos aceitos:**
- `João, Maria, Pedro` (vírgula)
- `João; Maria; Pedro` (ponto e vírgula)  
- `João|Maria|Pedro` (pipe)
- `João` (aluno único)
- *(vazio)* - vai para deck especial `[MISSING A.]`

**🎯 Como funciona:**
- Cada aluno listado recebe uma cópia da questão em seu subdeck pessoal
- Estrutura: `Sheets2Anki::NomeDeck::Aluno::Importancia::Topico::Subtopico::Conceito`
- Note types personalizados: `Sheets2Anki - NomeDeck - Aluno - TipoCard`

### 🔄 **Controle de Sincronização (SYNC?)**

**✅ Para SINCRONIZAR:**
- `true`, `TRUE`, `sim`, `SIM`, `yes`, `1`, `v` ou deixar vazio

**❌ Para NÃO sincronizar:**
- `false`, `FALSE`, `não`, `nao`, `no`, `0`, `f`

### 🧪 **Cards Cloze Automáticos**

Para criar cards cloze, use o padrão na coluna PERGUNTA:
```
A capital do Brasil é {{c1::Brasília}} e fica na região {{c2::Centro-Oeste}}.
```

O add-on detectará automaticamente e criará note types cloze personalizados para cada aluno!

## 🚀 Guia de Instalação e Uso

### 📥 **Instalação**

1. **No Anki:** `Ferramentas → Complementos → Obter Complementos...`
2. **Cole o código:** *(código será disponibilizado no AnkiWeb)*
3. **Reinicie o Anki**
4. **Menu disponível:** `Ferramentas → Sheets2Anki`

### 🏁 **Primeiros Passos - Setup Inicial**

#### **Passo 1: Prepare sua Planilha**
1. **Use o modelo:** [Template Google Sheets](https://docs.google.com/spreadsheets/d/1urrp2t8xA2C0f3vLTdQyQblVu5ur0lirFCN9KyCVLlY/edit?usp=sharing)
2. **Preencha os dados:** Adicione suas questões seguindo as 18 colunas
3. **Configure alunos:** Liste os nomes na coluna ALUNOS
4. **Publique a planilha:**
   - `Arquivo → Compartilhar → Publicar na web`
   - **Importante:** Escolha `Valores separados por tabulação (.tsv)`
   - Copie o link gerado

#### **Passo 2: Configure os Alunos Globalmente**
```
Ferramentas → Sheets2Anki → Configurar Alunos Globalmente (Ctrl+Shift+G)
```
- ✅ Marque os alunos que devem aparecer em TODOS os decks
- 💡 Alunos não marcados aqui NÃO aparecerão em nenhum deck
- 🔄 Use "Selecionar Todos" ou "Desmarcar Todos" para facilitar

#### **Passo 3: Adicione seu Primeiro Deck**
```
Ferramentas → Sheets2Anki → Adicionar Novo Deck Remoto (Ctrl+Shift+A)
```
1. **Cole a URL** da planilha publicada
2. **Nomeie seu deck** (sugestão automática disponível)
3. **Confirme** - o addon criará automaticamente toda a estrutura!

#### **Passo 4: Primeira Sincronização**
```
Ferramentas → Sheets2Anki → Sincronizar Decks Remotos (Ctrl+Shift+S)
```
- 🎉 Seus cards serão criados automaticamente
- 📂 Subdecks organizados por aluno, importância e tópico
- 🏷️ Tags hierárquicas aplicadas automaticamente

### ⚙️ **Configurações Opcionais**

#### **Sincronização AnkiWeb Automática**
```
Ferramentas → Sheets2Anki → Configurar Sincronização AnkiWeb (Ctrl+Shift+W)
```
- **🚫 Desabilitado:** Não sincroniza automaticamente
- **🔄 Automático:** Sincroniza com AnkiWeb após atualizar decks
- **🧪 Testar Conexão:** Verifica se está funcionando

#### **Sistema de Backup**
```
Ferramentas → Sheets2Anki → Backup de Decks Remotos
```
- 💾 Backup manual de todas as configurações
- 🔄 Restauração completa se necessário
- �️ Backup de segurança antes de operações importantes

### 🔄 **Fluxo de Trabalho Diário**

1. **📝 Edite sua planilha** no Google Sheets (adicione/modifique/remova cards)
2. **🔄 Sincronize no Anki:** `Ctrl+Shift+S` 
3. **📱 Estude normalmente** - cards atualizados automaticamente
4. **☁️ AnkiWeb sincroniza** sozinho (se configurado)

### ⌨️ **Atalhos Essenciais**

| Ação | Atalho | Descrição |
|------|--------|-----------|
| **Sincronizar** | `Ctrl+Shift+S` | Atualiza todos os decks |
| **Adicionar Deck** | `Ctrl+Shift+A` | Conecta nova planilha |
| **Config. Alunos** | `Ctrl+Shift+G` | Gerencia alunos globais |
| **Config. AnkiWeb** | `Ctrl+Shift+W` | Configura sync automático |
| **Desconectar Deck** | `Ctrl+Shift+D` | Remove conexão com planilha |
## 🎯 Recursos Avançados

### 📂 **Como Funciona a Estrutura de Subdecks**

Quando você sincroniza, o addon cria automaticamente uma hierarquia organizada:

```
Sheets2Anki::
└── NomeDoSeuDeck::
    ├── João::
    │   ├── Alta::Geografia::Capitais::Brasil
    │   └── Média::História::Descobrimentos::Portugal
    ├── Maria::
    │   ├── Alta::Matemática::Álgebra::Equações
    │   └── Baixa::Química::Tabela::Elementos
    └── [MISSING A.]:: (cards sem alunos específicos)
        └── Alta::Geral::Diversos::Conceitos
```

### 🏷️ **Sistema de Tags Automáticas**

Cada card recebe tags organizadas automaticamente:

**🎯 Categorias de Tags:**
- `Sheets2Anki::Topicos::geografia::capitais::brasil` - Hierarquia completa
- `Sheets2Anki::Bancas::cespe` - Banca organizadora
- `Sheets2Anki::Anos::2024` - Ano da questão
- `Sheets2Anki::Carreiras::concursos_publicos` - Área de aplicação
- `Sheets2Anki::Importancia::alta` - Nível de relevância

> **📝 Nota:** Tags baseadas na coluna ALUNOS foram removidas para simplificar a lógica do sistema.

### 🔄 **Sincronização Inteligente**

**🎯 O que acontece durante a sincronização:**

1. **Cards Novos:** Criados automaticamente com tags e subdecks
2. **Cards Modificados:** Atualizados preservando progresso de estudo
3. **Cards Removidos:** Deletados se não estão mais na planilha
4. **Mudança de Alunos:** Movidos para novos subdecks automaticamente
5. **SYNC? = false:** Cards ignorados mas não deletados

**💡 Dica:** O progresso de revisão (intervalos, facilidade) é sempre preservado!

### 🧪 **Suporte Completo a Cards Cloze**

**Detecção Automática:**
- O addon detecta padrões `{{c1::texto}}` na coluna PERGUNTA
- Cria automaticamente note types cloze personalizados
- Um note type para cada aluno: `Sheets2Anki - DeckName - Aluno - Cloze`

**Exemplo na Planilha:**
```
PERGUNTA: A capital do {{c1::Brasil}} é {{c2::Brasília}}
LEVAR PARA PROVA: Informações adicionais sobre a capital
```

### 💾 **Sistema de Backup Robusto**

**Backup Manual:**
```
Ferramentas → Sheets2Anki → Backup de Decks Remotos
```
- Escolha o que incluir: decks, alunos, configurações
- Exporta tudo em arquivo .zip
- Restauração completa quando necessário

**Backup de Segurança:**
- Automático antes de restaurar backups existentes
- Evita perda de dados durante restaurações
- Armazenado separadamente dos backups manuais

### 🌐 **Sincronização AnkiWeb Automática**

**Como Funciona:**
1. Você sincroniza com a planilha (Ctrl+Shift+S)
2. O addon atualiza seus decks locais
3. **Automaticamente** sincroniza com AnkiWeb (se configurado)
4. Seus outros dispositivos recebem as atualizações

**Compatibilidade:**
- ✅ Anki 2.1.50+ (método moderno)
- ✅ Versões anteriores (métodos de compatibilidade)
- ✅ AnkiMobile, AnkiDroid, AnkiWeb
## 🛠️ Solução de Problemas

### ❓ **Problemas Comuns e Soluções**

#### **🔴 "Nenhum aluno foi encontrado para sincronizar"**
**💡 Soluções:**
1. Vá em `Ctrl+Shift+G` → Marque os alunos desejados
2. Verifique se os nomes na planilha estão exatamente iguais aos configurados
3. Certifique-se de que a coluna ALUNOS está preenchida

#### **� "Erro ao carregar planilha" ou "URL inválida"**
**💡 Soluções:**
1. **Verifique a publicação:**
   - `Arquivo → Compartilhar → Publicar na web`
   - **Importante:** `Valores separados por tabulação (.tsv)`
2. **URL deve ser parecida com:**
   ```
   https://docs.google.com/spreadsheets/d/e/[ID]/pub?output=tsv
   ```
3. **Teste no navegador:** Cole a URL - deve baixar um arquivo .tsv

#### **🔴 Cards não aparecem após sincronização**
**� Soluções:**
1. **Verifique a coluna SYNC?:** Deve estar `true`, `sim`, `1` ou vazia
2. **IDs únicos:** Cada linha deve ter um ID diferente na coluna 1
3. **Alunos habilitados:** `Ctrl+Shift+G` → Confirme os alunos marcados

#### **� Subdecks não se organizam corretamente**
**💡 Soluções:**
1. **Preencha os campos:** IMPORTANCIA, TOPICO, SUBTOPICO, CONCEITO
2. **Aguarde a sincronização:** A reorganização acontece após finalizar
3. **Restart do Anki:** Às vezes é necessário reiniciar para ver a estrutura

#### **🔴 Sincronização AnkiWeb não funciona**
**💡 Soluções:**
1. **Use o teste:** `Ctrl+Shift+W` → "Testar Conexão"
2. **Verifique login:** `Ferramentas → Sincronizar` deve estar funcionando
3. **Tente modo manual:** Desabilite o automático e sincronize manualmente

### 📊 **Verificações de Integridade**

#### **✅ Checklist da Planilha**
- [ ] Exatamente **18 colunas** na ordem correta
- [ ] Campo **ID** preenchido e único para cada linha
- [ ] Campo **ALUNOS** preenchido (ou deixar vazio para `[MISSING A.]`)
- [ ] Coluna **SYNC?** configurada (`true`/`false` ou vazio)
- [ ] Planilha **publicada** como TSV (não apenas compartilhada)

#### **✅ Checklist do Anki**
- [ ] Alunos configurados globalmente (`Ctrl+Shift+G`)
- [ ] URL da planilha válida e acessível
- [ ] Anki atualizado (versão 2.1.50+)
- [ ] Complemento instalado e ativo

### 🔧 **Ferramentas de Diagnóstico**

#### **Log de Debug**
Consulte o arquivo `debug_sheets2anki.log` na pasta do complemento:
```
Anki → Ferramentas → Complementos → [Sheets2Anki] → Ver arquivos
```

#### **Teste de Conectividade**
```
Ctrl+Shift+W → "Testar Conexão"
```
- Mostra status da conexão AnkiWeb
- Informa sobre compatibilidade
- Exibe detalhes técnicos

#### **Informações do Sistema**
No final da janela de sincronização, veja:
- Quantos cards foram criados/atualizados
- Quais alunos foram processados
- Estatísticas detalhadas da planilha

### 🆘 **Casos Extremos**

#### **Reset Completo**
Se algo der muito errado:
1. **Backup primeiro:** `Ferramentas → Sheets2Anki → Backup`
2. **Desconectar deck:** `Ctrl+Shift+D`
3. **Reconfigurar alunos:** `Ctrl+Shift+G`
4. **Reconectar deck:** `Ctrl+Shift+A`

#### **Restaurar Backup**
Se perdeu dados importantes:
1. `Ferramentas → Sheets2Anki → Backup de Decks Remotos`
2. Clique em "Restaurar Backup"
3. Escolha o backup desejado
4. Confirme a restauração

## 📊 Compatibilidade e Requisitos

### ✅ **Requisitos do Sistema**
- **Anki:** Versão 2.1.50 ou superior
- **Sistema Operacional:** Windows, macOS ou Linux
- **Conexão:** Internet estável para sincronização
- **Google Sheets:** Planilha publicada com as 18 colunas obrigatórias

### 🔧 **Compatibilidade Testada**
- ✅ **Anki Desktop:** 2.1.50 - 2.1.66 (e superiores)
- ✅ **AnkiMobile:** iOS (sincronização via AnkiWeb)
- ✅ **AnkiDroid:** Android (sincronização via AnkiWeb) 
- ✅ **AnkiWeb:** Navegador (acesso completo aos decks)

### 🌐 **Funcionalidades por Plataforma**

| Funcionalidade | Anki Desktop | AnkiMobile | AnkiDroid | AnkiWeb |
|----------------|--------------|------------|-----------|---------|
| **Criar/Editar Cards** | ❌ Planilha | ❌ Planilha | ❌ Planilha | ❌ Planilha |
| **Estudar Cards** | ✅ Completo | ✅ Completo | ✅ Completo | ✅ Completo |
| **Ver Subdecks** | ✅ Completo | ✅ Completo | ✅ Completo | ✅ Completo |
| **Tags Hierárquicas** | ✅ Completo | ✅ Completo | ✅ Completo | ✅ Completo |
| **Sincronização** | ✅ Automática | ✅ Via AnkiWeb | ✅ Via AnkiWeb | ✅ Nativo |

### 🚀 **Performance e Limites**

**📈 Capacidade Testada:**
- ✅ **Até 10.000 cards** por deck (performance excelente)
- ✅ **Até 50 alunos** por deck (organizados automaticamente)
- ✅ **Até 20 decks** conectados simultaneamente
- ✅ **Sincronização rápida** (< 30 segundos para 1000 cards)

**⚡ Otimizações:**
- Sincronização incremental (apenas mudanças)
- Cache inteligente de planilhas
- Processamento paralelo de alunos
- Limpeza automática de dados órfãos

## 🏆 Casos de Uso Reais

### 👨‍🏫 **Para Professores**
**📚 Gerenciar Múltiplas Turmas:**
- Crie uma planilha por disciplina
- Liste alunos de diferentes turmas na coluna ALUNOS
- Configure `Ctrl+Shift+G` para sincronizar apenas turmas ativas
- Cada aluno vê apenas seus cards organizados

**🎯 Exemplo Prático:**
```
ID: MAT001
PERGUNTA: Qual a fórmula da área do círculo?
ALUNOS: Turma_A, Turma_B, João_Reforço
TOPICO: Matemática
SUBTOPICO: Geometria
CONCEITO: Círculo
```

### � **Para Grupos de Estudo**
**📖 Estudo Colaborativo:**
- Cada membro contribui com questões na planilha
- Filtre conteúdo por pessoa: `ALUNOS: Maria, João`
- Tags automáticas organizam por assunto
- Progresso individual preservado

### 🎓 **Para Concursos/Vestibulares**
**📋 Organização por Matéria:**
- BANCAS: `CESPE, FCC, VUNESP`
- CARREIRAS: `Magistratura, Fiscal, Analista`
- ANOS: `2023, 2024`
- Hierarquia: `Direito::Constitucional::Direitos_Fundamentais`

### 🏫 **Para Instituições de Ensino**
**📊 Gestão Curricular:**
- Coordenação centralizada na planilha
- Professores editam suas áreas
- Alunos recebem conteúdo personalizado
- Backup automático preserva histórico

## 💡 Dicas e Melhores Práticas

### � **Organização da Planilha**
1. **IDs Consistentes:** Use prefixos como `MAT001`, `HIS001`, `BIO001`
2. **Nomes de Alunos:** Mantenha sempre os mesmos nomes (case-sensitive)
3. **Categorização:** Preencha SEMPRE os campos TOPICO, SUBTOPICO, CONCEITO
4. **Importância:** Use escalas consistentes (`Alta`, `Média`, `Baixa`)

### 🎯 **Estratégias de Estudo**
1. **Filtro por Tags:** Use o navegador do Anki para estudar temas específicos
2. **Progressão Gradual:** Comece com cards de `Importancia::Alta`
3. **Revisão Temática:** Estude por `Topicos::materia` para dominar áreas
4. **Acompanhamento:** Use estatísticas do Anki para medir progresso

### 🔄 **Fluxo de Trabalho Eficiente**
1. **Manhã:** Sincronize (`Ctrl+Shift+S`) para pegar atualizações
2. **Durante o Dia:** Estude normalmente no Anki
3. **Noite:** Edite planilha se necessário
4. **AnkiWeb:** Sincroniza automaticamente em outros dispositivos

### 💾 **Backup e Segurança**
1. **Backup Semanal:** `Ferramentas → Sheets2Anki → Backup`
2. **Versione Planilhas:** Mantenha copies de segurança no Google Drive
3. **Teste Restauração:** Pratique a restauração em ambiente de teste
4. **Documente Mudanças:** Registre alterações importantes
## ❓ FAQ - Perguntas Frequentes

### **🤔 "Posso usar qualquer planilha do Google Sheets?"**
**R:** Não. A planilha deve ter exatamente as 18 colunas na ordem especificada e estar **publicada** como TSV. Use nosso [template](https://docs.google.com/spreadsheets/d/1urrp2t8xA2C0f3vLTdQyQblVu5ur0lirFCN9KyCVLlY/edit?usp=sharing) como base.

### **🤔 "Como funciona o sistema de alunos?"**
**R:** Cada nome na coluna ALUNOS gera um subdeck separado. Configure globalmente (`Ctrl+Shift+G`) quais alunos sincronizar. Alunos não configurados não aparecerão em nenhum deck.

### **🤔 "Meu progresso de estudo é perdido quando sincronizo?"**
**R:** Não! O progresso (intervalos, facilidade, estatísticas) é sempre preservado. Apenas o conteúdo dos cards é atualizado.

### **🤔 "Posso usar em múltiplos dispositivos?"**
**R:** Sim! Configure a sincronização AnkiWeb (`Ctrl+Shift+W`) e seus decks aparecerão em todos os dispositivos automaticamente.

### **🤔 "Como criar cards cloze?"**
**R:** Use o padrão `{{c1::resposta}}` na coluna PERGUNTA. O addon detecta automaticamente e cria note types cloze personalizados.

### **🤔 "Posso compartilhar apenas alguns cards com certos alunos?"**
**R:** Sim! Liste apenas os alunos desejados na coluna ALUNOS de cada linha. Cards sem alunos vão para o deck `[MISSING A.]`.

### **🤔 "E se eu mudar o nome de um aluno?"**
**R:** Configure o novo nome em `Ctrl+Shift+G` e desative o antigo. O sistema limpará automaticamente os dados do nome anterior.

### **🤔 "Posso usar offline?"**
**R:** Apenas para estudar. A sincronização com planilhas requer internet, mas você pode estudar os cards normalmente offline.

## 🔗 Links Úteis

- 📋 **[Template Google Sheets](https://docs.google.com/spreadsheets/d/1urrp2t8xA2C0f3vLTdQyQblVu5ur0lirFCN9KyCVLlY/edit?usp=sharing)** - Modelo pronto para usar
- 📚 **[AnkiWeb](https://ankiweb.net)** - Sincronização na nuvem
- 🎯 **[Manual do Anki](https://docs.ankiweb.net/)** - Documentação oficial
- 💾 **[Backup Google Drive](https://drive.google.com)** - Para suas planilhas

---

🎉 **Pronto para começar?** Baixe o template, configure seus alunos e transforme suas planilhas em poderosos decks do Anki!