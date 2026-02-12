# 🚀 Quick Start - Image Processor

## TL;DR

```bash
# 1. Install dependencies
cd scripts
./setup_image_processor.sh

# 2. Get Google credentials (see IMAGE_PROCESSOR_README.md)
# Save as: scripts/credentials.json

# 3. Get ImgBB API key from https://api.imgbb.com/

# 4. Run the script
python3 process_sheet_images.py
```

## What you need

1. **Google Sheets credentials** (`credentials.json`)
   - Get from: https://console.cloud.google.com/
   - Enable: Google Sheets API
   - Create: OAuth 2.0 Desktop App credentials

2. **ImgBB API key** (free)
   - Get from: https://api.imgbb.com/

## How to use

1. Insert images in Google Sheets using **Insert > Image > Image in cell**
2. Run `python3 process_sheet_images.py`
3. Follow the prompts
4. Sync normally in Anki

**Full documentation**: See `IMAGE_PROCESSOR_README.md`
