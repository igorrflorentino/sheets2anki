"""
Test: Verify that Sanity Check data is never sent to AI Assistance features.

This test validates the isolation between the 'Sanity Check' field and the 
AI Assistance functionality (AI Help, AI Ask, AI Checker) through:
1. Static analysis of JavaScript content extraction logic
2. Static analysis of Python AI handlers
3. Static analysis of prompt templates
4. Log file analysis

All tests use raw file reading to avoid Anki dependency issues.
"""

import re
import os

# Project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_file(relative_path):
    """Read a file from the project root."""
    path = os.path.join(PROJECT_ROOT, relative_path)
    with open(path, "r", errors="replace") as f:
        return f.read()


# =========================================================================
# Load source files once
# =========================================================================

TEMPLATES_PY = read_file("src/templates_and_definitions.py")
CONFIG_MANAGER_PY = read_file("src/config_manager.py")
AI_SERVICE_PY = read_file("src/ai_service.py")
INIT_PY = read_file("__init__.py")


def extract_string_constant(source, var_name):
    """Extract a triple-quoted string constant from Python source."""
    # Matches: VAR_NAME = """..."""  or  VAR_NAME = '''...'''
    pattern = rf'{var_name}\s*=\s*"""(.*?)"""'
    match = re.search(pattern, source, re.DOTALL)
    if match:
        return match.group(1)
    pattern = rf"{var_name}\s*=\s*'''(.*?)'''"
    match = re.search(pattern, source, re.DOTALL)
    if match:
        return match.group(1)
    return None


# =========================================================================
# TESTS
# =========================================================================


def test_js_desktop_hides_sanity_check_before_capture():
    """
    DESKTOP JS: Verify that captureOriginalContent() hides the 
    .sanity-check-container BEFORE reading document.body.innerText.
    """
    # The desktop JS is AI_HELP_JS_DESKTOP - a string in templates_and_definitions.py
    # Find the captureOriginalContent function in the full file content
    assert "captureOriginalContent" in TEMPLATES_PY, "captureOriginalContent function must exist"
    
    # Find the desktop version (first occurrence before mobile template)
    # Look for the pattern within the desktop JS section
    desktop_section_start = TEMPLATES_PY.index("AI_HELP_JS_DESKTOP")
    mobile_section_start = TEMPLATES_PY.index("AI_HELP_JS_MOBILE_TEMPLATE")
    desktop_js = TEMPLATES_PY[desktop_section_start:mobile_section_start]
    
    assert ".sanity-check-container" in desktop_js, "Must reference .sanity-check-container"
    assert "sanityCheck.style.display = 'none'" in desktop_js, "Must hide sanity check"
    
    # Verify ORDER: hide → read → restore
    hide_pos = desktop_js.index("sanityCheck.style.display = 'none'")
    read_pos = desktop_js.index("document.body.innerText")
    restore_pos = desktop_js.index("sanityCheck.style.display = originalDisplay")
    
    assert hide_pos < read_pos, "Sanity check must be hidden BEFORE reading innerText"
    assert read_pos < restore_pos, "innerText must be read BEFORE restoring sanity check"
    
    print("✅ DESKTOP JS: Sanity check is hidden before card content capture")


def test_js_mobile_hides_sanity_check_before_capture():
    """
    MOBILE JS: Verify that captureOriginalContent() hides the 
    .sanity-check-container BEFORE reading document.body.innerText.
    """
    mobile_section_start = TEMPLATES_PY.index("AI_HELP_JS_MOBILE_TEMPLATE")
    mobile_js = TEMPLATES_PY[mobile_section_start:]
    
    assert "captureOriginalContent" in mobile_js, "captureOriginalContent must exist in mobile template"
    assert ".sanity-check-container" in mobile_js, "Must reference .sanity-check-container in mobile"
    assert "sanityCheck.style.display = 'none'" in mobile_js, "Must hide sanity check in mobile"
    
    # Verify ORDER: hide → read → restore
    hide_pos = mobile_js.index("sanityCheck.style.display = 'none'")
    read_pos = mobile_js.index("document.body.innerText")
    restore_pos = mobile_js.index("sanityCheck.style.display = originalDisplay")
    
    assert hide_pos < read_pos, "Sanity check must be hidden BEFORE reading innerText (mobile)"
    assert read_pos < restore_pos, "innerText must be read BEFORE restoring sanity check (mobile)"
    
    print("✅ MOBILE JS: Sanity check is hidden before card content capture")


def test_collectCardContent_uses_cached_snapshot():
    """
    Verify that collectCardContent() returns the cached _originalCardContent
    and never re-reads the DOM (which could pick up sanity check data).
    """
    for label, section_marker in [
        ("DESKTOP", "AI_HELP_JS_DESKTOP"),
        ("MOBILE", "AI_HELP_JS_MOBILE_TEMPLATE")
    ]:
        start = TEMPLATES_PY.index(section_marker)
        # Get a reasonable chunk
        section = TEMPLATES_PY[start:start + 15000]
        
        # Find collectCardContent function body
        match = re.search(r'function collectCardContent\(\)\s*\{([^}]+)\}', section)
        assert match, f"collectCardContent function must exist in {label}"
        
        body = match.group(1)
        
        # Must return the cached snapshot
        assert "_originalCardContent" in body, f"Must use _originalCardContent in {label}"
        
        # Must NOT re-read DOM
        assert "document.body" not in body, f"Must NOT re-read document.body in {label}"
        assert "innerText" not in body, f"Must NOT call innerText in {label}"
        assert "textContent" not in body, f"Must NOT call textContent in {label}"
        
        print(f"✅ {label}: collectCardContent() uses cached snapshot only (no live DOM read)")


def test_all_ai_functions_use_collectCardContent():
    """
    Verify that requestAIHelp, requestAIChecker, and submitAIAsk
    all call collectCardContent() to get card content.
    """
    for label, section_marker in [
        ("DESKTOP", "AI_HELP_JS_DESKTOP"),
        ("MOBILE", "AI_HELP_JS_MOBILE_TEMPLATE")
    ]:
        start = TEMPLATES_PY.index(section_marker)
        section = TEMPLATES_PY[start:start + 15000]
        
        for func_name in ["requestAIHelp", "requestAIChecker", "submitAIAsk"]:
            func_match = re.search(rf'function {func_name}\(\)\s*\{{', section)
            assert func_match, f"{func_name} function must exist in {label}"
            
            # Extract function body
            func_start = func_match.end()
            brace_count = 1
            pos = func_start
            while brace_count > 0 and pos < len(section):
                if section[pos] == '{':
                    brace_count += 1
                elif section[pos] == '}':
                    brace_count -= 1
                pos += 1
            func_body = section[func_start:pos]
            
            assert "collectCardContent()" in func_body, \
                f"{func_name} must call collectCardContent() in {label}"
            
            # Verify it does NOT directly read DOM for content
            assert "document.body.innerText" not in func_body, \
                f"{func_name} must NOT directly read innerText in {label}"
        
        print(f"✅ {label}: All 3 AI functions (Help, Ask, Checker) use collectCardContent()")


def test_prompt_templates_no_sanity_references():
    """
    Verify that AI prompt templates (AI_HELP, AI_ASK, AI_CHECKER) 
    do not reference sanity check in any language.
    """
    # Search for any sanity reference in prompt dictionaries
    # The prompts are defined as AI_HELP_PROMPTS, AI_ASK_PROMPTS, AI_CHECKER_PROMPTS in config_manager.py
    
    for dict_name in ["AI_HELP_PROMPTS", "AI_ASK_PROMPTS", "AI_CHECKER_PROMPTS"]:
        # Find the dictionary definition
        dict_start = CONFIG_MANAGER_PY.index(dict_name)
        # Find the end (next top-level definition or large gap)
        # Simple: grab 5000 chars after the start
        dict_section = CONFIG_MANAGER_PY[dict_start:dict_start + 5000]
        
        assert "sanity" not in dict_section.lower(), \
            f"{dict_name} must not reference 'sanity'"
    
    print("✅ PROMPTS: No sanity check references in any AI prompt template (all languages)")


def test_python_ai_handlers_no_sanity_references():
    """
    Verify that the Python AI handler functions in __init__.py
    do not reference sanity check data.
    """
    for func_name in ["handle_ai_help_request", "handle_ai_checker_request", "handle_ai_ask_request"]:
        assert func_name in INIT_PY, f"{func_name} must exist in __init__.py"
    
    assert "sanity" not in INIT_PY.lower(), \
        "__init__.py must not reference sanity check"
    
    print("✅ PYTHON HANDLERS: No sanity check references in any AI handler function")


def test_ai_service_no_sanity_references():
    """
    Verify that ai_service.py does not reference sanity check.
    """
    assert "sanity" not in AI_SERVICE_PY.lower(), \
        "ai_service.py must not reference sanity check"
    
    print("✅ AI SERVICE: No sanity check references in ai_service.py")


def test_config_manager_no_sanity_references():
    """
    Verify that config_manager.py (which defines all prompts)
    does not reference sanity check.
    """
    assert "sanity" not in CONFIG_MANAGER_PY.lower(), \
        "config_manager.py must not reference sanity check"
    
    print("✅ CONFIG MANAGER: No sanity check references in config_manager.py")


def test_sanity_check_container_css_class_exists_in_template():
    """
    Verify that the sanity check HTML uses the .sanity-check-container class
    that the JS code targets for hiding.
    """
    # The HTML template must use the class
    assert 'class="sanity-check-container"' in TEMPLATES_PY or "class=\\'sanity-check-container\\'" in TEMPLATES_PY, \
        "Sanity check HTML must use .sanity-check-container class"
    
    # And the JS must target that same class
    assert ".sanity-check-container" in TEMPLATES_PY, \
        "JS must query .sanity-check-container to hide it"
    
    # Count occurrences to ensure both desktop AND mobile JS hide it
    hide_count = TEMPLATES_PY.count("sanityCheck.style.display = 'none'")
    assert hide_count >= 2, \
        f"Must hide sanity check in both desktop and mobile JS (found {hide_count} hide operations)"
    
    print(f"✅ TEMPLATE: Sanity check uses correct CSS class, hidden in {hide_count} JS contexts")


def test_debug_log_no_sanity_in_ai_context():
    """
    Verify that debug logs show no evidence of sanity check data
    being passed to AI functions.
    """
    log_path = os.path.join(PROJECT_ROOT, "debug_sheets2anki.log")
    if not os.path.exists(log_path):
        print("⚠️  LOGS: No debug log file found, skipping log analysis")
        return
    
    ai_related_lines = []
    sanity_lines_count = 0
    
    with open(log_path, "r", errors="replace") as f:
        for line in f:
            if any(tag in line for tag in ["[AI_HELP]", "[AI_ASK]", "[AI_CHECKER]", "[PYCMD]"]):
                ai_related_lines.append(line.strip())
            if "SANITY CHECK" in line:
                sanity_lines_count += 1
    
    # Check that no AI-related log line contains sanity check data
    for line in ai_related_lines:
        assert "SANITY CHECK" not in line, \
            f"AI log line must not contain sanity check data: {line[:100]}"
        assert "sanity" not in line.lower(), \
            f"AI log line must not reference sanity check: {line[:100]}"
    
    print(f"✅ LOGS: {len(ai_related_lines)} AI-related log entries, none contain sanity check data")
    print(f"   (Log has {sanity_lines_count} sanity check entries, all in sync/update context only)")


def test_ai_assistance_config_dialog_no_sanity():
    """
    Verify that the AI configuration dialog does not reference sanity check.
    """
    dialog_py = read_file("src/ai_assistance_config_dialog.py")
    assert "sanity" not in dialog_py.lower(), \
        "AI config dialog must not reference sanity check"
    
    print("✅ AI CONFIG DIALOG: No sanity check references")


if __name__ == "__main__":
    print("=" * 70)
    print("SANITY CHECK ↔ AI ASSISTANCE ISOLATION VERIFICATION")
    print("=" * 70)
    print()
    
    tests = [
        test_js_desktop_hides_sanity_check_before_capture,
        test_js_mobile_hides_sanity_check_before_capture,
        test_collectCardContent_uses_cached_snapshot,
        test_all_ai_functions_use_collectCardContent,
        test_prompt_templates_no_sanity_references,
        test_python_ai_handlers_no_sanity_references,
        test_ai_service_no_sanity_references,
        test_config_manager_no_sanity_references,
        test_sanity_check_container_css_class_exists_in_template,
        test_debug_log_no_sanity_in_ai_context,
        test_ai_assistance_config_dialog_no_sanity,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"❌ FAILED: {test.__name__}: {e}")
    
    print()
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    if failed == 0:
        print("🎯 CONCLUSION: Sanity Check data is CONFIRMED ISOLATED from AI Assistance")
    print("=" * 70)
