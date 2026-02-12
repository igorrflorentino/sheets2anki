"""
Embedded Google Apps Script content for image processing.
This is bundled with the addon so users can copy it to their clipboard.
"""

APPS_SCRIPT_CONTENT = r'''/**
 * Sheets2Anki Image Processor - Google Apps Script (Standalone)
 * 
 * Deploy this script ONCE as a standalone Web App. It works with ANY
 * spreadsheet - the addon sends the spreadsheet_id in each request.
 * 
 * Two-column workflow on the "Notes" sheet:
 *   - "IMAGE" column: contains the original in-cell images (NEVER modified)
 *   - "HTML IMAGE" column: receives the processed HTML <img> tags
 * 
 * Flow:
 * 1. Opens the target spreadsheet by ID
 * 2. Scans the "IMAGE" column for in-cell images
 * 3. Uploads new images to ImgBB
 * 4. Writes HTML <img> tags into the corresponding "HTML IMAGE" cell
 * 5. Skips rows where "HTML IMAGE" is already filled (to reprocess, clear it)
 * 
 * Deploy as a Web App (script.google.com > New Project):
 *   - Execute as: Me
 *   - Who has access: Anyone
 * 
 * The Sheets2Anki addon triggers this script via HTTP POST.
 */

// ============================================================================
// WEB APP ENTRY POINT
// ============================================================================

/**
 * Handles POST requests from the Sheets2Anki addon.
 * 
 * Expected JSON payload:
 *   { "imgbb_api_key": "your_api_key", "spreadsheet_id": "abc123..." }
 * 
 * Returns JSON:
 *   { "success": bool, "images_found": int, "images_processed": int,
 *     "already_processed": int, "errors": [...], "message": "..." }
 */
function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents);
    var imgbbApiKey = payload.imgbb_api_key;
    var spreadsheetId = payload.spreadsheet_id;
    
    if (!imgbbApiKey) {
      return jsonResponse_({
        success: false,
        message: "Missing imgbb_api_key in request payload"
      });
    }
    
    if (!spreadsheetId) {
      return jsonResponse_({
        success: false,
        message: "Missing spreadsheet_id in request payload"
      });
    }
    
    var result = processImages_(spreadsheetId, imgbbApiKey);
    return jsonResponse_(result);
    
  } catch (error) {
    return jsonResponse_({
      success: false,
      message: "Script error: " + error.message,
      errors: [error.message]
    });
  }
}

/**
 * Handles GET requests (used for testing connectivity).
 */
function doGet(e) {
  return jsonResponse_({
    success: true,
    message: "Sheets2Anki Image Processor is ready",
    version: "3.0"
  });
}

// ============================================================================
// CORE IMAGE PROCESSING
// ============================================================================

/**
 * Processes in-cell images from the "IMAGE" column → uploads to ImgBB →
 * writes HTML <img> tags into the "HTML IMAGE" column.
 * 
 * The original image in "IMAGE" is NEVER modified.
 * If the corresponding "HTML IMAGE" cell is NOT empty, the row is skipped
 * (already processed).
 * 
 * To reprocess an image, simply clear the "HTML IMAGE" cell for that row.
 * 
 * @param {string} spreadsheetId - Google Sheets spreadsheet ID
 * @param {string} imgbbApiKey - ImgBB API key
 * @returns {Object} Processing results
 */
function processImages_(spreadsheetId, imgbbApiKey) {
  var ss;
  try {
    ss = SpreadsheetApp.openById(spreadsheetId);
  } catch (e) {
    return {
      success: false,
      images_found: 0,
      images_processed: 0,
      already_processed: 0,
      message: "Cannot open spreadsheet. Make sure the ID is correct and you have access. Error: " + e.message,
      errors: [e.message]
    };
  }
  
  var sheet = ss.getSheetByName("Notes");
  
  if (!sheet) {
    return {
      success: true,
      images_found: 0,
      images_processed: 0,
      already_processed: 0,
      message: "No 'Notes' sheet found in spreadsheet",
      errors: []
    };
  }
  
  // Find both columns by scanning the header row
  var headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var sourceCol = -1;  // "IMAGE" column (source - contains in-cell images)
  var outputCol = -1;  // "HTML IMAGE" column (output - receives HTML tags)
  
  for (var h = 0; h < headerRow.length; h++) {
    var colName = String(headerRow[h]).trim().toUpperCase();
    if (colName === "IMAGE") {
      sourceCol = h + 1;
    } else if (colName === "HTML IMAGE") {
      outputCol = h + 1;
    }
  }
  
  if (sourceCol === -1) {
    return {
      success: true,
      images_found: 0,
      images_processed: 0,
      already_processed: 0,
      message: "No 'IMAGE' column found in 'Notes' sheet",
      errors: []
    };
  }
  
  if (outputCol === -1) {
    return {
      success: true,
      images_found: 0,
      images_processed: 0,
      already_processed: 0,
      message: "No 'HTML IMAGE' column found in 'Notes' sheet",
      errors: []
    };
  }
  
  var lastRow = sheet.getLastRow();
  
  if (lastRow < 2) {
    return {
      success: true,
      images_found: 0,
      images_processed: 0,
      already_processed: 0,
      message: "No data rows in 'Notes' sheet",
      errors: []
    };
  }
  
  var imagesFound = 0;
  var imagesProcessed = 0;
  var alreadyProcessed = 0;
  var errors = [];
  
  // Read both columns at once: source (IMAGE) and output (HTML IMAGE)
  var numRows = lastRow - 1;
  var sourceValues = sheet.getRange(2, sourceCol, numRows, 1).getValues();
  var outputValues = sheet.getRange(2, outputCol, numRows, 1).getValues();
  
  for (var r = 0; r < numRows; r++) {
    var sourceValue = sourceValues[r][0];
    var outputValue = outputValues[r][0];
    var row = r + 2; // actual row (1-indexed, skip header)
    
    // Skip rows where IMAGE column is empty or plain text (no image)
    if (!sourceValue || typeof sourceValue === "string" || typeof sourceValue === "number") {
      continue;
    }
    
    // This row has something in the IMAGE column (likely a CellImage)
    imagesFound++;
    
    // If HTML IMAGE column is NOT empty, skip (already processed)
    if (outputValue && String(outputValue).trim() !== "") {
      alreadyProcessed++;
      continue;
    }
    
    // Process the in-cell image from the IMAGE column
    try {
      var contentUrl = null;
      
      if (typeof sourceValue.getContentUrl === "function") {
        contentUrl = sourceValue.getContentUrl();
      } else if (typeof sourceValue.getUrl === "function") {
        contentUrl = sourceValue.getUrl();
      }
      
      if (!contentUrl) {
        errors.push("Row " + row + ": could not get image URL from IMAGE cell");
        continue;
      }
      
      // Fetch the image
      var response = UrlFetchApp.fetch(contentUrl);
      var imageBlob = response.getBlob();
      
      // Upload to ImgBB
      var imgbbUrl = uploadToImgBB_(imageBlob, imgbbApiKey, "sheets2anki_row" + row);
      
      if (!imgbbUrl) {
        errors.push("Failed to upload image at row " + row);
        continue;
      }
      
      // Write HTML tag to the HTML IMAGE column (never touches the IMAGE column)
      var htmlTag = '<img src="' + imgbbUrl + '" style="max-width: 400px; height: auto;">';
      sheet.getRange(row, outputCol).setValue(htmlTag);
      
      imagesProcessed++;
      
    } catch (cellError) {
      errors.push("Error processing image at row " + row + ": " + cellError.message);
    }
  }
  
  // No images found at all
  if (imagesFound === 0) {
    return {
      success: true,
      images_found: 0,
      images_processed: 0,
      already_processed: 0,
      message: "No in-cell images found in 'IMAGE' column",
      errors: []
    };
  }
  
  // Build summary message
  var message = "";
  if (imagesProcessed > 0 && alreadyProcessed > 0) {
    message = "Processed " + imagesProcessed + " new image(s), " + alreadyProcessed + " already up to date";
  } else if (imagesProcessed > 0) {
    message = "Successfully processed " + imagesProcessed + " image(s)";
  } else if (alreadyProcessed > 0) {
    message = "All " + alreadyProcessed + " image(s) already processed - nothing to do";
  } else if (errors.length > 0) {
    message = "Failed to process images";
  }
  
  if (errors.length > 0) {
    message += " (" + errors.length + " error(s))";
  }
  
  return {
    success: errors.length === 0 || imagesProcessed > 0,
    images_found: imagesFound,
    images_processed: imagesProcessed,
    already_processed: alreadyProcessed,
    message: message,
    errors: errors
  };
}

// ============================================================================
// ImgBB UPLOAD
// ============================================================================

/**
 * Uploads an image blob to ImgBB.
 * 
 * @param {Blob} imageBlob - Image blob to upload
 * @param {string} apiKey - ImgBB API key
 * @param {string} name - Image name
 * @returns {string|null} ImgBB URL or null on failure
 */
function uploadToImgBB_(imageBlob, apiKey, name) {
  try {
    var imageBase64 = Utilities.base64Encode(imageBlob.getBytes());
    
    var formData = {
      "key": apiKey,
      "image": imageBase64,
      "name": name
    };
    
    var options = {
      "method": "post",
      "payload": formData,
      "muteHttpExceptions": true
    };
    
    var response = UrlFetchApp.fetch("https://api.imgbb.com/1/upload", options);
    var responseCode = response.getResponseCode();
    
    if (responseCode !== 200) {
      Logger.log("ImgBB upload failed with code " + responseCode + ": " + response.getContentText());
      return null;
    }
    
    var result = JSON.parse(response.getContentText());
    
    if (result.success) {
      return result.data.url;
    } else {
      Logger.log("ImgBB error: " + JSON.stringify(result.error));
      return null;
    }
    
  } catch (error) {
    Logger.log("Upload error: " + error.message);
    return null;
  }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Creates a JSON response for the web app.
 * 
 * @param {Object} data - Response data
 * @returns {TextOutput} JSON response
 */
function jsonResponse_(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
'''
