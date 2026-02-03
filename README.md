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

Your spreadsheet is the brain of your deck. Here are the key columns:

| Column | Purpose | Example |
| :--- | :--- | :--- |
| **ID** | **Required.** Unique identifier for updates. | `Q101` |
| **STUDENTS** | **Required.** List os students who wants to learn the information. | `Igor, Isabelle, Jack` |
| **SYNC** | **Required.** Set to `TRUE` (or `VERDADEIRO`) to sync this row. | `TRUE` |
| **QUESTION** | **Required.** The front of your flashcard. | `Capital of France?` |
| **ANSWER** | **Required.** The back of your flashcard. | `Paris` |

> **💡 Pro Tip:** You can hide columns you don't use in Google Sheets to keep your view clean. The add-on will still read them!

---

## 🤖 Configuring AI Help

Sheets2Anki brings the power of LLMs to your flashcards.

1.  Go to `Tools` → `Sheets2Anki` → `Configure AI Help`.
2.  Choose your provider: **Google Gemini**, **Anthropic Claude**, or **OpenAI**.
3.  Enter your API Key (safely stored locally).
4.  **Usage:** When reviewing a card, click the **🤖 AI Help** button to get more context about the question!

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