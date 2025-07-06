# Sheets2Anki

**Sheets2Anki** is an Anki add-on that synchronizes your Anki decks with a published Google Sheets TSV. Your Google Sheets document serves as the source of truth: when you sync, cards are created, updated, or removed in your Anki deck to reflect the sheet's contents. This add-on is currently in **beta**, so features and behavior may still change.

## Features

- **Google Sheets as Source of Truth:**  
  Your published Google Sheet determines the cards present in Anki.  
- **Supports Both Basic and Cloze Cards:**  
  Automatically detects Cloze formatting (`{{c1::...}}`) in the question field for Cloze cards. Other questions become Basic cards.  
- **Automatic Tag Assignment:**  
  If you have a `tags` column in your sheet, those tags will be assigned to the cards in Anki.  
- **Deck Maintenance:**  
  - **Removed in Sheet → Removed in Anki:** If a card disappears from the sheet, it is removed from Anki on the next sync.
  - **Removed in Anki → Not Removed in Sheet:** There is **no reverse sync**. Deleting a card in Anki does not affect the sheet; the card may reappear if you sync again unless it's removed from the sheet.
  
**Important:** This add-on is in **beta** and currently supports only Basic and Cloze note types. Future updates may improve or extend functionality.

## No Reverse Sync & Deck Disconnection

- **No Reverse Sync:**  
  All changes flow from Google Sheets to Anki. If you delete or modify a card in Anki, it will not update the sheet. To permanently remove a card, remove it from the sheet before syncing again.
  
- **Syncing vs. Disconnecting a Remote Deck:**
  - **Sync Once and Disconnect:**  
    You can sync a deck once, and then if you prefer to manage cards locally without further remote updates, go to `Tools > Manage Remote Deck > Disconnect Remote Deck`. This "unlinks" Anki from the sheet. The local deck remains and can be edited freely in Anki as a normal deck.
  - **Continuous Syncing:**  
    Alternatively, you can keep the deck connected and continue updating your Google Sheets document. Upon each sync, Anki updates to match the sheet. If you want a card gone, you must remove it from the sheet, as deletions in Anki alone won't persist after a resync.

## Example Google Sheets Document

Use this [example Google Sheets document](https://docs.google.com/spreadsheets/d/1S97fZkuw1DctJhBB1yaiWiSh5grmNmY9Gp8KVPCpMfU/edit?usp=sharing) as a starting template.  
![imagen](https://github.com/user-attachments/assets/a030ddd0-5dae-483b-bde2-32f20ed0e245)
- Required columns:
  - Question field: either `question` or `front` column
  - Answer field: either `answer` or `back` column
  - Optional: `tags` column for card tagging
- Add Cloze-formatted questions (e.g., `{{c1::essential}}`) for Cloze cards.
- After finalizing, publish the sheet as a TSV (File > Publish to the Web) and copy the TSV URL.


## Installation

1. **Download the `.ankiaddon` File:**
   - Go to the [Releases](https://github.com/your-username/sheets2anki/releases) page of this repository.
   - Download the latest `.ankiaddon`.

2. **Install in Anki:**
   - In Anki, go to `Tools > Add-ons > Install from file...`.
   - Select the downloaded `.ankiaddon` file.
   - Restart Anki when prompted.

## Usage

1. **Add a New Remote Deck:**
   - `Tools > Manage Remote Deck > Add New Remote Deck`.
   - Paste the published TSV URL from your Google Sheet.
   - Enter a deck name and confirm.

2. **Sync Decks:**
   - `Tools > Manage Remote Deck > Sync Remote Decks` to update Anki from the sheet.

3. **Disconnect a Remote Deck:**
   - `Tools > Manage Remote Deck > Remove Remote Deck`.
   - This unlinks the remote sheet. The local deck remains, allowing you to manage it entirely in Anki going forward.

## Requirements

- **Anki Version:** Compatible with Anki 2.1.x.
- **Note Models Needed:**
  - **Basic:** Fields `Front` and `Back`.
  - **Cloze:** Fields `Text` and `Extra`.

Confirm these models exist before syncing.

## Troubleshooting

- **No Cards Imported?**  
  Check TSV headers (either `question`/`front` for questions and `answer`/`back` for answers, plus optional `tags`) and ensure required note models exist.
- **Changes Not Updating?**  
  Wait a few minutes after editing the sheet or verify the correct published TSV URL.
- **Cloze Cards Not Forming?**  
  Ensure Cloze syntax (`{{c1::...}}`) is correct and the Cloze model has `Text` and `Extra` fields, see Example Google Sheets Document above. 
- **Cards Reappearing After Deletion in Anki?**  
  Remember there's no reverse sync. Remove the card from the sheet if you want it gone permanently.

## Beta Status and Future Plans

Sheets2Anki is in beta. Basic and Cloze types are supported now, but more features and improvements may follow as the project evolves. Keep an eye on this repository for updates.