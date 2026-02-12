# 📚 Sheets2Anki

**The smartest way to create Anki cards. Collaborate in Sheets, sync to Anki.**

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Anki Version](https://img.shields.io/badge/Anki-25.x%2B-blue) ![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## 🚀 Why Sheets2Anki?

Creating flashcards manually is slow, lonely, and repetitive. **Sheets2Anki** transforms this workflow by letting you use the power of Google Sheets to manage your knowledge base.

**The Problem:**
*   😫 **Tedious:** Clicking through menus for every single card.
*   🔒 **Isolated:** Hard to share decks or work with classmates/colleagues.
*   📉 **Disorganized:** Difficult to see the "big picture" of your study material.

**The Solution:**
*   🚀 **Bulk Creation:** Write hundreds of cards as fast as you can type in a spreadsheet.
*   👥 **Collaboration:** Use Google Sheets to work together in real-time.
*   🧠 **AI-Powered:** Get instant explanations and help directly within your cards.

---

## ✨ Features that WOW

*   🤖 **AI Assistant Built-in:** Connect **Gemini**, **Claude**, or **OpenAI** to get explanations, context, and examples for your cards while you study.
*   ⏱️ **Focus Timer:** A beautiful, non-intrusive timer to keep your study sessions on track.
*   🔄 **Seamless Sync:** One-click synchronization from Sheets → Anki → AnkiWeb (Mobile/Tablet).
*   🏷️ **Smart Tagging:** Automatic hierarchical tags for Topic, Subtopic, Complexity, and Exam Board.
*   🧩 **Cloze Deletions:** Automatic detection of `{{c1::cloze}}` patterns.
*   📸 **Automatic Image Processing:** Insert images in Sheets, they're automatically hosted and embedded in your cards.
*   🎬 **Rich Media Support:** Embed HTML, Images, and Videos (YouTube/Vimeo) directly in your cards.
*   👩‍🎓 **Multi-Student Support:** Manage distinct decks for different students (or study groups) from a single sheet.

---

## 🛠️ Installation

1.  **Open Anki:** Go to `Tools` → `Add-ons` → `Get Add-ons...`
2.  **Enter Code:** Paste the Sheets2Anki code: *(Check AnkiWeb for the code)*
3.  **Restart Anki:** Restart to load the add-on.
4.  **Ready!** You will see a new `Sheets2Anki` menu under `Tools`.

---

## ⚡ Quick Start Guide

### 1. Get the Template
Don't start from scratch. Use our official template which has all the columns pre-configured.

[**➡️ Click here to get the Official Sheets2Anki Template**](https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing)

*(File → Make a copy)*

### 2. Connect to Anki
1.  In your Google Sheet, click `Share` -> `Anyone with the link can view` -> **Copy Link**.
2.  In Anki, press `Ctrl+Shift+A` (or `Tools` → `Sheets2Anki` → `Add New Remote Deck`).
3.  Paste your link and give your deck a name.

### 3. Sync & Study!
1.  Add your questions and answers to the sheet.
2.  In Anki, press `Ctrl+Shift+S` to sync.
3.  Your cards are now in Anki, organized and ready!

---

## 📊 Spreadsheet Structure

Your spreadsheet is the brain of your deck. The template comes with **23 columns**, but you only strictly need **3 in the header** plus a few filled in per row.

### 🔴 Required Columns (Must exist in the header)

| Column | Description | Example |
| :--- | :--- | :--- |
| **ID** | **Do not touch.** Unique identifier used to track card updates. | `Q101` |
| **QUESTION** | The front of your flashcard. | `Capital of France?` |
| **ANSWER** | The back of your flashcard. | `Paris` |

### 🟡 Control Columns (Recommended)

| Column | Description | Example |
| :--- | :--- | :--- |
| **STUDENTS** | Who is this card for? Comma-separated. | `John, Mary` |
| **SYNC** | Set to `TRUE` to sync this row. | `TRUE` |

### 🟢 Optional Columns (Use if needed)

| Column | Description | Example |
| :--- | :--- | :--- |
| **IMPORTANCE** | Priority level. | `High` |
| **TOPIC** | Organizing category. | `Geography` |
| **SUBTOPIC** | Organizing sub-category. | `Europe` |
| **CONCEPT** | Atomic concept (more refined than subtopic). | `Capital Cities` |
| **REVERSE** | Reverse question (creates an extra Answer → Question card). | `What city is the capital of France?` |
| **COMPLEMENTARY INFO** | Additional context. | `France is in Western Europe.` |
| **DETAILED INFO** | Extended explanation. | `Paris has been the capital since...` |
| **EXAMPLE 1** | First example. | `London is the capital of the UK.` |
| **EXAMPLE 2** | Second example. | `Berlin is the capital of Germany.` |
| **MNEMONIC** | Memory aids. | `My Very Educated Mother...` |
| **HTML IMAGE** | HTML code for images (or use Image Processor). | `<img src="...">` |
| **HTML VIDEO** | Embedded video (YouTube/Vimeo). | `<iframe src="...">` |
| **BOARDS** | Related exam boards. | `ENEM, FUVEST` |
| **LAST YEAR IN EXAM** | Last year this appeared in an exam. | `2024` |
| **CAREERS** | Related careers or areas. | `Medicine, Law` |
| **OTHER TAGS** | Additional tags for organization. | `review, hard` |
| **EXTRA FIELD 1/2/3** | Free-use fields for anything you want. | *(your content)* |

> 💡 **Tip:** You can hide any optional columns you don't use in Google Sheets to keep your workspace clean. The add-on will still read them correctly!

---

## 🤖 Configuring AI Help

Sheets2Anki brings the power of LLMs to your flashcards.

1.  Go to `Tools` → `Sheets2Anki` → `Configure AI Help`.
2.  Choose your provider: **Google Gemini**, **Anthropic Claude**, or **OpenAI**.
3.  Enter your API Key (safely stored locally).
4.  **Usage:** When reviewing a card, click the **🤖 AI Help** button to get more context about the question!

---

## 📸 Using Images in Your Cards

Sheets2Anki can automatically process images from Google Sheets and embed them in your flashcards!

### How It Works

1.  **Insert images** directly into cells in the **IMAGE** column (Insert > Image > Image in cell)
2.  **Configure once:** `Tools` → `Sheets2Anki` → `Configure Image Processor`
3.  **Automatic processing:** A Google Apps Script uploads images to ImgBB and writes HTML tags to the HTML IMAGE column.
4.  **Sync normally:** Your cards will include the images automatically!

### Setup (One-time)

1.  **Get ImgBB API Key** (Free):
    *   Visit [api.imgbb.com](https://api.imgbb.com/)
    *   Sign up (no credit card required)
    *   Copy your API key

2.  **Deploy the Google Apps Script** (once — works for all spreadsheets):
    *   In Anki, open `Tools` → `Sheets2Anki` → `Configure Image Processor`
    *   Click **📋 Copy Script to Clipboard**
    *   Go to [script.google.com](https://script.google.com) → **New project**
    *   Paste the script → **Save**
    *   Click **Deploy → New deployment**
    *   Configure: Type = Web app, Execute as = Me, Access = Anyone
    *   Click **Deploy** and authorize when prompted
    *   **Copy the Web App URL**

3.  **Configure in Anki**:
    *   `Tools` → `Sheets2Anki` → `Configure Image Processor`
    *   ☑ Enable automatic image processing
    *   Paste your **ImgBB API key**
    *   Paste your **Web App URL**
    *   Click "🧪 Test Configuration"
    *   Save!

> 📖 **Detailed Guide:** See [`scripts/IMAGE_PROCESSOR_README.md`](scripts/IMAGE_PROCESSOR_README.md) for complete documentation.

### Usage Tips

✅ **DO:** Insert images using "Insert > Image > Image in cell" in the **HTML IMAGE** column  
❌ **DON'T:** Use drag-and-drop or "Image over cells" (not detectable)

Images are hosted permanently on ImgBB (free) and will work on all devices including AnkiMobile!

---

## 📂 Advanced Organization

The add-on automatically creates a rich tag hierarchy for your cards in the Anki Browser:

```text
sheets2anki
├── topics::topic::subtopic::concept    (hierarchical content tree)
├── concepts::concept                   (flat concept search)
├── importance::level                   (priority level)
├── boards::board                       (exam boards)
├── years::year                         (exam years)
├── careers::career                     (professional areas)
└── other_tags::tag                     (additional tags)
```

Your **decks** are organized as:

```text
Sheets2Anki
└── Remote Deck
    └── Student
        └── Importance
            └── Topic
                └── Subtopic
                    └── Concept
```

---

## 🆘 Support & Troubleshooting

**Something went wrong?**

1.  **Check the logs:** `Tools` → `Add-ons` → `Sheets2Anki` → `View Files` → `debug_sheets2anki.log`.
2.  **Configure AnkiWeb Sync:** Press `Ctrl+Shift+W` to configure automatic AnkiWeb synchronization.
3.  **Backup & Reset:** Access `Tools` → `Sheets2Anki` → `Remote Decks Backup` to save your state, then try removing and re-adding the deck.

---

**Happy Studying! 🚀**
*Manage less, learn more.*
