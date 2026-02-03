# Sheets2Anki: Google Sheets to Anki + AI Integration

**Create flashcards in Google Sheets and sync them to Anki. Now with AI support!**

Stop wasting time creating cards one by one. Use the power of spreadsheets to manage your study material.

## 🚀 Key Features

*   **Bulk Creation:** Write hundreds of cards as fast as you can type.
*   **🤖 AI Integration:** Use **Gemini**, **Claude**, or **OpenAI** to get explanations directly in your cards.
*   **Collaboration:** Work with friends or students on the same spreadsheet.
*   **Smart Sync:** Cards are automatically organized into subdecks (Topic > Subtopic).
*   **Rich Media:** Supports HTML, Images, and Videos (YouTube/Vimeo).
*   **Cloze Support:** Automatically detects `{{c1::cloze}}` cards.

## ⚡ Quick Start

1.  **Get the Template:** [Click here to copy the Official Google Sheet Template](https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing).
2.  **Connect:** 
    *   In Sheets: `Share` -> `Anyone with the link can view` -> Copy Link.
    *   In Anki: `Tools` -> `Sheets2Anki` -> `Add Remote Deck` -> Paste Link.
3.  **Sync:** Press `Ctrl+Shift+S` to bring your cards into Anki.

## 📋 How it Works

Simply fill in the columns in the spreadsheet:
| Column | Purpose | Example |
| :--- | :--- | :--- |
| **ID** | **Required.** Unique identifier for updates. | `Q101` |
| **STUDENTS** | **Required.** List os students who wants to learn the information. | `Igor, Isabelle, Jack` |
| **SYNC** | **Required.** Set to `TRUE` (or `VERDADEIRO`) to sync this row. | `TRUE` |
| **QUESTION** | **Required.** The front of your flashcard. | `Capital of France?` |
| **ANSWER** | **Required.** The back of your flashcard. | `Paris` |

The add-on handles the rest, creating beautiful, organized notes in your collection.

---
*Support the project on GitHub: [igorrflorentino/sheets2anki](https://github.com/igorrflorentino/sheets2anki)*
