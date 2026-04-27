

// Decode Base64-encoded prompts to prevent HTML parser corruption
function _b64decode(str) {
  try {
    return decodeURIComponent(Array.prototype.map.call(
      atob(str), function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }
    ).join(''));
  } catch(e) {
    return atob(str);
  }
}

// AI Help Config (embedded for mobile support)
var AI_CONFIG = {
  service: "gemini",
  model: "flash",
  apiKey: "123",
  prompt_help: _b64decode("aA=="),
  prompt_ask: _b64decode("YQ=="),
  prompt_checker: _b64decode("Yw==")
};

// Pricing per 1M tokens
var PRICING = {
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
  'gpt-3.5-turbo': [0.50, 1.50],
  'o1': [15.00, 60.00],
  'o1-mini': [3.00, 12.00]
};

function getPricing(model) {
  model = model.toLowerCase();
  for (var prefix in PRICING) {
    if (model.indexOf(prefix) !== -1) return PRICING[prefix];
  }
  return [1.00, 3.00];
}

function calculateCost(model, inputTokens, outputTokens) {
  var p = getPricing(model);
  return (inputTokens * p[0] / 1000000) + (outputTokens * p[1] / 1000000);
}

function requestAIHelp() {
  var btn = document.getElementById('ai-help-btn');
  if (!btn || btn.classList.contains('loading')) return;
  
  btn.classList.add('loading');
  window._aiModalTitle = '🤖 AI Help';
  var cardContent = collectCardContent();
  
  // Try desktop first
  if (typeof pycmd !== 'undefined') {
    pycmd('sheets2anki_ai_help:' + encodeURIComponent(cardContent));
    return;
  }
  
  // Mobile: direct API call
  callAIAPI(cardContent);
}

function requestAIChecker() {
  var btn = document.getElementById('ai-checker-btn');
  if (!btn || btn.classList.contains('loading')) return;
  
  btn.classList.add('loading');
  window._aiModalTitle = '🔍 AI Checker';
  var cardContent = collectCardContent();
  
  // Try desktop first
  if (typeof pycmd !== 'undefined') {
    pycmd('sheets2anki_ai_checker:' + encodeURIComponent(cardContent));
    return;
  }
  
  // Mobile: direct API call with checker prompt
  callAICheckerAPI(cardContent);
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
  
  // Try desktop first
  if (typeof pycmd !== 'undefined') {
    pycmd('sheets2anki_ai_ask:' + encodeURIComponent(question) + '|||' + encodeURIComponent(cardContent));
    return;
  }
  
  // Mobile: direct API call with custom question
  callAIAskAPI(question, cardContent);
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

function _replacePromptPlaceholder(promptTemplate, placeholder, value) {
  // Handles both {placeholder} and {placeholder} forms
  var regex = new RegExp('\{\{' + placeholder + '\}\}|\{' + placeholder + '\}', 'g');
  var testRegex = new RegExp('\{\{' + placeholder + '\}\}|\{' + placeholder + '\}');
  var hadPlaceholder = testRegex.test(promptTemplate);
  var result = promptTemplate.replace(regex, value);
  return { text: result, had: hadPlaceholder };
}

function callAIAskAPI(question, cardContent) {
  var promptTemplate = AI_CONFIG.prompt_ask;
  
  // Replace {card_content} placeholder with fallback
  var r1 = _replacePromptPlaceholder(promptTemplate, 'card_content', cardContent);
  var prompt = r1.text;
  if (!r1.had) {
    prompt = prompt + '\n\n' + cardContent;
  }
  
  // Replace {question} placeholder with fallback
  var r2 = _replacePromptPlaceholder(prompt, 'question', question);
  prompt = r2.text;
  if (!r2.had) {
    prompt = prompt + '\n\nQuestion: ' + question;
  }
  
  if (AI_CONFIG.service === 'gemini') {
    callGeminiAPI(prompt);
  } else if (AI_CONFIG.service === 'claude') {
    callClaudeAPI(prompt);
  } else if (AI_CONFIG.service === 'openai') {
    callOpenAIAPI(prompt);
  }
}

function callAIAPI(cardContent) {
  var promptTemplate = AI_CONFIG.prompt_help;
  var r = _replacePromptPlaceholder(promptTemplate, 'card_content', cardContent);
  var prompt = r.text;
  if (!r.had) {
    prompt = prompt + '\n\n' + cardContent;
  }
  
  if (AI_CONFIG.service === 'gemini') {
    callGeminiAPI(prompt);
  } else if (AI_CONFIG.service === 'claude') {
    callClaudeAPI(prompt);
  } else if (AI_CONFIG.service === 'openai') {
    callOpenAIAPI(prompt);
  }
}

function callAICheckerAPI(cardContent) {
  var checkerTemplate = AI_CONFIG.prompt_checker;
  var r = _replacePromptPlaceholder(checkerTemplate, 'card_content', cardContent);
  var prompt = r.text;
  if (!r.had) {
    prompt = prompt + '\n\n' + cardContent;
  }
  
  if (AI_CONFIG.service === 'gemini') {
    callGeminiAPI(prompt);
  } else if (AI_CONFIG.service === 'claude') {
    callClaudeAPI(prompt);
  } else if (AI_CONFIG.service === 'openai') {
    callOpenAIAPI(prompt);
  }
}

function callGeminiAPI(prompt) {
  var url = 'https://generativelanguage.googleapis.com/v1beta/models/' + AI_CONFIG.model + ':generateContent?key=' + AI_CONFIG.apiKey;
  
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.7, maxOutputTokens: 4096 }
    })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) {
      showAIHelpError(data.error.message || 'API Error');
      return;
    }
    var text = '';
    try {
      text = data.candidates[0].content.parts[0].text;
    } catch(e) {
      text = 'No response generated';
    }
    var usage = data.usageMetadata || {};
    var inputTokens = usage.promptTokenCount || 0;
    var outputTokens = usage.candidatesTokenCount || 0;
    showAIHelpResponse(text, {
      input_tokens: inputTokens,
      output_tokens: outputTokens,
      cost: calculateCost(AI_CONFIG.model, inputTokens, outputTokens)
    });
  })
  .catch(function(e) { showAIHelpError('Request failed: ' + e.message); });
}

function callClaudeAPI(prompt) {
  // Note: Claude API may have CORS restrictions from browser
  var url = 'https://api.anthropic.com/v1/messages';
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': AI_CONFIG.apiKey,
      'anthropic-version': '2023-06-01',
      'anthropic-dangerous-direct-browser-access': 'true'
    },
    body: JSON.stringify({
      model: AI_CONFIG.model,
      max_tokens: 4096,
      messages: [{ role: 'user', content: prompt }]
    })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) {
      showAIHelpError(data.error.message || 'API Error');
      return;
    }
    var text = data.content && data.content[0] ? data.content[0].text : 'No response';
    var usage = data.usage || {};
    showAIHelpResponse(text, {
      input_tokens: usage.input_tokens || 0,
      output_tokens: usage.output_tokens || 0,
      cost: calculateCost(AI_CONFIG.model, usage.input_tokens || 0, usage.output_tokens || 0)
    });
  })
  .catch(function(e) { showAIHelpError('Request failed: ' + e.message); });
}

function callOpenAIAPI(prompt) {
  var url = 'https://api.openai.com/v1/chat/completions';
  
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + AI_CONFIG.apiKey
    },
    body: JSON.stringify({
      model: AI_CONFIG.model,
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 4096,
      temperature: 0.7
    })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) {
      showAIHelpError(data.error.message || 'API Error');
      return;
    }
    var text = data.choices && data.choices[0] ? data.choices[0].message.content : 'No response';
    var usage = data.usage || {};
    showAIHelpResponse(text, {
      input_tokens: usage.prompt_tokens || 0,
      output_tokens: usage.completion_tokens || 0,
      cost: calculateCost(AI_CONFIG.model, usage.prompt_tokens || 0, usage.completion_tokens || 0)
    });
  })
  .catch(function(e) { showAIHelpError('Request failed: ' + e.message); });
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
  
  // Inline math $ ... $ -> \( ... \)
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
  
  // On mobile (no pycmd), show inline; on desktop, use modal
  if (typeof pycmd === 'undefined') {
    var inline = document.getElementById('ai-help-inline');
    if (inline) {
      var titleHtml = window._aiModalTitle ? '<h3>' + window._aiModalTitle + '</h3>' : '';
      inline.innerHTML = titleHtml + html;
      inline.classList.add('show');
    }
  } else {
    var modal = document.getElementById('ai-help-modal');
    var body = document.getElementById('ai-help-modal-body');
    if (!modal || !body) return;
    var titleEl = document.querySelector('.ai-help-modal-title');
    if (titleEl && window._aiModalTitle) titleEl.textContent = window._aiModalTitle;
    body.innerHTML = html;
    modal.classList.add('show');
  }
  
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
  
  var errorHtml = '<div class="ai-help-error">⚠️ ' + error + '</div>';
  
  // On mobile (no pycmd), show inline; on desktop, use modal
  if (typeof pycmd === 'undefined') {
    var inline = document.getElementById('ai-help-inline');
    if (inline) {
      var titleHtml = window._aiModalTitle ? '<h3>' + window._aiModalTitle + '</h3>' : '';
      inline.innerHTML = titleHtml + errorHtml;
      inline.classList.add('show');
    }
  } else {
    var modal = document.getElementById('ai-help-modal');
    var body = document.getElementById('ai-help-modal-body');
    if (!modal || !body) return;
    var titleEl = document.querySelector('.ai-help-modal-title');
    if (titleEl && window._aiModalTitle) titleEl.textContent = window._aiModalTitle;
    body.innerHTML = errorHtml;
    modal.classList.add('show');
  }
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

