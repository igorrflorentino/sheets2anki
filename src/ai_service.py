"""
AI Service Module for Sheets2Anki.

This module provides integration with multiple AI providers:
- Google Gemini
- Anthropic Claude
- OpenAI GPT

Features:
- Unified API for all providers
- Model listing for each provider
- Thread-safe API calls
- Error handling with user-friendly messages
- Token usage and cost tracking
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import List, Dict, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, Future


# =============================================================================
# CONSTANTS
# =============================================================================

# API Endpoints
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
CLAUDE_API_BASE = "https://api.anthropic.com/v1"
OPENAI_API_BASE = "https://api.openai.com/v1"

# Default timeout in seconds
DEFAULT_TIMEOUT = 30

# Default max tokens for AI responses
DEFAULT_MAX_TOKENS = 4096

# Thread pool for async API calls
_executor = ThreadPoolExecutor(max_workers=2)

# Pricing per 1M tokens (as of Jan 2024, approximate)
# Format: {model_prefix: (input_cost_per_1m, output_cost_per_1m)}
PRICING = {
    # Gemini pricing
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-pro": (0.50, 1.50),
    # Claude pricing  
    "claude-sonnet-4": (3.00, 15.00),
    "claude-3-5-sonnet": (3.00, 15.00),
    "claude-3-5-haiku": (0.80, 4.00),
    "claude-3-opus": (15.00, 75.00),
    "claude-3-haiku": (0.25, 1.25),
    # OpenAI pricing
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "o1": (15.00, 60.00),
    "o1-mini": (3.00, 12.00),
}

def get_pricing(model: str) -> Tuple[float, float]:
    """Get pricing for a model (input, output) per 1M tokens."""
    model_lower = model.lower()
    for prefix, pricing in PRICING.items():
        if prefix in model_lower:
            return pricing
    # Default fallback pricing
    return (1.00, 3.00)


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost in USD for token usage."""
    input_price, output_price = get_pricing(model)
    cost = (input_tokens * input_price / 1_000_000) + (output_tokens * output_price / 1_000_000)
    return cost


# =============================================================================
# PROVIDER IMPLEMENTATIONS
# =============================================================================


class AIProvider:
    """Base class for AI providers."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def get_models(self) -> List[Dict[str, str]]:
        """Returns list of available models."""
        raise NotImplementedError
    
    def call_api(self, model: str, prompt: str) -> Dict:
        """
        Calls the API with the given prompt.
        
        Returns:
            Dict with keys: 'text', 'input_tokens', 'output_tokens', 'cost'
        """
        raise NotImplementedError
    
    def _make_request(self, url: str, headers: Dict, data: Optional[Dict] = None, 
                      method: str = "GET") -> Dict:
        """Makes an HTTP request and returns JSON response."""
        try:
            if data:
                data_bytes = json.dumps(data).encode('utf-8')
            else:
                data_bytes = None
            
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
            
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
                return json.loads(response.read().decode('utf-8'))
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else str(e)
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', error_body)
            except json.JSONDecodeError:
                error_msg = error_body
            raise AIServiceError(f"API Error ({e.code}): {error_msg}")
        except urllib.error.URLError as e:
            raise AIServiceError(f"Connection error: {e.reason}")
        except Exception as e:
            raise AIServiceError(f"Request failed: {str(e)}")


class GeminiProvider(AIProvider):
    """Google Gemini API provider."""
    
    def get_models(self) -> List[Dict[str, str]]:
        """Returns list of available Gemini models."""
        url = f"{GEMINI_API_BASE}/models?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        response = self._make_request(url, headers)
        
        models = []
        for model in response.get("models", []):
            name = model.get("name", "")
            # Extract model ID from full path (e.g., "models/gemini-pro" -> "gemini-pro")
            model_id = name.replace("models/", "") if name.startswith("models/") else name
            display_name = model.get("displayName", model_id)
            
            # Only include models that support generateContent
            supported_methods = model.get("supportedGenerationMethods", [])
            if "generateContent" in supported_methods:
                models.append({
                    "id": model_id,
                    "name": display_name
                })
        
        return models
    
    def call_api(self, model: str, prompt: str) -> Dict:
        """Calls Gemini API with the given prompt."""
        url = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": DEFAULT_MAX_TOKENS,
            }
        }
        
        response = self._make_request(url, headers, data, method="POST")
        
        # Extract text and usage from response
        try:
            text = ""
            candidates = response.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    text = parts[0].get("text", "")
            
            # Extract token usage
            usage = response.get("usageMetadata", {})
            input_tokens = usage.get("promptTokenCount", 0)
            output_tokens = usage.get("candidatesTokenCount", 0)
            
            cost = calculate_cost(model, input_tokens, output_tokens)
            
            return {
                "text": text or "No response generated.",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost
            }
        except (KeyError, IndexError) as e:
            raise AIServiceError(f"Failed to parse Gemini response: {e}")


class ClaudeProvider(AIProvider):
    """Anthropic Claude API provider."""
    
    def get_models(self) -> List[Dict[str, str]]:
        """Returns list of available Claude models."""
        # Claude doesn't have a public models endpoint, so we return known models
        return [
            {"id": "claude-sonnet-4-20250514", "name": "Claude Sonnet 4 (Latest)"},
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
        ]
    
    def call_api(self, model: str, prompt: str) -> Dict:
        """Calls Claude API with the given prompt."""
        url = f"{CLAUDE_API_BASE}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = self._make_request(url, headers, data, method="POST")
        
        # Extract text and usage from response
        try:
            text = ""
            content = response.get("content", [])
            if content:
                text = content[0].get("text", "")
            
            # Extract token usage
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            
            cost = calculate_cost(model, input_tokens, output_tokens)
            
            return {
                "text": text or "No response generated.",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost
            }
        except (KeyError, IndexError) as e:
            raise AIServiceError(f"Failed to parse Claude response: {e}")


class OpenAIProvider(AIProvider):
    """OpenAI GPT API provider."""
    
    def get_models(self) -> List[Dict[str, str]]:
        """Returns list of available OpenAI models."""
        url = f"{OPENAI_API_BASE}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = self._make_request(url, headers)
        
        models = []
        for model in response.get("data", []):
            model_id = model.get("id", "")
            # Filter to only include chat models
            if any(prefix in model_id for prefix in ["gpt-4", "gpt-3.5", "o1", "o3"]):
                models.append({
                    "id": model_id,
                    "name": model_id
                })
        
        # Sort by name for better UX
        models.sort(key=lambda x: x["name"], reverse=True)
        return models
    
    def call_api(self, model: str, prompt: str) -> Dict:
        """Calls OpenAI API with the given prompt."""
        url = f"{OPENAI_API_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": DEFAULT_MAX_TOKENS,
            "temperature": 0.7
        }
        
        response = self._make_request(url, headers, data, method="POST")
        
        # Extract text and usage from response
        try:
            text = ""
            choices = response.get("choices", [])
            if choices:
                message = choices[0].get("message", {})
                text = message.get("content", "")
            
            # Extract token usage
            usage = response.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            cost = calculate_cost(model, input_tokens, output_tokens)
            
            return {
                "text": text or "No response generated.",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost
            }
        except (KeyError, IndexError) as e:
            raise AIServiceError(f"Failed to parse OpenAI response: {e}")


# =============================================================================
# EXCEPTIONS
# =============================================================================


class AIServiceError(Exception):
    """Custom exception for AI service errors."""
    pass


# =============================================================================
# PUBLIC API
# =============================================================================


def get_provider(service: str, api_key: str) -> AIProvider:
    """
    Factory function to get the appropriate AI provider.
    
    Args:
        service: Service name (gemini, claude, openai)
        api_key: API key for the service
    
    Returns:
        AIProvider instance
    
    Raises:
        ValueError: If service is not recognized
    """
    providers = {
        "gemini": GeminiProvider,
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
    }
    
    if service not in providers:
        raise ValueError(f"Unknown service: {service}. Valid options: {list(providers.keys())}")
    
    return providers[service](api_key)


def get_available_models(service: str, api_key: str) -> List[Dict[str, str]]:
    """
    Gets available models for a specific AI service.
    
    Args:
        service: Service name (gemini, claude, openai)
        api_key: API key for the service
    
    Returns:
        List of dicts with 'id' and 'name' keys
    
    Raises:
        AIServiceError: If there's an API error
        ValueError: If service is not recognized
    """
    provider = get_provider(service, api_key)
    return provider.get_models()


def call_ai_api(service: str, model: str, api_key: str, prompt: str, 
                card_content: str) -> Dict:
    """
    Calls an AI API with the card content.
    
    Args:
        service: Service name (gemini, claude, openai)
        model: Model ID to use
        api_key: API key for the service
        prompt: Prompt template (should contain {card_content} placeholder)
        card_content: The actual card content to analyze
    
    Returns:
        Dict with keys: 'text', 'input_tokens', 'output_tokens', 'cost'
    
    Raises:
        AIServiceError: If there's an API error
        ValueError: If service is not recognized
    """
    # Build final prompt by replacing placeholder
    if "{card_content}" in prompt:
        final_prompt = prompt.replace("{card_content}", card_content)
    else:
        # If no placeholder, append card content
        final_prompt = f"{prompt}\n\n{card_content}"
    
    provider = get_provider(service, api_key)
    return provider.call_api(model, final_prompt)


def call_ai_api_async(service: str, model: str, api_key: str, prompt: str,
                      card_content: str, callback: Callable[[Dict, Optional[Exception]], None]) -> Future:
    """
    Calls an AI API asynchronously.
    
    Args:
        service: Service name (gemini, claude, openai)
        model: Model ID to use
        api_key: API key for the service
        prompt: Prompt template (should contain {card_content} placeholder)
        card_content: The actual card content to analyze
        callback: Function to call with (result_dict, error) when complete
    
    Returns:
        Future object for the async operation
    """
    def run_and_callback():
        try:
            result = call_ai_api(service, model, api_key, prompt, card_content)
            callback(result, None)
        except Exception as e:
            callback({}, e)
    
    return _executor.submit(run_and_callback)


def validate_api_key(service: str, api_key: str) -> bool:
    """
    Validates an API key by attempting to fetch models.
    
    Args:
        service: Service name (gemini, claude, openai)
        api_key: API key to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        models = get_available_models(service, api_key)
        return len(models) > 0
    except Exception:
        return False
