# 📚 Sheets2Anki

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

### � **Sistema de Consistência de Nomes Automático**
- **Correção Automática:** O sistema detecta e corrige automaticamente inconsistências nos nomes dos note types
- **Sincronização Inteligente:** Durante cada sincronização, verifica se os nomes no Anki estão alinhados com a configuração
- **Atualização Transparente:** Corrige diferenças entre nomes remotos e locais sem intervenção manual
- **Preservação de Dados:** Mantém todo o histórico de estudo e configurações durante as correções

### �👥 **Sistema Avançado de Gestão de Alunos**
- **Configuração Global:** Defina uma vez quais alunos sincronizar em todos os decks
- **Subdecks Personalizados:** Cada aluno tem sua própria hierarquia organizada
- **Note Types Únicos:** Modelos de card personalizados para cada aluno
- **Filtragem Inteligente:** Sincronize apenas os alunos que você escolher

### 🔄 **Sincronização Seletiva e Inteligente**
- **Controle Total:** Coluna `SYNC?` permite escolher quais cards sincronizar
- **Múltiplos Formatos:** Aceita `true`, `false`, `sim`, `não`, `1`, `0` e variações
- **Sincronização AnkiWeb:** Automática após atualizar seus decks
- **Backup de Segurança:** Proteção automática antes de restaurações

### 📊 **Resumo de Sincronização Aprimorado**
- **Visualização Dupla:** Modos "Simplificado" e "Completo" para diferentes necessidades
- **Ordem Otimizada:** No modo "Completo", o resumo geral agregado aparece primeiro, seguido dos detalhes individuais
- **Métricas Detalhadas:** Estatísticas completas da planilha e resultados por deck
- **Interface Responsiva:** Suporte automático para dark mode e layout adaptável

### 🏷️ **Sistema de Tags Hierárquico Completo**
Organização automática em 8 categorias:
- **👥 Alunos:** `Sheets2Anki::Alunos::aluno`
- **📚 Tópicos:** `Sheets2Anki::Topicos::topico::subtopico::conceito`
- **🏛️ Bancas:** `Sheets2Anki::Bancas::banca`
- **📅 Anos:** `Sheets2Anki::Anos::ano`
- **💼 Carreiras:** `Sheets2Anki::Carreiras::carreira`
- **⭐ Importância:** `Sheets2Anki::Importancia::importancia`
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

Sua planilha do Google Sheets deve ter exatamente **19 colunas obrigatórias**. 
Use nosso [**modelo pronto**](https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing) como base!

### 📊 **Estrutura das Colunas**

| # | Coluna | Descrição | Exemplo |
|---|--------|-----------|---------|
| 1 | **ID** | Identificador único | `Q001`, `Q002` |
| 2 | **ALUNOS** | Lista de alunos (separados por vírgula) | `João, Maria, Pedro` |
| 3 | **SYNC?** | Controle de sincronização | `true`, `false`, `sim` |
| 4 | **IMPORTANCIA** | Nível de relevância | `Alta`, `Média`, `Baixa` |
| 5 | **TOPICO** | Categoria principal | `Geografia` |
| 6 | **SUBTOPICO** | Subcategoria | `Capitais` |
| 7 | **CONCEITO** | Conceito específico | `Brasil` |
| 8 | **PERGUNTA** | Texto do card/frente | `Qual é a capital do Brasil?` |
| 9 | **LEVAR PARA PROVA** | Resposta principal/verso | `Brasília` |
| 10 | **INFO COMPLEMENTAR** | Informações extras | `Fundada em 1960` |
| 11 | **INFO DETALHADA** | Detalhes expandidos | `Planejada por Oscar Niemeyer` |
| 12 | **ILUSTRAÇÃO HTML** | Imagens e HTML | `<img src="https://...">` |
| 13 | **EXEMPLO 1** | Primeiro exemplo | `Também é sede do governo` |
| 14 | **EXEMPLO 2** | Segundo exemplo | `Localizada no Distrito Federal` |
| 15 | **EXEMPLO 3** | Terceiro exemplo | `Patrimônio da Humanidade` |
| 16 | **BANCAS** | Bancas organizadoras | `CESPE, FCC` |
| 17 | **ULTIMO ANO EM PROVA** | Ano da última questão | `2024` |
| 18 | **CARREIRAS** | Área/carreira | `Concursos Públicos` |
| 19 | **TAGS ADICIONAIS** | Tags extras | `fundamental, básico` |

### 🖼️ **Coluna ILUSTRAÇÃO HTML**

A coluna **ILUSTRAÇÃO HTML** permite adicionar imagens, diagramas e qualquer conteúdo HTML aos seus cards:

**✅ Exemplos de uso:**
- `<img src="https://exemplo.com/diagrama.png" style="max-width:300px;">`
- `<a href="https://link.com">Clique aqui</a>`
- `<div style="color:red;">Texto destacado</div>`

**🎯 Posicionamento:** A ilustração aparece no **verso do card**, após a resposta principal, para contextualizar a informação sem "dar dicas" na pergunta.

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
- `true`, `TRUE`, `sim`, `SIM`, `yes`, `1`, `v`

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
- Use o modelo [Template Google Sheets](https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing).
- Crie uma cópia do modelo.
- Preencha os dados seguindo a estrutura das colunas.

#### **Passo 2: Configure o comportamento do addon**
- Configure a Configuração Global de Alunos.
- Configure o Gerenciamento de Opções de Deck.
- Configure a Sincronização Automática com AnkiWeb.

#### **Passo 3: Adicione o Deck Remoto**
- Abra sua planilha no Google Sheets.
- Clique em `Compartilhar` (canto superior direito).
- Configure como `Qualquer pessoa com o link pode ver`.
- Copie o link de compartilhamento (`/edit?usp=sharing`).
- Cole o link dentro do addon.
- Confirme, o addon criará automaticamente toda a estrutura!

#### **Passo 4: Sincronização**
- Modifique os dados da planilha.
- Faça uma sincroniação dentro do addon
- Seus cards serão atualizados automaticamente.

## 🎯 Recursos Avançados

### ⌨️ **Atalhos Essenciais**

| Ação | Atalho | Descrição |
|------|--------|-----------|
| **Sincronizar** | `Ctrl+Shift+S` | Atualiza todos os decks |
| **Adicionar Deck** | `Ctrl+Shift+A` | Conecta nova planilha |
| **Config. Alunos** | `Ctrl+Shift+G` | Gerencia alunos globais |
| **Config. AnkiWeb** | `Ctrl+Shift+W` | Configura sync automático |
| **Desconectar Deck** | `Ctrl+Shift+D` | Remove conexão com planilha |

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

### 🔄 **Sincronização Inteligente**

**🎯 O que acontece durante a sincronização:**

1. **Cards Novos:** Criados automaticamente com tags e subdecks
2. **Cards Modificados:** Atualizados preservando progresso de estudo
3. **Cards Removidos:** Deletados se não estão mais na planilha
4. **Mudança de Alunos:** Movidos para novos subdecks automaticamente
5. **SYNC? = false:** Cards ignorados mas não deletados
6. **🆕 Consistência Automática:** Sistema verifica e corrige nomes inconsistentes automaticamente

**💡 Dica:** O progresso de revisão (intervalos, facilidade) é sempre preservado!

### 🔧 **Gerenciamento de Cards** ⭐

#### **Sistema de Consistência de Nomes**
- **Detecção Automática:** Identifica inconsistências entre nomes remotos e locais durante a sincronização
- **Correção Inteligente:** Atualiza automaticamente note types e configurações desatualizadas
- **Prevenção de Reversão:** Evita que operações posteriores desfaçam as correções aplicadas
- **Log Detalhado:** Registra todas as correções para transparência e debugging

#### **Interface de Resumo Otimizada**
- **Organização Melhorada:** Resumo geral aparece primeiro no modo "Completo"
- **Informações Hierárquicas:** Visão agregada seguida de detalhes individuais por deck
- **Performance Aprimorada:** Renderização mais rápida de grandes volumes de dados
- **Experiência do Usuário:** Layout mais intuitivo e informativo

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

#### **🔴 Cards não aparecem após sincronização**
**� Soluções:**
1. **Verifique a coluna SYNC?:** Deve estar `true`, `sim`, `1`
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
- [ ] Exatamente **19 colunas** na ordem correta
- [ ] Campo **ID** preenchido e único para cada linha
- [ ] Campo **ALUNOS** preenchido (ou deixar vazio para `[MISSING A.]`)
- [ ] Coluna **SYNC?** configurada (`true`/`false`)

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

---

🎉 **Pronto para começar?** Baixe o template, configure seus alunos e transforme suas planilhas em poderosos decks do Anki!