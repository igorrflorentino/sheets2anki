# 📸 Sheets2Anki Image Processor

Automatically processes embedded images in your Google Sheets spreadsheet:

- Detects images in the "HTML IMAGE" column of the "Notes" sheet
- Uploads them to ImgBB (free image hosting)
- Writes HTML `<img>` tags into the same cell
- Smart detection: skips already-processed images, reprocesses changed ones
- **Never deletes** your original images from the spreadsheet

## Quick Setup (One Time)

### 1. Get an ImgBB API Key

1. Go to [https://api.imgbb.com](https://api.imgbb.com)
2. Create a free account
3. Copy your API key

### 2. Deploy the Google Apps Script

You only need to do this **once** — the same script works with **all** your spreadsheets.

1. In Anki, open **Sheets2Anki → Configure Image Processor**
2. Click **📋 Copy Script to Clipboard**
3. Go to [https://script.google.com](https://script.google.com)
4. Click **New project**
5. Delete any existing code in the editor and **paste** (Ctrl+V)
6. Rename the project to "Sheets2Anki Image Processor" (optional)
7. Click **Save** (💾 icon or Ctrl+S)
8. Click **Deploy → New deployment**
9. Configure:
   - **Type**: Web app
   - **Execute as**: Me
   - **Who has access**: Anyone
10. Click **Deploy**
11. Authorize the script when prompted (it needs access to your spreadsheets)
12. **Copy the Web App URL** (it looks like `https://script.google.com/macros/s/.../exec`)

### 3. Configure in Anki

1. Back in the Image Processor configuration dialog
2. Paste your **ImgBB API key**
3. Paste your **Web App URL**
4. Enable **automatic image processing**
5. Click **Test Configuration** to verify
6. Click **Save Configuration**

That's it! The addon will automatically process images on every sync for any spreadsheet.

## How It Works

During each sync, the addon:

1. Extracts the spreadsheet ID from the deck URL
2. Sends a POST to your deployed script with the ID + ImgBB key
3. The script opens the spreadsheet, finds the "HTML IMAGE" column
4. Uploads new images to ImgBB and writes HTML tags
5. Returns a summary to the addon

## Important Notes

- **One deployment for all spreadsheets** — no need to install per sheet
- **Only the "HTML IMAGE" column** is scanned — floating images and other columns are ignored
- **Images are never deleted** from your spreadsheet — only HTML tags are added
- **Already-processed images are skipped** — no duplicate uploads
- **Changed images are reprocessed** — if you replace an image, it gets re-uploaded
- The Web App URL should be kept private
- If you update the script, go to Deploy → Manage deployments → Edit → select "New version" → Deploy

## Troubleshooting

| Issue | Solution |
| ----- | -------- |
| "Web App URL not configured" | Paste the URL in Sheets2Anki → Configure Image Processor |
| "Cannot open spreadsheet" | Make sure you have access to the spreadsheet |
| "Failed to connect to Web App" | Check your internet connection and verify the URL |
| Script timeout | Google Apps Script has a 6-minute execution limit; process fewer images at once |
| Images not detected | Ensure images are in cells of the "HTML IMAGE" column (Insert → Image → Image in cell) |
| "Missing imgbb_api_key" | Enter your ImgBB API key in the addon configuration |
