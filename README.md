# 📚 Sheets2Anki

**Crie e gerencie seus flashcards do Anki diretamente no Google Sheets.**

## 🎯 O Problema

Criar flashcards no Anki é trabalhoso. Você precisa abrir o app, navegar pelos menus, preencher campos um por um. Para quem trabalha com muitos cards — professores, estudantes de concursos, criadores de conteúdo — isso consome tempo e dificulta a colaboração.

## ✨ A Solução

O **Sheets2Anki** usa sua planilha do Google Sheets como fonte dos cards. Você edita a planilha (sozinho ou em equipe), clica em sincronizar, e pronto — seus cards aparecem organizados no Anki.

```
Google Sheets  →  Anki  →  AnkiWeb
   (edita)      (recebe)  (sincroniza para outros dispositivos)
```

## 🌟 O que você pode fazer

- **Criar cards em massa** — Uma linha na planilha = um card no Anki
- **Colaborar** — Múltiplas pessoas podem editar a mesma planilha
- **Organizar por alunos** — Cada aluno tem seus próprios subdecks
- **Hierarquia automática** — Cards organizados por tópico, subtópico e conceito
- **Tags automáticas** — Classificação por bancas, anos, carreiras e importância
- **Cards Cloze** — Suporte a `{{c1::texto}}` detectado automaticamente
- **Sincronização AnkiWeb** — Seus cards chegam a todos os seus dispositivos

---

## � Instalação

1. No Anki: `Ferramentas → Complementos → Obter Complementos...`
2. Cole o código: *(disponível no AnkiWeb)*
3. Reinicie o Anki
4. Acesse via `Ferramentas → Sheets2Anki`

---

## 📋 Configurando sua Planilha

Use nosso [**modelo pronto**](https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing) como base.

### Estrutura das Colunas (23 obrigatórias)

| Coluna | O que colocar | Exemplo |
|--------|---------------|---------|
| **ID** | Identificador único do card | `Q001` |
| **ALUNOS** | Quem recebe este card | `João, Maria` |
| **SYNC** | Sincronizar? | `sim` ou `não` |
| **IMPORTANCIA** | Prioridade | `Alta`, `Média`, `Baixa` |
| **TOPICO** | Tema principal | `Geografia` |
| **SUBTOPICO** | Tema secundário | `Capitais` |
| **CONCEITO** | Conceito específico | `Brasil` |
| **PERGUNTA** | Frente do card | `Qual é a capital do Brasil?` |
| **LEVAR PARA PROVA** | Verso do card (resposta) | `Brasília` |
| **INFO COMPLEMENTAR** | Detalhes extras | `Fundada em 1960` |
| **INFO DETALHADA** | Mais detalhes | `Projetada por Oscar Niemeyer` |
| **EXEMPLO 1** | Primeiro exemplo | - |
| **EXEMPLO 2** | Segundo exemplo | - |
| **EXEMPLO 3** | Terceiro exemplo | - |
| **IMAGEM HTML** | Imagens/HTML | `<img src="...">` |
| **VÍDEO HTML** | Vídeos embedded | `<iframe src="...">` |
| **EXTRA 1** | Campo livre (uso pessoal) | - |
| **EXTRA 2** | Campo livre (uso pessoal) | - |
| **EXTRA 3** | Campo livre (uso pessoal) | - |
| **BANCAS** | Bancas de concurso | `CESPE, FCC` |
| **ULTIMO ANO EM PROVA** | Ano da questão | `2024` |
| **CARREIRAS** | Área de aplicação | `Fiscal` |
| **TAGS ADICIONAIS** | Tags extras | `fundamental` |

### Dicas Importantes

**Alunos:** Liste separados por vírgula. Se deixar vazio, o card vai para `[MISSING A.]`.

**SYNC:** Deve ser explicitamente preenchido. Aceita `true`, `sim`, `1` para sincronizar. Células vazias ou com outros valores **não sincronizam**.

**Cards Cloze:** Escreva na PERGUNTA usando o padrão `{{c1::resposta}}`:
```
A capital do Brasil é {{c1::Brasília}} e fica no {{c2::Centro-Oeste}}.
```

---

## ⚙️ Usando o Addon

### Passo 1: Configure os Alunos

Antes de sincronizar, defina quais alunos você quer importar:

1. Pressione `Ctrl+Shift+G` (ou `Ferramentas → Sheets2Anki → Configurar Alunos`)
2. Marque os alunos que deseja sincronizar
3. Confirme

> 💡 Apenas cards dos alunos marcados serão sincronizados.

### Passo 2: Conecte sua Planilha

1. Abra sua planilha no Google Sheets
2. Clique em `Compartilhar` → `Qualquer pessoa com o link pode ver`
3. Copie o link
4. No Anki, pressione `Ctrl+Shift+A` (ou `Ferramentas → Sheets2Anki → Adicionar Deck Remoto`)
5. Cole o link e confirme

### Passo 3: Sincronize

- Pressione `Ctrl+Shift+S` para sincronizar
- O addon busca os dados da planilha e atualiza seus cards
- Se configurado, sincroniza automaticamente com o AnkiWeb

---

## ⌨️ Atalhos

| Ação | Atalho |
|------|--------|
| Sincronizar | `Ctrl+Shift+S` |
| Adicionar deck | `Ctrl+Shift+A` |
| Configurar alunos | `Ctrl+Shift+G` |
| Configurar AnkiWeb | `Ctrl+Shift+W` |
| Desconectar deck | `Ctrl+Shift+D` |

---

## 📂 Como os Cards são Organizados

Após sincronizar, seus cards ficam organizados assim:

```
Sheets2Anki::
└── NomeDoDeck::
    ├── João::
    │   └── Alta::Geografia::Capitais::Brasil
    ├── Maria::
    │   └── Média::História::Descobrimentos::Portugal
    └── [MISSING A.]::
        └── (cards sem aluno definido)
```

Tags são aplicadas automaticamente por tópico, banca, ano e importância. Veja detalhes em [Tópicos Avançados](#sistema-de-tags-hierárquico).

---

## � Backup

Acesse via `Ferramentas → Sheets2Anki → Backup de Decks Remotos`:

- **Criar backup:** Salva configurações, decks e alunos em arquivo .zip
- **Restaurar backup:** Recupera configurações de um backup anterior

---

## ❓ Perguntas Frequentes

**Meu progresso de estudo é perdido ao sincronizar?**
> Não. Intervalos, facilidade e estatísticas são preservados. Apenas o conteúdo é atualizado.

**Posso usar em vários dispositivos?**
> Sim. Configure o AnkiWeb (`Ctrl+Shift+W`) e seus cards sincronizam automaticamente.

**Como faço cards cloze?**
> Use `{{c1::resposta}}` na coluna PERGUNTA. Veja exemplo em [Dicas Importantes](#dicas-importantes).

**Cards não aparecem após sincronizar?**
> Verifique: (1) coluna SYNC está `sim`, (2) alunos estão marcados em `Ctrl+Shift+G`, (3) ID é único.

**Como desconectar uma planilha?**
> Use `Ctrl+Shift+D` e selecione o deck para desconectar.

---

## � Problemas?

1. Verifique o arquivo de log: `Ferramentas → Complementos → [Sheets2Anki] → Ver arquivos → debug_sheets2anki.log`
2. Teste a conexão AnkiWeb: `Ctrl+Shift+W → Testar Conexão`
3. Para resetar: faça backup, desconecte o deck (`Ctrl+Shift+D`), reconecte (`Ctrl+Shift+A`)

---

## 🔧 Tópicos Avançados

Esta seção contém detalhes técnicos para usuários avançados.

### Sistema de Tags Hierárquico

O addon aplica tags automaticamente em 6 categorias:

| Categoria | Formato | Exemplo |
|-----------|---------|---------|
| Tópicos | `Sheets2Anki::Topicos::topico::subtopico::conceito` | `Sheets2Anki::Topicos::geografia::capitais::brasil` |
| Bancas | `Sheets2Anki::Bancas::banca` | `Sheets2Anki::Bancas::cespe` |
| Anos | `Sheets2Anki::Anos::ano` | `Sheets2Anki::Anos::2024` |
| Carreiras | `Sheets2Anki::Carreiras::carreira` | `Sheets2Anki::Carreiras::fiscal` |
| Importância | `Sheets2Anki::Importancia::nivel` | `Sheets2Anki::Importancia::alta` |
| Alunos | `Sheets2Anki::Alunos::aluno` | `Sheets2Anki::Alunos::joao` |

### Note Types Personalizados

O addon cria note types únicos para cada combinação de deck, aluno e tipo de card:

- **Cards básicos:** `Sheets2Anki - NomeDeck - Aluno - Basic`
- **Cards cloze:** `Sheets2Anki - NomeDeck - Aluno - Cloze`

Isso permite que cada aluno tenha formatação e campos personalizados sem afetar outros.

### Sistema de Consistência de Nomes

Durante a sincronização, o addon verifica e corrige automaticamente:

- Inconsistências entre nomes de note types no Anki e na configuração
- Diferenças entre nomes remotos (planilha) e locais (Anki)
- Atualiza configurações desatualizadas sem perda de dados

### Colunas IMAGEM HTML e VÍDEO HTML

Permitem adicionar conteúdo multimídia no verso dos cards:

**IMAGEM HTML** - Para imagens e ilustrações:
```html
<img src="https://exemplo.com/imagem.png" style="max-width:300px;">
<a href="https://link.com">Link externo</a>
<div style="color:red;">Texto destacado</div>
```

**VÍDEO HTML** - Para vídeos embedded (YouTube, Vimeo, etc.):
```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/VIDEO_ID" frameborder="0" allowfullscreen></iframe>
```

Ambos aparecem após a resposta principal no verso do card.

### Formatos Aceitos no Campo ALUNOS

O addon reconhece múltiplos separadores:

- Vírgula: `João, Maria, Pedro`
- Ponto e vírgula: `João; Maria; Pedro`
- Pipe: `João|Maria|Pedro`

### Backup Automático de Segurança

Ao restaurar um backup, o addon cria automaticamente um backup de segurança do estado atual antes de sobrescrever. Isso previne perda de dados caso a restauração não seja o desejado.

### Compatibilidade AnkiWeb

- ✅ Anki 2.1.50+ (método moderno de sincronização)
- ✅ Versões anteriores (métodos de compatibilidade)
- ✅ AnkiMobile, AnkiDroid, AnkiWeb

### Arquivo de Log

O addon registra todas as operações em `debug_sheets2anki.log`:

```
Ferramentas → Complementos → [Sheets2Anki] → Ver arquivos
```

Útil para diagnosticar problemas de sincronização.

---

🎉 **Pronto!** Edite sua planilha, sincronize, e seus cards estarão no Anki.