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
2.  In Anki, press `Ctrl+Shift+A` (or `Tools` → `Sheets2Anki` → `Add Remote Deck`).
3.  Paste your link and give your deck a name.

### 3. Sync & Study!
1.  Add your questions and answers to the sheet.
2.  In Anki, press `Ctrl+Shift+S` to sync.
3.  Your cards are now in Anki, organized and ready!

---

## 📊 Spreadsheet Structure

Your spreadsheet is the brain of your deck. The template comes with 23 columns, but you only strictly need to fill in **5 of them**.

### 🔴 Mandatory Columns (Must be filled)

| Column | Description | Example |
| :--- | :--- | :--- |
| **ID** | **Do not touch.** Unique identifier used to track card updates. | `Q101` |
| **STUDENTS** | Who is this card for? | `John, Mary` |
| **SYNC** | Control switch. Set to `TRUE` to sync this row. | `TRUE` |
| **QUESTION** | The front of your flashcard. | `Capital of France?` |
| **ANSWER** | The back of your flashcard. | `Paris` |

### 🟢 Optional Columns (Use if needed)

| Column | Description | Example |
| :--- | :--- | :--- |
| **TOPIC** | Organizing category. | `Geography` |
| **SUBTOPIC** | Organizing sub-category. | `Europe` |
| **IMPORTANCE** | Priority level (High/Medium/Low). | `High` |
| **MEDIA** | Embed images or videos. | `<img src="...">` |
| **MNEMONIC** | Memory aids. | `My Very Educated Mother...` |

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

1.  **Insert images** directly into cells in Google Sheets (Insert > Image > Image in cell)
2.  **Configure once:** `Tools` → `Sheets2Anki` → `📸 Configure Image Processor`
3.  **Automatic processing:** Images are uploaded to free hosting and replaced with HTML tags
4.  **Sync normally:** Your cards will include the images automatically!

### Setup (One-time)

1.  **Get ImgBB API Key** (Free):
    *   Visit [api.imgbb.com](https://api.imgbb.com/)
    *   Sign up (no credit card required)
    *   Copy your API key

2.  **Get Google Sheets Credentials**:
    *   Go to [Google Cloud Console](https://console.cloud.google.com/)
    *   Create a project and enable "Google Sheets API"
    *   Create OAuth 2.0 credentials (Desktop App)
    *   Download `credentials.json`

3.  **Configure in Anki**:
    *   `Tools` → `Sheets2Anki` → `📸 Configure Image Processor`
    *   ☑ Enable automatic image processing
    *   Paste ImgBB API key
    *   Select `credentials.json` file
    *   Click "🧪 Test Configuration"
    *   Save!

> 📖 **Detailed Guide:** See [`scripts/IMAGE_PROCESSOR_README.md`](scripts/IMAGE_PROCESSOR_README.md) for complete documentation.

### Usage Tips

✅ **DO:** Insert images using "Insert > Image > Image in cell"  
❌ **DON'T:** Use drag-and-drop or "Image over cells" (not detectable)

Images are hosted permanently on ImgBB (free) and will work on all devices including AnkiMobile!

---

## 📂 Advanced Organization

The add-on automatically creates a beautiful hierarchy for your cards in the Anki Browser:

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
2.  **Test Connection:** Press `Ctrl+Shift+W` to test your connection to AnkiWeb.
3.  **Reset:** Access `Tools` → `Sheets2Anki` → `Backup` to save your state, then try removing and re-adding the deck.

---

**Happy Studying! 🚀**
*Manage less, learn more.*
