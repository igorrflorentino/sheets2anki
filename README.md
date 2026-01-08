# 📚 Sheets2Anki

**Create and manage your Anki flashcards directly from Google Sheets.**

## 🎯 The Problem

Creating flashcards in Anki is labor-intensive. You need to open the app, navigate through menus, fill in fields one by one. For those who work with many cards — teachers, students studying for exams, content creators — this consumes time and makes collaboration difficult.

## ✨ The Solution

**Sheets2Anki** uses your Google Sheet as the source for cards. You edit the spreadsheet (alone or as a team), click sync, and that's it — your cards appear organized in Anki.

```
Google Sheets  →  Anki  →  AnkiWeb
   (edit)       (receives) (syncs to other devices)
```

## 🌟 What you can do

- **Create cards in bulk** — One row in the spreadsheet = one card in Anki
- **Collaborate** — Multiple people can edit the same spreadsheet
- **Organize by students** — Each student has their own subdecks
- **Automatic hierarchy** — Cards organized by topic, subtopic and concept
- **Automatic tags** — Classification by exam boards, years, careers and importance
- **Cloze cards** — Support for `{{c1::text}}` detected automatically
- **AnkiWeb sync** — Your cards reach all your devices

---

## 📦 Installation

1. In Anki: `Tools → Add-ons → Get Add-ons...`
2. Paste the code: *(available on AnkiWeb)*
3. Restart Anki
4. Access via `Tools → Sheets2Anki`

---

## 📋 Setting Up Your Spreadsheet

Use our [**ready-made template**](https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing) as a base.

### Column Structure (23 required)

| Column | What to put | Example |
|--------|-------------|---------|
| **ID** | Unique card identifier | `Q001` |
| **ALUNOS** | Who receives this card | `John, Mary` |
| **SYNC** | Synchronize? | `yes` or `no` |
| **IMPORTANCIA** | Priority | `High`, `Medium`, `Low` |
| **TOPICO** | Main theme | `Geography` |
| **SUBTOPICO** | Secondary theme | `Capitals` |
| **CONCEITO** | Specific concept | `Brazil` |
| **PERGUNTA** | Front of the card | `What is the capital of Brazil?` |
| **LEVAR PARA PROVA** | Back of the card (answer) | `Brasília` |
| **INFO COMPLEMENTAR** | Extra details | `Founded in 1960` |
| **INFO DETALHADA** | More details | `Designed by Oscar Niemeyer` |
| **EXEMPLO 1** | First example | - |
| **EXEMPLO 2** | Second example | - |
| **EXEMPLO 3** | Third example | - |
| **IMAGEM HTML** | Images/HTML | `<img src="...">` |
| **VIDEO HTML** | Embedded videos | `<iframe src="...">` |
| **CAMPO EXTRA 1** | Free field (personal use) | - |
| **CAMPO EXTRA 2** | Free field (personal use) | - |
| **CAMPO EXTRA 3** | Free field (personal use) | - |
| **BANCAS** | Exam boards | `CESPE, FCC` |
| **ULTIMO ANO EM PROVA** | Question year | `2024` |
| **CARREIRAS** | Application area | `Tax` |
| **TAGS ADICIONAIS** | Extra tags | `fundamental` |

### Important Tips

**ALUNOS:** List separated by commas. If left empty, the card goes to `[MISSING STUDENT]`.

**SYNC:** Must be explicitly filled. Accepts `true`, `yes`, `1` to synchronize. Empty cells or other values **do not sync**.

**Cloze Cards:** Write in PERGUNTA using the pattern `{{c1::answer}}`:
```
The capital of Brazil is {{c1::Brasília}} and it's in the {{c2::Center-West}}.
```

---

## ⚙️ Using the Addon

### Step 1: Configure Students

Before syncing, define which students you want to import:

1. Press `Ctrl+Shift+G` (or `Tools → Sheets2Anki → Configure Students`)
2. Check the students you want to sync
3. Confirm

> 💡 Only cards from checked students will be synchronized.

### Step 2: Connect Your Spreadsheet

1. Open your spreadsheet in Google Sheets
2. Click `Share` → `Anyone with the link can view`
3. Copy the link
4. In Anki, press `Ctrl+Shift+A` (or `Tools → Sheets2Anki → Add Remote Deck`)
5. Paste the link and confirm

### Step 3: Synchronize

- Press `Ctrl+Shift+S` to synchronize
- The addon fetches data from the spreadsheet and updates your cards
- If configured, automatically syncs with AnkiWeb

---

## ⌨️ Shortcuts

| Action | Shortcut |
|--------|----------|
| Synchronize | `Ctrl+Shift+S` |
| Add deck | `Ctrl+Shift+A` |
| Configure students | `Ctrl+Shift+G` |
| Configure AnkiWeb | `Ctrl+Shift+W` |
| Disconnect deck | `Ctrl+Shift+D` |

---

## 📂 How Cards are Organized

After syncing, your cards are organized like this:

```
Sheets2Anki::
└── DeckName::
    ├── John::
    │   └── High::Geography::Capitals::Brazil
    ├── Mary::
    │   └── Medium::History::Discoveries::Portugal
    └── [MISSING STUDENT]::
        └── (cards without defined student)
```

Tags are automatically applied by topic, exam board, year and importance. See details in [Advanced Topics](#hierarchical-tag-system).

---

## 💾 Backup

Access via `Tools → Sheets2Anki → Backup Remote Decks`:

- **Create backup:** Saves settings, decks and students in a .zip file
- **Restore backup:** Recovers settings from a previous backup

---

## ❓ Frequently Asked Questions

**Is my study progress lost when syncing?**
> No. Intervals, ease and statistics are preserved. Only the content is updated.

**Can I use on multiple devices?**
> Yes. Configure AnkiWeb (`Ctrl+Shift+W`) and your cards sync automatically.

**How do I make cloze cards?**
> Use `{{c1::answer}}` in the PERGUNTA column. See example in [Important Tips](#important-tips).

**Cards don't appear after syncing?**
> Check: (1) SYNC column is `yes`, (2) students are checked in `Ctrl+Shift+G`, (3) ID is unique.

**How to disconnect a spreadsheet?**
> Use `Ctrl+Shift+D` and select the deck to disconnect.

---

## 🔧 Problems?

1. Check the log file: `Tools → Add-ons → [Sheets2Anki] → View files → debug_sheets2anki.log`
2. Test AnkiWeb connection: `Ctrl+Shift+W → Test Connection`
3. To reset: backup, disconnect the deck (`Ctrl+Shift+D`), reconnect (`Ctrl+Shift+A`)

---

## 🔧 Advanced Topics

This section contains technical details for advanced users.

### Hierarchical Tag System

The addon automatically applies tags in 6 categories:

| Category | Format | Example |
|----------|--------|---------|
| Topics | `Sheets2Anki::Topics::topic::subtopic::concept` | `Sheets2Anki::Topics::geography::capitals::brazil` |
| Exam Boards | `Sheets2Anki::ExamBoards::board` | `Sheets2Anki::ExamBoards::cespe` |
| Years | `Sheets2Anki::Years::year` | `Sheets2Anki::Years::2024` |
| Careers | `Sheets2Anki::Careers::career` | `Sheets2Anki::Careers::tax` |
| Importance | `Sheets2Anki::Importance::level` | `Sheets2Anki::Importance::high` |
| Students | `Sheets2Anki::Students::student` | `Sheets2Anki::Students::john` |

### Custom Note Types

The addon creates unique note types for each combination of deck, student and card type:

- **Basic cards:** `Sheets2Anki - DeckName - Student - Basic`
- **Cloze cards:** `Sheets2Anki - DeckName - Student - Cloze`

This allows each student to have personalized formatting and fields without affecting others.

### Name Consistency System

During synchronization, the addon automatically checks and corrects:

- Inconsistencies between note type names in Anki and in the configuration
- Differences between remote names (spreadsheet) and local names (Anki)
- Updates outdated configurations without data loss

### IMAGEM HTML and VIDEO HTML Columns

Allow adding multimedia content to the back of cards:

**IMAGEM HTML** - For images and illustrations:
```html
<img src="https://example.com/image.png" style="max-width:300px;">
<a href="https://link.com">External link</a>
<div style="color:red;">Highlighted text</div>
```

**VIDEO HTML** - For embedded videos (YouTube, Vimeo, etc.):
```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/VIDEO_ID" frameborder="0" allowfullscreen></iframe>
```

Both appear after the main answer on the back of the card.

### Accepted Formats in the ALUNOS Field

The addon recognizes multiple separators:

- Comma: `John, Mary, Peter`
- Semicolon: `John; Mary; Peter`
- Pipe: `John|Mary|Peter`

### Automatic Safety Backup

When restoring a backup, the addon automatically creates a safety backup of the current state before overwriting. This prevents data loss in case the restoration is not what was desired.

### System Requirements

- **Anki:** Version 25.x or newer
- **Python:** 3.13+ (included with Anki 25.x)
- **Qt:** Qt6 (included with Anki 25.x)

### AnkiWeb Compatibility

- ✅ Anki 25.x+ (Qt6, modern sync)
- ✅ AnkiMobile, AnkiDroid, AnkiWeb

### Log File

The addon logs all operations in `debug_sheets2anki.log`:

```
Tools → Add-ons → [Sheets2Anki] → View files
```

Useful for diagnosing synchronization problems.

---

🎉 **Done!** Edit your spreadsheet, sync, and your cards will be in Anki.