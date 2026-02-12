"""
Image Processor Module for Sheets2Anki

Simplified module that triggers a Google Apps Script Web App
to process embedded images in Google Sheets:
- Sends HTTP POST to the deployed script URL
- The script handles image detection, ImgBB upload, and HTML writing
- Returns results to the addon

Author: Sheets2Anki Team
License: MIT
"""

from typing import Tuple

from .utils import add_debug_message


def add_debug_msg(message, category="IMAGE_PROCESSOR"):
    """Helper to add debug messages."""
    add_debug_message(message, category)


def _extract_spreadsheet_id(url: str) -> str:
    """
    Extracts the spreadsheet ID from a Google Sheets URL.
    
    Handles formats like:
      - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
      - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/export?format=tsv
      - https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/gviz/tq?...
    
    Returns the ID string or empty string if not found.
    """
    import re
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else ""


def process_images_for_sync(spreadsheet_url: str) -> Tuple[bool, str]:
    """
    Main function to process images before sync.
    Triggers the Google Apps Script Web App to process embedded images.
    
    Args:
        spreadsheet_url: URL of the spreadsheet to process
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    from .config_manager import (
        get_image_processor_config,
        get_image_processor_enabled
    )
    
    # Check if image processor is enabled
    if not get_image_processor_enabled():
        return True, "Image processor disabled"
    
    add_debug_msg("=" * 70)
    add_debug_msg("📸 IMAGE PROCESSOR - Starting")
    add_debug_msg("=" * 70)
    
    # Get configuration
    config = get_image_processor_config()
    imgbb_key = config.get("imgbb_api_key", "")
    webapp_url = config.get("webapp_url", "")
    
    if not imgbb_key:
        error_msg = "ImgBB API key not configured"
        add_debug_msg(f"❌ {error_msg}")
        return False, error_msg
    
    if not webapp_url:
        error_msg = "Google Apps Script Web App URL not configured"
        add_debug_msg(f"❌ {error_msg}")
        return False, error_msg
    
    # Extract spreadsheet ID from URL
    spreadsheet_id = _extract_spreadsheet_id(spreadsheet_url)
    if not spreadsheet_id:
        error_msg = f"Could not extract spreadsheet ID from URL: {spreadsheet_url}"
        add_debug_msg(f"❌ {error_msg}")
        return False, error_msg
    
    add_debug_msg(f"📋 Spreadsheet ID: {spreadsheet_id}")
    
    # Trigger the Google Apps Script
    add_debug_msg(f"🌐 Triggering Web App: {webapp_url[:60]}...")
    
    try:
        import urllib.request
        import urllib.error
        import json
        
        # Prepare POST payload with spreadsheet ID
        payload = json.dumps({
            "imgbb_api_key": imgbb_key,
            "spreadsheet_id": spreadsheet_id
        }).encode("utf-8")
        
        # Create request
        req = urllib.request.Request(
            webapp_url,
            data=payload,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )
        
        # Send request (timeout 120s — image processing can be slow)
        add_debug_msg("⏳ Waiting for script to complete...")
        with urllib.request.urlopen(req, timeout=120) as response:
            response_data = response.read().decode("utf-8")
            result = json.loads(response_data)
        
        add_debug_msg(f"📬 Script response: {json.dumps(result, indent=2)}")
        
        # Parse result
        success = result.get("success", False)
        message = result.get("message", "No message from script")
        images_found = result.get("images_found", 0)
        images_processed = result.get("images_processed", 0)
        already_processed = result.get("already_processed", 0)
        errors = result.get("errors", [])
        
        # Log details
        add_debug_msg(f"  📊 Images found: {images_found}")
        add_debug_msg(f"  ✅ Images processed: {images_processed}")
        add_debug_msg(f"  ⏭️ Already processed: {already_processed}")
        if errors:
            for err in errors[:5]:
                add_debug_msg(f"  ❌ Error: {err}")
        
        add_debug_msg(f"\n{'=' * 70}")
        add_debug_msg(f"{'✅' if success else '❌'} IMAGE PROCESSOR - Completed: {message}")
        add_debug_msg(f"{'=' * 70}\n")
        
        return success, message
        
    except urllib.error.URLError as e:
        error_msg = f"Failed to connect to Web App: {e}"
        add_debug_msg(f"❌ {error_msg}")
        return False, error_msg
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid response from Web App: {e}"
        add_debug_msg(f"❌ {error_msg}")
        return False, error_msg
        
    except Exception as e:
        error_msg = f"Image processing error: {e}"
        add_debug_msg(f"❌ {error_msg}")
        return False, error_msg
