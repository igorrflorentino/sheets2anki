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

### Column Structure 

| Column | What to put | Example |
|--------|-------------|---------|
| **ID** | Unique card identifier | `Q001` |
| **STUDENTS** | Who receives this card | `John, Mary` |
| **SYNC** | Synchronize? | `yes` or `no` |
| **IMPORTANCE** | Priority | `High`, `Medium`, `Low` |
| **TOPIC** | Main theme | `Geography` |
| **SUBTOPIC** | Secondary theme | `Capitals` |
| **CONCEPT** | Specific concept | `Brazil` |
| **QUESTION** | Front of the card | `What is the capital of Brazil?` |
| **ANSWER** | Back of the card (answer) | `Brasília` |
| **COMPLEMENTARY INFO** | Extra details | `Founded in 1960` |
| **DETAILED INFO** | More details | `Designed by Oscar Niemeyer` |
| **EXAMPLE 1** | First example | - |
| **EXAMPLE 2** | Second example | - |
| **MNEMONIC** | Mnemonic for memory aid | - |
| **HTML IMAGE** | Images/HTML | `<img src="...">` |
| **HTML VIDEO** | Embedded videos | `<iframe src="...">` |
| **EXTRA FIELD 1** | Free field (personal use) | - |
| **EXTRA FIELD 2** | Free field (personal use) | - |
| **EXTRA FIELD 3** | Free field (personal use) | - |
| **BOARDS** | Exam boards | `CESPE, FCC` |
| **LAST YEAR IN EXAM** | Question year | `2024` |
| **CAREERS** | Application area | `Tax` |
| **OTHER TAGS** | Extra tags | `fundamental` |

### Important Tips

**Requirements:** The spreadsheet must have the 23 columns listed above, but only the following columns must be filled:
- ID - unique card identifier (auto-generated in the [**template**](https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing))
- STUDENTS - who receives this card (list separated by commas. If left empty, the card goes to `[MISSING STUDENT]`)
- SYNC - synchronize? (true, yes, 1 to sync, empty or other values do not sync)
- QUESTION - front of the card
- ANSWER - back of the card

**Cloze Cards:** Write in QUESTION using the pattern `{{c1::answer}}`:
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

### HTML IMAGE and HTML VIDEO Columns

Allow adding multimedia content to the back of cards:

**HTML IMAGE** - For images and illustrations:
```html
<img src="https://example.com/image.png" style="max-width:300px;">
<a href="https://link.com">External link</a>
<div style="color:red;">Highlighted text</div>
```

**HTML VIDEO** - For embedded videos (YouTube, Vimeo, etc.):
```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/VIDEO_ID" frameborder="0" allowfullscreen></iframe>
```

Both appear after the main answer on the back of the card.

### Accepted Formats in the STUDENTS Field

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