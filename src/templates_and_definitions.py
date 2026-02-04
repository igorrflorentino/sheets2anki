"""
Templates and column definitions for the Sheets2Anki addon.

This module centralizes:
- Standardized spreadsheet column name definitions
- HTML templates for Anki cards
- Functions for creating note models
- Data structure validation

Consolidated from:
- card_templates.py: Card templates and models
- column_definitions.py: Spreadsheet column definitions
"""

# =============================================================================
# CONTROL FIELDS
# =============================================================================

# Basic system fields
identifier = "ID"  # Unique question identifier (required)
students = "STUDENTS"  # Indicates which students are interested in studying this note
is_sync = "SYNC"  # Synchronization control field (true/false/1/0)

# =============================================================================
# MAIN FIELDS
# =============================================================================

# Main question fields
question = "QUESTION"  # Main question text / front of card
answer = "ANSWER"  # Succinct and atomic answer to the question
reverse = "REVERSE"  # Reverse question (Answer -> Question)

# =============================================================================
# DETAIL FIELDS
# =============================================================================

# Additional information about the question
info_1 = "COMPLEMENTARY INFO"  # Basic complementary information
info_2 = "DETAILED INFO"  # Additional detailed information

# =============================================================================
# EXAMPLE FIELDS
# =============================================================================

# Examples related to the question (up to 3 examples)
example_1 = "EXAMPLE 1"  # First example
example_2 = "EXAMPLE 2"  # Second example
mnemonic = "MNEMONIC"  # Mnemonic for memory aid

# =============================================================================
# MULTIMEDIA FIELDS
# =============================================================================

# Helps make information visually more attractive
multimedia_1 = "HTML IMAGE"  # HTML code for renderable images and illustrations
multimedia_2 = "HTML VIDEO"  # HTML code for embedded videos (YouTube, Vimeo, etc.)

# =============================================================================
# CATEGORIZATION FIELDS
# =============================================================================

# Hierarchical content categorization
hierarchy_1 = "IMPORTANCE"  # Question importance level
hierarchy_2 = "TOPIC"  # Main question topic
hierarchy_3 = "SUBTOPIC"  # Specific subtopic
hierarchy_4 = "CONCEPT"  # Atomic concept being asked (more refined than subtopic)

# =============================================================================
# METADATA FIELDS
# =============================================================================

# Context and source information
tags_1 = "BOARDS"  # Related exam boards
tags_2 = "LAST YEAR IN EXAM"  # Last year appeared in exam
tags_3 = "CAREERS"  # Related careers or professional areas
tags_4 = "OTHER TAGS"  # Additional tags for organization

# =============================================================================
# CUSTOMIZABLE EXTRA FIELDS
# =============================================================================

# Extra fields for user customization
extra_field_1 = "EXTRA FIELD 1"  # Extra field 1 - free use
extra_field_2 = "EXTRA FIELD 2"  # Extra field 2 - free use
extra_field_3 = "EXTRA FIELD 3"  # Extra field 3 - free use

# =============================================================================
# VALIDATION CONFIGURATIONS
# =============================================================================

# Complete list of all available spreadsheet columns
ALL_AVAILABLE_COLUMNS = [
    identifier,  # Unique identifier
    students,  # Interested students control
    is_sync,  # Synchronization control

    hierarchy_1,  # Importance level
    hierarchy_2,  # Main topic
    hierarchy_3,  # Subtopic
    hierarchy_4,  # Atomic concept

    question,  # Main question text / front of card
    answer,  # Succinct answer (core of response)
    reverse,  # Reverse question

    info_1,  # Complementary info
    info_2,  # Detailed info

    example_1,  # First example
    example_2,  # Second example
    mnemonic,  # Mnemonic for memory aid

    multimedia_1,  # HTML code for images and illustrations
    multimedia_2,  # HTML code for embedded videos

    tags_1,  # Related exam boards
    tags_2,  # Exam year
    tags_3,  # Careers or professional areas
    tags_4,  # Additional tags

    extra_field_1,  # Extra field 1
    extra_field_2,  # Extra field 2
    extra_field_3,  # Extra field 3
]

# Fields considered mandatory for note creation
# Fields considered mandatory for note creation
ESSENTIAL_FIELDS = [identifier]

# Fields required in spreadsheet headers (for parsing to work)
# Fields required in spreadsheet headers (for parsing to work)
REQUIRED_HEADERS = [identifier, question, answer]

# Fields that can be used for filtering/selection
# Fields that can be used for filtering/selection
FILTER_FIELDS = [hierarchy_1, hierarchy_2, hierarchy_3, hierarchy_4,
                 tags_1, tags_2, tags_3, tags_4]

# Fields containing extensive text information
TEXT_FIELDS = [
    question,
    answer,
    reverse,
    info_1,
    info_2,
    example_1,
    example_2,
    mnemonic,
    extra_field_1,
    extra_field_2,
    extra_field_3,
]

# Fields containing media (images, videos, etc.)
MEDIA_FIELDS = [
    multimedia_1,
    multimedia_2,
]

# Fields that should be included in Anki notes
NOTE_FIELDS = [
    identifier,  # Unique identifier
    
    hierarchy_1,  # Importance level
    hierarchy_2,  # Main topic
    hierarchy_3,  # Subtopic
    hierarchy_4,  # Atomic concept
    
    question,  # Question text
    reverse,  # Reverse question
    answer,  # Succinct answer (core of response)
    
    info_1,  # Complementary info
    info_2,  # Detailed info
    
    example_1,  # First example
    example_2,  # Second example
    mnemonic,  # Mnemonic for memory aid
    
    multimedia_1,  # HTML code for images and illustrations
    multimedia_2,  # HTML code for embedded videos

    extra_field_1,  # Extra field 1
    extra_field_2,  # Extra field 2
    extra_field_3,  # Extra field 3
    
    tags_1,  # Related exam boards
    tags_2,  # Exam year
    tags_3,  # Careers or professional areas
    tags_4,  # Additional tags
]

# Fields containing metadata
METADATA_FIELDS = [
    hierarchy_1,
    hierarchy_2,
    hierarchy_3,
    hierarchy_4,
    tags_1,
    tags_2,
    tags_3,
    tags_4,
]

# =============================================================================
# CONSTANTS AND TEMPLATES
# =============================================================================

# Constant to identify if we are in development mode
# This constant will be changed to False during the build process
IS_DEVELOPMENT_MODE = True

# Hardcoded URLs for testing and simulations
TEST_SHEETS_URLS = [
    (
        "Sheets2Anki Template (Edit Link)",
        "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing",
    )
]

# Template constants for card generation
CARD_SHOW_ALLWAYS_TEMPLATE = """
<b>➡️ {field_name}</b><br>
{{{{{field_value}}}}}<br><br>
"""

CARD_SHOW_HIDE_TEMPLATE = """
{{{{#{field_value}}}}}
<b>➡️ {field_name}</b><br>
{{{{{field_value}}}}}<br><br>
{{{{/{field_value}}}}}
"""

MARKERS_TEMPLATE = """
<h2 style="color: orange; text-align: center; margin-bottom: 0;">{text}</h2>
<div style="text-align: center; font-size: 0.8em; color: gray;">{observation}</div>
<hr>
"""

# =============================================================================
# TIMER FEATURE - CSS AND JAVASCRIPT
# =============================================================================

# Timer CSS styling - Between Sections (inline, centered)
TIMER_CSS_BETWEEN_SECTIONS = """
<style>
.sheets2anki-timer {
  display: block;
  width: fit-content;
  margin: 10px auto;
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.75);
  color: #00ff88;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 18px;
  font-weight: bold;
  border-radius: 8px;
  text-align: center;
  user-select: none;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
.sheets2anki-timer::before {
  content: '⏱️ ';
}
.sheets2anki-timer-frozen::before {
  content: '🏁 ';
}
</style>
"""

# Timer CSS styling - Top Middle (fixed position)
TIMER_CSS_TOP_MIDDLE = """
<style>
/* Add padding to prevent timer from covering content */
body {
  padding-top: 50px;
}
.sheets2anki-timer {
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.75);
  color: #00ff88;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 18px;
  font-weight: bold;
  border-radius: 8px;
  z-index: 9999;
  user-select: none;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
.sheets2anki-timer::before {
  content: '⏱️ ';
}
.sheets2anki-timer-frozen::before {
  content: '🏁 ';
}
</style>
"""

# Default timer CSS (for backward compatibility)
TIMER_CSS = TIMER_CSS_BETWEEN_SECTIONS

# Timer JavaScript for FRONT side (starts timer)
TIMER_JS_FRONT = """
<script>
(function() {
  // Start timer when front side loads
  var startTime = Date.now();
  sessionStorage.setItem('sheets2anki_timer_start', startTime.toString());
  
  var timerEl = document.getElementById('sheets2anki-timer');
  if (!timerEl) return;
  
  function formatTime(ms) {
    var totalSeconds = Math.floor(ms / 1000);
    var minutes = Math.floor(totalSeconds / 60);
    var seconds = totalSeconds % 60;
    return (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
  }
  
  function updateTimer() {
    var elapsed = Date.now() - startTime;
    timerEl.textContent = formatTime(elapsed);
  }
  
  // Update immediately and then every second
  updateTimer();
  var intervalId = setInterval(updateTimer, 1000);
  
  // Store interval ID for potential cleanup
  window.sheets2ankiTimerInterval = intervalId;
})();
</script>
"""

# Timer JavaScript for BACK side (shows frozen time)
TIMER_JS_BACK = """
<script>
(function() {
  var timerEl = document.getElementById('sheets2anki-timer');
  if (!timerEl) return;
  
  // Clear any running interval from front side
  if (window.sheets2ankiTimerInterval) {
    clearInterval(window.sheets2ankiTimerInterval);
  }
  
  // Change emoji to 🏁 to indicate frozen/finished state
  timerEl.classList.add('sheets2anki-timer-frozen');
  
  var startTimeStr = sessionStorage.getItem('sheets2anki_timer_start');
  if (startTimeStr) {
    var startTime = parseInt(startTimeStr, 10);
    var elapsed = Date.now() - startTime;
    
    function formatTime(ms) {
      var totalSeconds = Math.floor(ms / 1000);
      var minutes = Math.floor(totalSeconds / 60);
      var seconds = totalSeconds % 60;
      return (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
    }
    
    timerEl.textContent = formatTime(elapsed);
  } else {
    timerEl.textContent = '--:--';
  }
})();
</script>
"""

# Timer HTML element
TIMER_HTML = '<div id="sheets2anki-timer" class="sheets2anki-timer">00:00</div>'

# =============================================================================
# AI HELP BUTTON - CSS, HTML AND JAVASCRIPT
# =============================================================================

# AI Help Button CSS
AI_HELP_CSS = """
<style>
/* Theme variables - defaults to dark mode */
:root {
  --ai-bg: #1e1e1e;
  --ai-bg-secondary: #2d2d2d;
  --ai-text: #e0e0e0;
  --ai-text-muted: #888;
  --ai-border: #404040;
  --ai-accent: #667eea;
  --ai-accent-secondary: #764ba2;
  --ai-code-bg: #333;
  --ai-code-text: #f8f8f2;
  --ai-error: #ff6b6b;
  --ai-error-bg: rgba(255, 107, 107, 0.1);
  --ai-overlay: rgba(0, 0, 0, 0.7);
  --ai-shadow: rgba(0, 0, 0, 0.5);
}

/* Light mode overrides */
@media (prefers-color-scheme: light) {
  :root {
    --ai-bg: #ffffff;
    --ai-bg-secondary: #f5f5f5;
    --ai-text: #1a1a1a;
    --ai-text-muted: #666;
    --ai-border: #e0e0e0;
    --ai-accent: #5a67d8;
    --ai-accent-secondary: #6b46c1;
    --ai-code-bg: #f0f0f0;
    --ai-code-text: #333;
    --ai-error: #e53e3e;
    --ai-error-bg: rgba(229, 62, 62, 0.1);
    --ai-overlay: rgba(0, 0, 0, 0.5);
    --ai-shadow: rgba(0, 0, 0, 0.2);
  }
}

/* Also support Anki's night mode class */
.night_mode {
  --ai-bg: #1e1e1e;
  --ai-bg-secondary: #2d2d2d;
  --ai-text: #e0e0e0;
  --ai-text-muted: #888;
  --ai-border: #404040;
  --ai-accent: #667eea;
  --ai-accent-secondary: #764ba2;
  --ai-code-bg: #333;
  --ai-code-text: #f8f8f2;
  --ai-error: #ff6b6b;
  --ai-error-bg: rgba(255, 107, 107, 0.1);
}

.ai-help-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 20px 0;
  padding: 10px;
}

.ai-help-button {
  background: linear-gradient(135deg, var(--ai-accent) 0%, var(--ai-accent-secondary) 100%);
  color: white;
  border: none;
  border-radius: 25px;
  padding: 12px 28px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ai-help-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.ai-help-button:active {
  transform: translateY(0);
}

.ai-help-button.loading {
  opacity: 0.7;
  cursor: wait;
}

.ai-help-button .spinner {
  display: none;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

.ai-help-button.loading .spinner {
  display: inline-block;
}

.ai-help-button.loading .btn-text {
  display: none;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* AI Help Response Modal (for desktop) */
.ai-help-modal {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--ai-overlay);
  z-index: 10000;
  justify-content: center;
  align-items: center;
}

.ai-help-modal.show {
  display: flex;
}

.ai-help-modal-content {
  background: var(--ai-bg);
  color: var(--ai-text);
  border-radius: 16px;
  padding: 24px;
  max-width: 90%;
  max-height: 80%;
  overflow-y: auto;
  box-shadow: 0 10px 40px var(--ai-shadow);
  position: relative;
  border: 1px solid var(--ai-border);
}

.ai-help-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--ai-border);
}

.ai-help-modal-title {
  font-size: 18px;
  font-weight: bold;
  color: var(--ai-accent);
}

.ai-help-modal-close {
  background: none;
  border: none;
  color: var(--ai-text-muted);
  font-size: 24px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.ai-help-modal-close:hover {
  background: var(--ai-bg-secondary);
  color: var(--ai-text);
}

.ai-help-modal-body {
  line-height: 1.7;
  font-size: 14px;
  color: var(--ai-text);
}

.ai-help-modal-body h2,
.ai-help-modal-body h3,
.ai-help-modal-body h4 {
  color: var(--ai-accent);
  margin: 16px 0 8px 0;
}

.ai-help-modal-body h2 { font-size: 18px; }
.ai-help-modal-body h3 { font-size: 16px; }
.ai-help-modal-body h4 { font-size: 15px; }

.ai-help-modal-body p { margin: 8px 0; }
.ai-help-modal-body ul { margin: 8px 0; padding-left: 24px; }
.ai-help-modal-body li { margin: 4px 0; }

.ai-help-modal-body code {
  background: var(--ai-code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--ai-code-text);
}

.ai-help-modal-body strong { color: var(--ai-text); font-weight: 600; }
.ai-help-modal-body hr { border: none; border-top: 1px solid var(--ai-border); margin: 16px 0; }

.ai-help-error {
  color: var(--ai-error);
  padding: 12px;
  background: var(--ai-error-bg);
  border-radius: 8px;
  text-align: center;
}

/* Usage info - vertical layout */
.ai-help-usage {
  margin-top: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--ai-border);
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: var(--ai-text-muted);
}

.ai-help-usage span {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Inline response area (for mobile) */
.ai-help-inline {
  display: none;
  width: 100%;
  max-width: 600px;
  margin-top: 15px;
  padding: 16px;
  background: var(--ai-bg);
  border: 1px solid var(--ai-border);
  border-radius: 12px;
  line-height: 1.7;
  font-size: 14px;
  color: var(--ai-text);
  box-shadow: 0 4px 12px var(--ai-shadow);
}

.ai-help-inline.show {
  display: block;
}

.ai-help-inline h2,
.ai-help-inline h3,
.ai-help-inline h4 {
  color: var(--ai-accent);
  margin: 16px 0 8px 0;
}

.ai-help-inline h2 { font-size: 18px; }
.ai-help-inline h3 { font-size: 16px; }
.ai-help-inline h4 { font-size: 15px; }

.ai-help-inline p { margin: 8px 0; }
.ai-help-inline ul { margin: 8px 0; padding-left: 24px; }
.ai-help-inline li { margin: 4px 0; }

.ai-help-inline code {
  background: var(--ai-code-bg);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--ai-code-text);
}

.ai-help-inline strong { color: var(--ai-text); font-weight: 600; }
.ai-help-inline hr { border: none; border-top: 1px solid var(--ai-border); margin: 16px 0; }

.ai-help-inline .ai-help-error {
  color: var(--ai-error);
  padding: 12px;
  background: var(--ai-error-bg);
  border-radius: 8px;
  text-align: center;
}

/* Base Table Styles */
.ai-help-modal-body table,
.ai-help-inline table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
  font-size: 14px;
}

.ai-help-modal-body th,
.ai-help-inline th {
  background: var(--ai-bg-secondary);
  color: var(--ai-accent);
  font-weight: bold;
  text-align: left;
  padding: 10px 12px;
  border: 1px solid var(--ai-border);
}

.ai-help-modal-body td,
.ai-help-inline td {
  padding: 8px 12px;
  border: 1px solid var(--ai-border);
  color: var(--ai-text);
}

.ai-help-modal-body tr:nth-child(even),
.ai-help-inline tr:nth-child(even) {
  background: rgba(128, 128, 128, 0.05);
}

.ai-help-modal-body tr:hover,
.ai-help-inline tr:hover {
  background: rgba(128, 128, 128, 0.1);
}

</style>
"""

# AI Help Button HTML
AI_HELP_BUTTON_HTML = """
<div class="ai-help-container">
  <!-- Load marked.js for markdown parsing -->
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <button id="ai-help-btn" class="ai-help-button" onclick="requestAIHelp()">
    <span class="btn-text">🤖 AI Help</span>
    <span class="spinner"></span>
  </button>
  <div id="ai-help-inline" class="ai-help-inline"></div>
</div>

<div id="ai-help-modal" class="ai-help-modal" onclick="closeAIHelpModal(event)">
  <div class="ai-help-modal-content" onclick="event.stopPropagation()">
    <div class="ai-help-modal-header">
      <span class="ai-help-modal-title">🤖 AI Help</span>
      <button class="ai-help-modal-close" onclick="closeAIHelpModal()">&times;</button>
    </div>
    <div id="ai-help-modal-body" class="ai-help-modal-body">
      Loading...
    </div>
  </div>
</div>
"""

# AI Help JavaScript - Base template (desktop-only mode)
AI_HELP_JS_DESKTOP = """
<script>
// Desktop-only mode: hide button if pycmd not available
(function() {
  if (typeof pycmd === 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
      var container = document.querySelector('.ai-help-container');
      if (container) container.style.display = 'none';
    });
    var container = document.querySelector('.ai-help-container');
    if (container) container.style.display = 'none';
  }
})();

function requestAIHelp() {
  var btn = document.getElementById('ai-help-btn');
  if (!btn || btn.classList.contains('loading')) return;
  
  btn.classList.add('loading');
  var cardContent = collectCardContent();
  
  if (typeof pycmd !== 'undefined') {
    pycmd('sheets2anki_ai_help:' + encodeURIComponent(cardContent));
  } else {
    btn.classList.remove('loading');
  }
}

""" + """
function collectCardContent() {
  var allText = document.body.innerText || document.body.textContent;
  return allText.trim();
}

""" + """
function processMathAndMarkdown(text) {
  var mathBlocks = [];
  var placeholder = "MATHBLOCK";
  var suffix = "END";
  
  // Display math $$ ... $$ -> \[ ... \]
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, function(match, content) {
    var id = mathBlocks.length;
    mathBlocks.push('\\\\[' + content + '\\\\]');
    return placeholder + id + suffix;
  });
  
  // Inline math $ ... $ -> \( ... \) (Disallow newlines)
  text = text.replace(/([^\\\\$]|^)\$([^\s$\\n](?:[^$\\n]*?[^\s$\\n])?)\$(?!\d)/g, function(match, prefix, content) {
    var id = mathBlocks.length;
    mathBlocks.push('\\\\(' + content + '\\\\)');
    return prefix + placeholder + id + suffix;
  });
  
  var html = (typeof marked !== 'undefined') ? marked.parse(text) : text;
  
  for (var i = 0; i < mathBlocks.length; i++) {
    var regex = new RegExp(placeholder + i + suffix, 'g');
    html = html.replace(regex, mathBlocks[i]);
  }
  
  return html;
}

function renderMathJax() {
  if (typeof MathJax !== 'undefined') {
    if (MathJax.typesetPromise) {
      MathJax.typesetPromise();
    } else if (MathJax.Hub && MathJax.Hub.Queue) {
      MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    }
  }
}

function showAIHelpResponse(response, usageInfo) {
  var btn = document.getElementById('ai-help-btn');
  if (btn) btn.classList.remove('loading');
  
  var modal = document.getElementById('ai-help-modal');
  var body = document.getElementById('ai-help-modal-body');
  
  var html = processMathAndMarkdown(response);
  
  if (usageInfo && (usageInfo.input_tokens || usageInfo.output_tokens)) {
    var totalTokens = usageInfo.input_tokens + usageInfo.output_tokens;
    var cost = usageInfo.cost || 0;
    var costStr = cost < 0.01 ? cost.toFixed(6) : cost.toFixed(4);
    html += '<div class="ai-help-usage">';
    html += '<span>📊 Tokens: ' + totalTokens + ' (' + usageInfo.input_tokens + ' in / ' + usageInfo.output_tokens + ' out)</span>';
    html += '<span>💰 Cost: $' + costStr + '</span>';
    html += '</div>';
  }
  
  body.innerHTML = html;
  modal.classList.add('show');
  
  // Trigger MathJax
  setTimeout(renderMathJax, 10);
}

function showAIHelpError(error) {
  var btn = document.getElementById('ai-help-btn');
  if (btn) btn.classList.remove('loading');
  
  var modal = document.getElementById('ai-help-modal');
  var body = document.getElementById('ai-help-modal-body');
  body.innerHTML = '<div class="ai-help-error">⚠️ ' + error + '</div>';
  modal.classList.add('show');
}

function closeAIHelpModal(event) {
  if (event && event.target !== event.currentTarget) return;
  var modal = document.getElementById('ai-help-modal');
  modal.classList.remove('show');
}

if (typeof globalThis !== 'undefined') {
  globalThis.sheets2ankiAIResponse = function(response, usageInfo) {
    showAIHelpResponse(response, usageInfo);
  };
  globalThis.sheets2ankiAIError = function(error) {
    showAIHelpError(error);
  };
}
</script>
"""

# AI Help JavaScript - Mobile mode (with embedded API config)
AI_HELP_JS_MOBILE_TEMPLATE = """
<script>
// AI Help Config (embedded for mobile support)
var AI_CONFIG = {{
  service: '{service}',
  model: '{model}',
  apiKey: '{api_key}',
  prompt: {prompt_json}
}};

// Pricing per 1M tokens
var PRICING = {{
  'gemini-2.0-flash': [0.10, 0.40],
  'gemini-1.5-flash': [0.075, 0.30],
  'gemini-1.5-pro': [1.25, 5.00],
  'gemini-pro': [0.50, 1.50],
  'claude-sonnet-4': [3.00, 15.00],
  'claude-3-5-sonnet': [3.00, 15.00],
  'claude-3-5-haiku': [0.80, 4.00],
  'claude-3-opus': [15.00, 75.00],
  'claude-3-haiku': [0.25, 1.25],
  'gpt-4o': [2.50, 10.00],
  'gpt-4o-mini': [0.15, 0.60],
  'gpt-4-turbo': [10.00, 30.00],
  'gpt-4': [30.00, 60.00],
  'gpt-3.5-turbo': [0.50, 1.50]
}};

function getPricing(model) {{
  model = model.toLowerCase();
  for (var prefix in PRICING) {{
    if (model.indexOf(prefix) !== -1) return PRICING[prefix];
  }}
  return [1.00, 3.00];
}}

function calculateCost(model, inputTokens, outputTokens) {{
  var p = getPricing(model);
  return (inputTokens * p[0] / 1000000) + (outputTokens * p[1] / 1000000);
}}

function requestAIHelp() {{
  var btn = document.getElementById('ai-help-btn');
  if (!btn || btn.classList.contains('loading')) return;
  
  btn.classList.add('loading');
  var cardContent = collectCardContent();
  
  // Try desktop first
  if (typeof pycmd !== 'undefined') {{
    pycmd('sheets2anki_ai_help:' + encodeURIComponent(cardContent));
    return;
  }}
  
  // Mobile: direct API call
  callAIAPI(cardContent);
}}

function callAIAPI(cardContent) {{
  var prompt = AI_CONFIG.prompt.replace(/\\u007B\\u007Bcard_content\\u007D\\u007D|\\u007Bcard_content\\u007D/g, cardContent);
  if (prompt.indexOf(cardContent) === -1) {{
    prompt = prompt + '\\n\\n' + cardContent;
  }}
  
  if (AI_CONFIG.service === 'gemini') {{
    callGeminiAPI(prompt);
  }} else if (AI_CONFIG.service === 'claude') {{
    callClaudeAPI(prompt);
  }} else if (AI_CONFIG.service === 'openai') {{
    callOpenAIAPI(prompt);
  }}
}}

function callGeminiAPI(prompt) {{
  var url = 'https://generativelanguage.googleapis.com/v1beta/models/' + AI_CONFIG.model + ':generateContent?key=' + AI_CONFIG.apiKey;
  
  fetch(url, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{
      contents: [{{ parts: [{{ text: prompt }}] }}],
      generationConfig: {{ temperature: 0.7, maxOutputTokens: 4096 }}
    }})
  }})
  .then(function(r) {{ return r.json(); }})
  .then(function(data) {{
    if (data.error) {{
      showAIHelpError(data.error.message || 'API Error');
      return;
    }}
    var text = '';
    try {{
      text = data.candidates[0].content.parts[0].text;
    }} catch(e) {{
      text = 'No response generated';
    }}
    var usage = data.usageMetadata || {{}};
    var inputTokens = usage.promptTokenCount || 0;
    var outputTokens = usage.candidatesTokenCount || 0;
    showAIHelpResponse(text, {{
      input_tokens: inputTokens,
      output_tokens: outputTokens,
      cost: calculateCost(AI_CONFIG.model, inputTokens, outputTokens)
    }});
  }})
  .catch(function(e) {{ showAIHelpError('Request failed: ' + e.message); }});
}}

function callClaudeAPI(prompt) {{
  // Note: Claude API may have CORS restrictions from browser
  var url = 'https://api.anthropic.com/v1/messages';
  
  fetch(url, {{
    method: 'POST',
    headers: {{
      'Content-Type': 'application/json',
      'x-api-key': AI_CONFIG.apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true'
    }},
    body: JSON.stringify({{
      model: AI_CONFIG.model,
      max_tokens: 4096,
      messages: [{{ role: 'user', content: prompt }}]
    }})
  }})
  .then(function(r) {{ return r.json(); }})
  .then(function(data) {{
    if (data.error) {{
      showAIHelpError(data.error.message || 'API Error');
      return;
    }}
    var text = data.content && data.content[0] ? data.content[0].text : 'No response';
    var usage = data.usage || {{}};
    showAIHelpResponse(text, {{
      input_tokens: usage.input_tokens || 0,
      output_tokens: usage.output_tokens || 0,
      cost: calculateCost(AI_CONFIG.model, usage.input_tokens || 0, usage.output_tokens || 0)
    }});
  }})
  .catch(function(e) {{ showAIHelpError('Request failed: ' + e.message); }});
}}

function callOpenAIAPI(prompt) {{
  var url = 'https://api.openai.com/v1/chat/completions';
  
  fetch(url, {{
    method: 'POST',
    headers: {{
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + AI_CONFIG.apiKey
    }},
    body: JSON.stringify({{
      model: AI_CONFIG.model,
      messages: [{{ role: 'user', content: prompt }}],
      max_tokens: 4096,
      temperature: 0.7
    }})
  }})
  .then(function(r) {{ return r.json(); }})
  .then(function(data) {{
    if (data.error) {{
      showAIHelpError(data.error.message || 'API Error');
      return;
    }}
    var text = data.choices && data.choices[0] ? data.choices[0].message.content : 'No response';
    var usage = data.usage || {{}};
    showAIHelpResponse(text, {{
      input_tokens: usage.prompt_tokens || 0,
      output_tokens: usage.completion_tokens || 0,
      cost: calculateCost(AI_CONFIG.model, usage.prompt_tokens || 0, usage.completion_tokens || 0)
    }});
  }})
  .catch(function(e) {{ showAIHelpError('Request failed: ' + e.message); }});
}}

function collectCardContent() {{
  var allText = document.body.innerText || document.body.textContent;
  return allText.trim();
}}

function processMathAndMarkdown(text) {{
  var mathBlocks = [];
  var placeholder = "MATHBLOCK";
  var suffix = "END";
  
  // Display math $$ ... $$ -> \[ ... \]
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, function(match, content) {{
    var id = mathBlocks.length;
    mathBlocks.push('\\\\[' + content + '\\\\]');
    return placeholder + id + suffix;
  }});
  
  // Inline math $ ... $ -> \( ... \)
  text = text.replace(/([^\\\\$]|^)\$([^\s$\\n](?:[^$\\n]*?[^\s$\\n])?)\$(?!\d)/g, function(match, prefix, content) {{
    var id = mathBlocks.length;
    mathBlocks.push('\\\\(' + content + '\\\\)');
    return prefix + placeholder + id + suffix;
  }});
  
  var html = (typeof marked !== 'undefined') ? marked.parse(text) : text;
  
  for (var i = 0; i < mathBlocks.length; i++) {{
    var regex = new RegExp(placeholder + i + suffix, 'g');
    html = html.replace(regex, mathBlocks[i]);
  }}
  
  return html;
}}

function renderMathJax() {{
  if (typeof MathJax !== 'undefined') {{
    if (MathJax.typesetPromise) {{
      MathJax.typesetPromise();
    }} else if (MathJax.Hub && MathJax.Hub.Queue) {{
      MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    }}
  }}
}}

function showAIHelpResponse(response, usageInfo) {{
  var btn = document.getElementById('ai-help-btn');
  if (btn) btn.classList.remove('loading');
  
  var html = processMathAndMarkdown(response);
  
  if (usageInfo && (usageInfo.input_tokens || usageInfo.output_tokens)) {{
    var totalTokens = usageInfo.input_tokens + usageInfo.output_tokens;
    var cost = usageInfo.cost || 0;
    var costStr = cost < 0.01 ? cost.toFixed(6) : cost.toFixed(4);
    html += '<div class="ai-help-usage">';
    html += '<span>📊 Tokens: ' + totalTokens + ' (' + usageInfo.input_tokens + ' in / ' + usageInfo.output_tokens + ' out)</span>';
    html += '<span>💰 Cost: $' + costStr + '</span>';
    html += '</div>';
  }}
  
  // On mobile (no pycmd), show inline; on desktop, use modal
  if (typeof pycmd === 'undefined') {{
    var inline = document.getElementById('ai-help-inline');
    if (inline) {{
      inline.innerHTML = html;
      inline.classList.add('show');
    }}
  }} else {{
    var modal = document.getElementById('ai-help-modal');
    var body = document.getElementById('ai-help-modal-body');
    body.innerHTML = html;
    modal.classList.add('show');
  }}
  
  // Trigger MathJax
  setTimeout(renderMathJax, 10);
}}

function showAIHelpError(error) {{
  var btn = document.getElementById('ai-help-btn');
  if (btn) btn.classList.remove('loading');
  
  var errorHtml = '<div class="ai-help-error">⚠️ ' + error + '</div>';
  
  // On mobile (no pycmd), show inline; on desktop, use modal
  if (typeof pycmd === 'undefined') {{
    var inline = document.getElementById('ai-help-inline');
    if (inline) {{
      inline.innerHTML = errorHtml;
      inline.classList.add('show');
    }}
  }} else {{
    var modal = document.getElementById('ai-help-modal');
    var body = document.getElementById('ai-help-modal-body');
    body.innerHTML = errorHtml;
    modal.classList.add('show');
  }}
}}

function closeAIHelpModal(event) {{
  if (event && event.target !== event.currentTarget) return;
  var modal = document.getElementById('ai-help-modal');
  modal.classList.remove('show');
}}

if (typeof globalThis !== 'undefined') {{
  globalThis.sheets2ankiAIResponse = function(response, usageInfo) {{
    showAIHelpResponse(response, usageInfo);
  }};
  globalThis.sheets2ankiAIError = function(error) {{
    showAIHelpError(error);
  }};
}}
</script>
"""

# Keep old constant for backward compatibility (desktop-only mode)
AI_HELP_JS = AI_HELP_JS_DESKTOP


def generate_ai_help_js(mobile_enabled=False, service="gemini", model="", api_key="", prompt=""):
    """
    Generates AI Help JavaScript based on configuration.
    
    Args:
        mobile_enabled: If True, embed API config for mobile support
        service: AI service (gemini, claude, openai)
        model: Model ID
        api_key: API key
        prompt: Custom prompt template
    
    Returns:
        str: JavaScript code for AI Help
    """
    import json
    
    if not mobile_enabled:
        return AI_HELP_JS_DESKTOP
    
    # Escape curly braces to prevent Anki from interpreting them as fields
    # We replace {{ with \u007B\u007B and }} with \u007D\u007D
    # This keeps the characters in the final JS string but hides them from Anki's template engine
    prompt_json = json.dumps(prompt)
    prompt_json = prompt_json.replace("{{", "\\u007B\\u007B").replace("}}", "\\u007D\\u007D")
    
    return AI_HELP_JS_MOBILE_TEMPLATE.format(
        service=service,
        model=model,
        api_key=api_key,
        prompt_json=prompt_json
    )

# Default values for empty fields (will be converted to lowercase by clean_tag_text)
DEFAULT_IMPORTANCE = "[MISSING_IMPORTANCE]"
DEFAULT_TOPIC = "[MISSING_TOPIC]"
DEFAULT_SUBTOPIC = "[MISSING_SUBTOPIC]"
DEFAULT_CONCEPT = "[MISSING_CONCEPT]"
DEFAULT_STUDENT = "[MISSING_STUDENT]"

# Root deck name - non-modifiable constant by user
DEFAULT_PARENT_DECK_NAME = "Sheets2Anki"

# Tag prefixes (all lowercase for consistency - Anki tags are case-insensitive)
TAG_ROOT = "sheets2anki"
TAG_TOPICS = "topics"
TAG_SUBTOPICS = "subtopics"
TAG_CONCEPTS = "concepts"
TAG_EXAM_BOARDS = "boards"
TAG_YEARS = "years"
TAG_CAREERS = "careers"
TAG_IMPORTANCE = "importance"
TAG_ADDITIONAL = "other_tags"

# =============================================================================
# COLUMN VALIDATION FUNCTIONS
# =============================================================================


def validate_required_columns(columns):
    """
    Validates if all required columns are present in the spreadsheet.

    Args:
        columns (list): List of spreadsheet column names

    Returns:
        tuple: (is_valid, missing_columns) where:
            - is_valid: bool indicating if all columns are present
            - missing_columns: list of missing columns
    """
    missing_columns = [col for col in ALL_AVAILABLE_COLUMNS if col not in columns]
    return len(missing_columns) == 0, missing_columns


def is_essential_field(field_name):
    """
    Checks if a field is considered essential for note creation.

    Args:
        field_name (str): Field name to check

    Returns:
        bool: True if field is essential, False otherwise
    """
    return field_name in ESSENTIAL_FIELDS


def is_filter_field(field_name):
    """
    Checks if a field can be used for filtering/selection.

    Args:
        field_name (str): Field name to check

    Returns:
        bool: True if field can be used for filtering, False otherwise
    """
    return field_name in FILTER_FIELDS


def get_field_category(field_name):
    """
    Returns the category of a specific field.

    Args:
        field_name (str): Field name

    Returns:
        str: Field category ('essential', 'text', 'metadata', 'filter', 'unknown')
    """
    if field_name in ESSENTIAL_FIELDS:
        return "essential"
    elif field_name in TEXT_FIELDS:
        return "text"
    elif field_name in METADATA_FIELDS:
        return "metadata"
    elif field_name in FILTER_FIELDS:
        return "filter"
    else:
        return "unknown"


def should_sync_question(fields):
    """
    Checks if a question should be synchronized based on the SYNC field.

    Args:
        fields (dict): Dictionary with question fields

    Returns:
        bool: True if should synchronize, False otherwise
    """
    sync_value = fields.get(is_sync, "").strip().lower()

    # Consider positive values: true, 1, sim, yes, verdadeiro
    # Consider positive values: true, 1, yes
    positive_values = ["true", "1", "yes", "sim", "v"]

    if sync_value in positive_values:
        return True
    else:
        # If value is not recognized or empty, do NOT synchronize
        # Synchronization must be explicitly marked
        return False


def get_all_column_info():
    """
    Returns complete information about all defined columns.

    Returns:
        dict: Dictionary with detailed information for each column
    """
    column_info = {}

    for column in ALL_AVAILABLE_COLUMNS:
        column_info[column] = {
            "name": column,
            "category": get_field_category(column),
            "is_essential": is_essential_field(column),
            "is_filter": is_filter_field(column),
            "is_text": column in TEXT_FIELDS,
            "is_metadata": column in METADATA_FIELDS,
        }

    return column_info


# =============================================================================
# CARD TEMPLATES
# =============================================================================


def create_card_template(is_cloze=False, timer_position=None, ai_help_enabled=None, is_reverse=False):
    """
    Creates the HTML template for a card (standard or cloze).

    Args:
        is_cloze (bool): Whether to create a cloze template
        timer_position (str): Timer position - "top_middle", "between_sections", or "hidden"
                             If None, reads from config
        ai_help_enabled (bool): Whether to include AI Help button on back card
                               If None, reads from config
        is_reverse (bool): Whether to create a reverse template (Reverse->Question)

    Returns:
        dict: Dictionary with 'qfmt' and 'afmt' template strings
    """
    
    # Get timer position from config if not specified
    if timer_position is None:
        try:
            from .config_manager import get_timer_position
            timer_position = get_timer_position()
        except ImportError:
            timer_position = "between_sections"  # Default fallback
    
    # Get AI Help config from settings if not specified
    ai_help_config = None
    if ai_help_enabled is None:
        try:
            from .config_manager import get_ai_help_config
            ai_help_config = get_ai_help_config()
            ai_help_enabled = ai_help_config.get("enabled", False)
        except ImportError:
            ai_help_enabled = False  # Default fallback
            ai_help_config = None

    # Common header fields
    header_fields = [
        (hierarchy_1, hierarchy_1),
        (hierarchy_2, hierarchy_2),
        (hierarchy_3, hierarchy_3),
        (hierarchy_4, hierarchy_4),
    ]

    # Build header section
    header = ""
    for field_name, field_value in header_fields:
        header += CARD_SHOW_ALLWAYS_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Question format
    question_html = (
        f"<b>❓ {question.capitalize()}</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{question}}}}}<br><br>"
    )

    # Answer format
    answer_html = (
        f"<b>❗️ {answer.capitalize()}</b><br>"
        f"{{{{{'cloze:' if is_cloze else ''}{answer}}}}}<br><br>"
    )

    # Information fields
    info_fields = [info_1, info_2]

    extra_infos = ""
    for info_field in info_fields:
        extra_infos += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=info_field.capitalize(), field_value=info_field
        )

    # Image multimedia field
    image_html = CARD_SHOW_HIDE_TEMPLATE.format(
        field_name=multimedia_1.capitalize(), field_value=multimedia_1
    )

    # Video multimedia field
    video_html = CARD_SHOW_HIDE_TEMPLATE.format(
        field_name=multimedia_2.capitalize(), field_value=multimedia_2
    )

    # Example fields
    example_fields = [example_1, example_2, mnemonic]

    examples = ""
    for field in example_fields:
        examples += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Customizable extra fields
    extra_fields = [extra_field_1, extra_field_2, extra_field_3]

    extras = ""
    for field in extra_fields:
        extras += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field.capitalize(), field_value=field
        )

    # Footer fields
    footer_fields = [
        (tags_1, tags_1),
        (tags_2, tags_2),
        (tags_3, tags_3),
        (tags_4, tags_4),
    ]

    # Build footer section
    footer = ""
    for field_name, field_value in footer_fields:
        footer += CARD_SHOW_HIDE_TEMPLATE.format(
            field_name=field_name.capitalize(), field_value=field_value
        )

    # Determine timer components based on position
    if timer_position == "hidden":
        # No timer
        timer_css = ""
        timer_html = ""
        timer_js_front = ""
        timer_js_back = ""
    elif timer_position == "top_middle":
        # Fixed position at top middle
        timer_css = TIMER_CSS_TOP_MIDDLE
        timer_html = TIMER_HTML
        timer_js_front = TIMER_JS_FRONT
        timer_js_back = TIMER_JS_BACK
    else:  # "between_sections" (default)
        # Between CONTEXT and CARD sections
        timer_css = TIMER_CSS_BETWEEN_SECTIONS
        timer_html = TIMER_HTML
        timer_js_front = TIMER_JS_FRONT
        timer_js_back = TIMER_JS_BACK

    # Build complete templates
    if is_reverse:
        # Question format for Reverse cards (REVERSE field is the question)
        question_html = (
            f"<b>❓ {question.capitalize()}</b><br>"
            f"{{{{{reverse}}}}}<br><br>"
        )
        
        # Answer format for Reverse cards (QUESTION field is the answer)
        answer_html = (
            f"<b>❗️ {answer.capitalize()}</b><br>"
            f"{{{{{question}}}}}<br><br>"
        )

    if timer_position == "top_middle":
        # For top_middle: timer at beginning (fixed position, so doesn't matter)
        qfmt = (
            timer_css +
            timer_html +
            MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
            header +
            MARKERS_TEMPLATE.format(text="CARD", observation="") +
            question_html +
            timer_js_front
        )
    elif timer_position == "hidden":
        # No timer at all
        qfmt = (
            MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
            header +
            MARKERS_TEMPLATE.format(text="CARD", observation="") +
            question_html
        )
    else:  # "between_sections"
        # Timer between CONTEXT and CARD
        qfmt = (
            timer_css +
            MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
            header +
            timer_html +
            MARKERS_TEMPLATE.format(text="CARD", observation="") +
            question_html +
            timer_js_front
        )
    
    # Back template
    if is_cloze:
        back_content = (
            header + 
            (timer_html if timer_position == "between_sections" else "") +
            MARKERS_TEMPLATE.format(text="CARD", observation="") +
            question_html +
            MARKERS_TEMPLATE.format(text="INFORMATION", observation="May be empty") +
            extra_infos + 
            examples + 
            image_html + 
            video_html + 
            extras + 
            MARKERS_TEMPLATE.format(text="TAGS", observation="May be empty") + 
            footer
        )
    else:
        # Basic card: show question + answer + additional info
        back_content = (
            header + 
            (timer_html if timer_position == "between_sections" else "") +
            MARKERS_TEMPLATE.format(text="CARD", observation="") +
            question_html +
            answer_html +
            MARKERS_TEMPLATE.format(text="INFORMATION", observation="May be empty") +
            extra_infos + 
            examples + 
            image_html + 
            video_html + 
            extras + 
            MARKERS_TEMPLATE.format(text="TAGS", observation="May be empty") +
            footer
        )
    
    # Build AI Help components if enabled
    ai_help_components = ""
    if ai_help_enabled:
        # Check if mobile support is enabled
        if ai_help_config and ai_help_config.get("mobile_enabled", False):
            ai_help_js = generate_ai_help_js(
                mobile_enabled=True,
                service=ai_help_config.get("service", "gemini"),
                model=ai_help_config.get("model", ""),
                api_key=ai_help_config.get("api_key", ""),
                prompt=ai_help_config.get("prompt", "")
            )
        else:
            ai_help_js = AI_HELP_JS_DESKTOP
        ai_help_components = AI_HELP_CSS + AI_HELP_BUTTON_HTML + ai_help_js
    
    if timer_position == "top_middle":
        afmt = (
            timer_css +
            timer_html +
            MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
            back_content +
            ai_help_components +
            timer_js_back
        )
    elif timer_position == "hidden":
        afmt = (
            MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
            back_content +
            ai_help_components
        )
    else:  # "between_sections"
        afmt = (
            timer_css +
            MARKERS_TEMPLATE.format(text="CONTEXT", observation="") +
            back_content +
            ai_help_components +
            timer_js_back
        )

    return {"qfmt": qfmt, "afmt": afmt}


def create_model(col, model_name, is_cloze=False, url=None, debug_messages=None, is_reverse=False):
    """
    Creates a new Anki note model.

    Args:
        col: Anki collection object
        model_name (str): Name for the new model
        is_cloze (bool): Whether to create a cloze model
        url (str, optional): Remote deck URL for automatic registration
        debug_messages (list, optional): List for debug
        is_reverse (bool): Whether to create a reverse model
        debug_messages (list, optional): List for debug

    Returns:
        object: The created Anki model
    """
    from .utils import register_note_type_for_deck

    model = col.models.new(model_name)
    if is_cloze:
        model["type"] = 1  # Set as cloze type

    # Add fields (excluding internal control fields like SYNC)
    for field in NOTE_FIELDS:
        template = col.models.new_field(field)
        col.models.add_field(model, template)

    # Add card template
    template = col.models.new_template("Cloze" if is_cloze else "Card 1")
    card_template = create_card_template(is_cloze, is_reverse=is_reverse)
    template["qfmt"] = card_template["qfmt"]
    template["afmt"] = card_template["afmt"]

    col.models.add_template(model, template)
    col.models.save(model)

    # Automatically register note type if URL was provided
    if url and model.get("id"):
        try:
            register_note_type_for_deck(url, model["id"], model_name, debug_messages)
        except Exception as e:
            if debug_messages:
                debug_messages.append(f"Error registering note type {model['id']}: {e}")

    return model


def ensure_custom_models(col, url, student=None, debug_messages=None):
    """
    Ensures both models (standard and cloze) exist in Anki.
    Uses IDs stored in meta.json to find existing note types,
    instead of searching only by name.

    Args:
        col: Anki collection object
        url (str): Remote deck URL
        student (str, optional): Student name for creating specific models
        debug_messages (list, optional): List for debug

    Returns:
        dict: Dictionary containing 'standard', 'cloze', and 'reverse' models
    """
    from .config_manager import get_deck_note_type_ids
    from .config_manager import get_deck_remote_name
    from .utils import get_note_type_name
    from .utils import register_note_type_for_deck

    def add_debug_msg(message):
        if debug_messages:
            debug_messages.append(f"[ENSURE_MODELS] {message}")

    models = {}

    # Get remote deck name and existing note types
    remote_deck_name = get_deck_remote_name(url) or "RemoteDeck"
    existing_note_types = get_deck_note_type_ids(url) or {}

    add_debug_msg(
        f"Searching note types for student='{student}', remote_deck_name='{remote_deck_name}'"
    )
    add_debug_msg(f"Existing note types: {len(existing_note_types)} found")

    # Helper function to find note type by pattern
    def find_existing_note_type(is_cloze=False, is_reverse=False):
        if is_reverse:
            target_type = "Reverse"
        elif is_cloze:
            target_type = "Cloze"
        else:
            target_type = "Basic"
            
        target_pattern = (
            f" - {student} - {target_type}" if student else f" - {target_type}"
        )

        # Search in existing note types
        for note_type_id_str, note_type_name in existing_note_types.items():
            if note_type_name.endswith(target_pattern):
                try:
                    note_type_id = int(note_type_id_str)
                    from anki.models import NotetypeId
                    model = col.models.get(NotetypeId(note_type_id))
                    if model:
                        add_debug_msg(
                            f"Found existing note type: ID {note_type_id} - '{note_type_name}'"
                        )
                        return model, note_type_name
                except (ValueError, TypeError):
                    continue
        return None, None

    # Standard model (Basic)
    expected_name = get_note_type_name(
        url, remote_deck_name, student=student, is_cloze=False
    )
    existing_model, existing_name = find_existing_note_type(is_cloze=False)

    if existing_model:
        # Use existing model and do NOT force new name if already registered
        current_registered_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_model["id"]:
                    current_registered_name = note_type_name
                    break
            except ValueError:
                continue

        if current_registered_name:
            # Already registered, use current config name
            add_debug_msg(
                f"Using existing (Basic) model ALREADY REGISTERED: '{existing_name}' with config name: '{current_registered_name}'"
            )
            models["standard"] = existing_model
        else:
            # Not registered, register with expected name
            register_note_type_for_deck(
                url, existing_model["id"], expected_name, debug_messages
            )
            models["standard"] = existing_model
            add_debug_msg(
                f"Existing (Basic) model registered: '{existing_name}' → expected: '{expected_name}'"
            )
    else:
        # Create new model only if it really doesn't exist
        add_debug_msg(f"Creating new (Basic) model: '{expected_name}'")
        model = create_model(
            col, expected_name, is_cloze=False, url=url, debug_messages=debug_messages
        )
        models["standard"] = model

    # Cloze model
    expected_cloze_name = get_note_type_name(
        url, remote_deck_name, student=student, is_cloze=True
    )
    existing_cloze_model, existing_cloze_name = find_existing_note_type(is_cloze=True)

    if existing_cloze_model:
        # Use existing model and do NOT force new name if already registered
        current_registered_cloze_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_cloze_model["id"]:
                    current_registered_cloze_name = note_type_name
                    break
            except ValueError:
                continue

        if current_registered_cloze_name:
            # Already registered, use current config name
            add_debug_msg(
                f"Using existing (Cloze) model ALREADY REGISTERED: '{existing_cloze_name}' with config name: '{current_registered_cloze_name}'"
            )
            models["cloze"] = existing_cloze_model
        else:
            # Not registered, register with expected name
            register_note_type_for_deck(
                url, existing_cloze_model["id"], expected_cloze_name, debug_messages
            )
            models["cloze"] = existing_cloze_model
            add_debug_msg(
                f"Existing (Cloze) model registered: '{existing_cloze_name}' → expected: '{expected_cloze_name}'"
            )
    else:
        # Create new model only if it really doesn't exist
        add_debug_msg(f"Creating new (Cloze) model: '{expected_cloze_name}'")
        cloze_model = create_model(
            col,
            expected_cloze_name,
            is_cloze=True,
            url=url,
            debug_messages=debug_messages,
        )
        models["cloze"] = cloze_model

    # Reverse model
    expected_reverse_name = get_note_type_name(
        url, remote_deck_name, student=student, is_cloze=False, is_reverse=True
    )
    existing_reverse_model, existing_reverse_name = find_existing_note_type(is_cloze=False, is_reverse=True)

    if existing_reverse_model:
        # Use existing model and do NOT force new name if already registered
        current_registered_reverse_name = None
        for note_type_id_str, note_type_name in existing_note_types.items():
            try:
                if int(note_type_id_str) == existing_reverse_model["id"]:
                    current_registered_reverse_name = note_type_name
                    break
            except ValueError:
                continue

        if current_registered_reverse_name:
            # Already registered, use current config name
            add_debug_msg(
                f"Using existing (Reverse) model ALREADY REGISTERED: '{existing_reverse_name}' with config name: '{current_registered_reverse_name}'"
            )
            models["reverse"] = existing_reverse_model
        else:
            # Not registered, register with expected name
            register_note_type_for_deck(
                url, existing_reverse_model["id"], expected_reverse_name, debug_messages
            )
            models["reverse"] = existing_reverse_model
            add_debug_msg(
                f"Existing (Reverse) model registered: '{existing_reverse_name}' → expected: '{expected_reverse_name}'"
            )
    else:
        # Create new model only if it really doesn't exist
        add_debug_msg(f"Creating new (Reverse) model: '{expected_reverse_name}'")
        # We use standard template structure (is_cloze=False) for Reverse notes
        # The fields are mapped differently in data_processor.py
        reverse_model = create_model(
            col,
            expected_reverse_name,
            is_cloze=False,
            url=url,
            debug_messages=debug_messages,
            is_reverse=True,
        )
        models["reverse"] = reverse_model

    return models

def update_existing_note_type_templates(col, debug_messages=None):
    """
    Updates templates of all existing Sheets2Anki note types
    to include ALL fields defined in NOTE_FIELDS and ensure templates are up to date.
    
    Args:
        col: Anki collection object
        debug_messages (list, optional): List for debug
    
    Returns:
        int: Number of updated note types
    """
    if debug_messages is None:
        debug_messages = []
    
    updated_count = 0
    
    # Search all note types that start with "Sheets2Anki"
    all_models = col.models.all()
    sheets2anki_models = [
        model for model in all_models 
        if model.get("name", "").startswith("Sheets2Anki")
    ]
    
    debug_messages.append(f"[UPDATE_TEMPLATES] Found {len(sheets2anki_models)} Sheets2Anki note types")
    
    for model in sheets2anki_models:
        try:
            model_name = model.get("name", "")
            is_cloze = model.get("type") == 1
            model_was_updated = False
            
            # 1. Check for missing fields
            # ----------------------------------------------------------------
            existing_field_names = []
            for field in model.get("flds", []):
                # Handle different field formats (dict or object)
                if hasattr(field, 'get'):
                    fname = field.get("name", "")
                elif isinstance(field, dict):
                    fname = field.get("name", "")
                else:
                    fname = getattr(field, 'name', "")
                existing_field_names.append(fname)
            
            # Verify every standard field
            for target_field in NOTE_FIELDS:
                if target_field not in existing_field_names:
                    debug_messages.append(f"[UPDATE_TEMPLATES] Adding missing field '{target_field}' to {model_name}")
                    # Add missing field
                    field_template = col.models.new_field(target_field)
                    col.models.add_field(model, field_template)
                    model_was_updated = True
            
            # 2. Update card templates (HTML/CSS)
            # ----------------------------------------------------------------
            # We force update if we added fields OR if we want to ensure latest HTML structure
            # To be efficient, we generate the current standard template
            new_card_template = create_card_template(is_cloze)
            templates = model.get("tmpls", [])
            
            if templates:
                for i, template in enumerate(templates):
                    # Get current content
                    if hasattr(template, 'get'):
                        current_qfmt = template.get("qfmt", "")
                        current_afmt = template.get("afmt", "")
                    elif isinstance(template, dict):
                        current_qfmt = template.get("qfmt", "")
                        current_afmt = template.get("afmt", "")
                    else:
                        current_qfmt = getattr(template, 'qfmt', "")
                        current_afmt = getattr(template, 'afmt', "")
                    
                    # Check if update is needed (simple string comparison)
                    # This ensures any HTML change in code is propagated
                    needs_template_update = (
                        current_qfmt.strip() != new_card_template["qfmt"].strip() or 
                        current_afmt.strip() != new_card_template["afmt"].strip()
                    )
                    
                    if needs_template_update:
                        # Update template content
                        if hasattr(template, '__setitem__'):
                            template["qfmt"] = new_card_template["qfmt"]
                            template["afmt"] = new_card_template["afmt"]
                        elif isinstance(template, dict):
                            template["qfmt"] = new_card_template["qfmt"]
                            template["afmt"] = new_card_template["afmt"]
                        else:
                            setattr(template, 'qfmt', new_card_template["qfmt"])
                            setattr(template, 'afmt', new_card_template["afmt"])
                        
                        model_was_updated = True
                        debug_messages.append(f"[UPDATE_TEMPLATES] Template {i+1} updated for {model_name}")
            
            # 3. Save changes if anything was modified
            # ----------------------------------------------------------------
            if model_was_updated:
                col.models.save(model)
                updated_count += 1
                debug_messages.append(f"[UPDATE_TEMPLATES] ✅ {model_name} updated successfully")
            else:
                debug_messages.append(f"[UPDATE_TEMPLATES] ⏭️ {model_name} is already up to date")
            
        except Exception as e:
            debug_messages.append(f"[UPDATE_TEMPLATES] ❌ Error processing {model.get('name', 'unknown')}: {e}")
            import traceback
            debug_messages.append(traceback.format_exc())
    
    debug_messages.append(f"[UPDATE_TEMPLATES] 🎯 Total note types updated: {updated_count}")
    return updated_count
