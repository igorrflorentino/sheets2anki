

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
  window._aiModalTitle = '🤖 AI Help';
  var cardContent = collectCardContent();
  
  if (typeof pycmd !== 'undefined') {
    pycmd('sheets2anki_ai_help:' + encodeURIComponent(cardContent));
  } else {
    btn.classList.remove('loading');
  }
}

function requestAIChecker() {
  var btn = document.getElementById('ai-checker-btn');
  if (!btn || btn.classList.contains('loading')) return;
  
  btn.classList.add('loading');
  window._aiModalTitle = '🔍 AI Checker';
  var cardContent = collectCardContent();
  
  if (typeof pycmd !== 'undefined') {
    pycmd('sheets2anki_ai_checker:' + encodeURIComponent(cardContent));
  } else {
    btn.classList.remove('loading');
  }
}

function openAIAskInput() {
  var modal = document.getElementById('ai-ask-input-modal');
  if (modal) {
    modal.classList.add('show');
    var textarea = document.getElementById('ai-ask-textarea');
    if (textarea) {
      textarea.value = '';
      textarea.focus();
    }
  }
}

function closeAIAskInput(event) {
  if (event && event.target !== event.currentTarget) return;
  var modal = document.getElementById('ai-ask-input-modal');
  if (modal) modal.classList.remove('show');
}

function submitAIAsk() {
  var submitBtn = document.querySelector('.ai-ask-submit');
  if (submitBtn && submitBtn.classList.contains('loading')) return;
  
  var textarea = document.getElementById('ai-ask-textarea');
  var question = textarea ? textarea.value.trim() : '';
  if (!question) return;
  
  var btn = document.getElementById('ai-ask-btn');
  if (btn) btn.classList.add('loading');
  window._aiModalTitle = '💬 AI Ask';
  
  if (submitBtn) {
    submitBtn.classList.add('loading');
    submitBtn.innerHTML = 'Sending... ⏳';
  }
  if (textarea) textarea.disabled = true;
  
  var cardContent = collectCardContent();
  
  if (typeof pycmd !== 'undefined') {
    pycmd('sheets2anki_ai_ask:' + encodeURIComponent(question) + '|||' + encodeURIComponent(cardContent));
  } else {
    resetAIAskInput();
  }
}

function resetAIAskInput() {
  var submitBtn = document.querySelector('.ai-ask-submit');
  if (submitBtn) {
    submitBtn.classList.remove('loading');
    submitBtn.innerHTML = 'Send Question';
  }
  var textarea = document.getElementById('ai-ask-textarea');
  if (textarea) textarea.disabled = false;
  closeAIAskInput();
}



// Capture the original card content ONCE on page load, before any AI response is injected.
// This prevents AI responses from contaminating subsequent AI requests.
(function() {
  function captureOriginalContent() {
    if (!window._originalCardContent) {
      var allText = document.body.innerText || document.body.textContent;
      window._originalCardContent = allText.trim();
    }
  }
  // Capture immediately (for cases where DOM is already ready)
  captureOriginalContent();
  // Also capture on DOMContentLoaded (fallback for early script execution)
  document.addEventListener('DOMContentLoaded', captureOriginalContent);
})();

function collectCardContent() {
  // Always return the original card content snapshot, never re-read the DOM
  return window._originalCardContent || '';
}


function processMathAndMarkdown(text) {
  var mathBlocks = [];
  var placeholder = "MATHBLOCK";
  var suffix = "END";
  
  // Display math $$ ... $$ -> \[ ... \]
  text = text.replace(/\$\$([\s\S]*?)\$\$/g, function(match, content) {
    var id = mathBlocks.length;
    mathBlocks.push('\\[' + content + '\\]');
    return placeholder + id + suffix;
  });
  
  // Inline math $ ... $ -> \( ... \) (Disallow newlines)
  text = text.replace(/([^\\$]|^)\$([^\s$\n](?:[^$\n]*?[^\s$\n])?)\$(?!\d)/g, function(match, prefix, content) {
    var id = mathBlocks.length;
    mathBlocks.push('\\(' + content + '\\)');
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
  var askBtn = document.getElementById('ai-ask-btn');
  if (askBtn) askBtn.classList.remove('loading');
  var checkerBtn = document.getElementById('ai-checker-btn');
  if (checkerBtn) checkerBtn.classList.remove('loading');
  
  if (typeof resetAIAskInput === 'function') resetAIAskInput();
  
  var modal = document.getElementById('ai-help-modal');
  var body = document.getElementById('ai-help-modal-body');
  if (!modal || !body) return;
  var titleEl = document.querySelector('.ai-help-modal-title');
  if (titleEl && window._aiModalTitle) titleEl.textContent = window._aiModalTitle;
  
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
  var askBtn = document.getElementById('ai-ask-btn');
  if (askBtn) askBtn.classList.remove('loading');
  var checkerBtn = document.getElementById('ai-checker-btn');
  if (checkerBtn) checkerBtn.classList.remove('loading');
  
  if (typeof resetAIAskInput === 'function') resetAIAskInput();
  
  var modal = document.getElementById('ai-help-modal');
  var body = document.getElementById('ai-help-modal-body');
  if (!modal || !body) return;
  body.innerHTML = '<div class="ai-help-error">⚠️ ' + error + '</div>';
  modal.classList.add('show');
}

function closeAIHelpModal(event) {
  if (event && event.target !== event.currentTarget) return;
  var modal = document.getElementById('ai-help-modal');
  if (modal) modal.classList.remove('show');
}

if (typeof globalThis !== 'undefined') {
  globalThis.sheets2ankiAIResponse = function(response, usageInfo) {
    showAIHelpResponse(response, usageInfo);
  };
  globalThis.sheets2ankiAIError = function(error) {
    showAIHelpError(error);
  };
}

