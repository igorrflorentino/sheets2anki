#!/usr/bin/env python3
"""
Script de debug consolidado para o Sheets2Anki.
Centraliza todos os utilitários de debug para facilitar a manutenção.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import urllib.request
import urllib.error
import traceback
from src.constants import TEST_SHEETS_URLS
from src.column_definitions import REQUIRED_COLUMNS
from src.parseRemoteDeck import (
    getRemoteDeck, parse_tsv_data, build_remote_deck_from_tsv, 
    validate_google_sheets_url, create_fallback_urls, ensure_values_only_url,
    validate_tsv_headers
)

def debug_url_validation():
    """Debug de validação de URLs"""
    print("=== DEBUG URL VALIDATION ===")
    
    test_urls = [
        "https://docs.google.com/spreadsheets/d/1ABC123DEF456789012345678901234567890123456/edit#gid=0",
        "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv",
        "https://invalid-url.com/test",
        "https://docs.google.com/spreadsheets/d/SHORT/edit#gid=0"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- URL {i} ---")
        print(f"URL: {url}")
        
        try:
            result = validate_google_sheets_url(url)
            print(f"Valid: {result['valid']}")
            print(f"Spreadsheet ID: {result.get('spreadsheet_id', 'N/A')}")
            print(f"GID: {result.get('gid', 'N/A')}")
            if result['issues']:
                print(f"Issues: {result['issues']}")
            if result['suggestions']:
                print(f"Suggestions: {result['suggestions']}")
        except Exception as e:
            print(f"Error: {e}")

def debug_header_validation():
    """Debug de validação de headers"""
    print("\n=== DEBUG HEADER VALIDATION ===")
    
    # Testar com headers corretos
    correct_headers = REQUIRED_COLUMNS.copy()
    print(f"Testing correct headers: {len(correct_headers)} columns")
    
    try:
        validated = validate_tsv_headers(correct_headers)
        print(f"✅ Validation passed: {len(validated)} headers")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    # Testar com headers incompletos
    incomplete_headers = REQUIRED_COLUMNS[:10]  # Apenas 10 primeiros
    print(f"\nTesting incomplete headers: {len(incomplete_headers)} columns")
    
    try:
        validated = validate_tsv_headers(incomplete_headers)
        print(f"✅ Validation passed: {len(validated)} headers")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

def debug_getRemoteDeck_workflow():
    """Debug do workflow completo do getRemoteDeck"""
    print("\n=== DEBUG getRemoteDeck WORKFLOW ===")
    
    # Testar com primeira URL das constantes
    name, original_url = TEST_SHEETS_URLS[0]
    print(f"Testing URL: {name}")
    print(f"Original URL: {original_url}")
    
    # Passo 1: Validar URL
    print("\n--- STEP 1: URL Validation ---")
    validation_result = validate_google_sheets_url(original_url)
    print(f"Validation: {validation_result}")
    
    # Passo 2: Modificar URL
    print("\n--- STEP 2: URL Modification ---")
    modified_url = ensure_values_only_url(original_url)
    print(f"Modified URL: {modified_url}")
    
    # Passo 3: Criar fallback URLs
    print("\n--- STEP 3: Fallback URLs ---")
    fallback_urls = create_fallback_urls(original_url, validation_result)
    urls_to_try = [modified_url] + fallback_urls
    print(f"Total URLs to try: {len(urls_to_try)}")
    
    # Passo 4: Testar download
    print("\n--- STEP 4: Download Test ---")
    successful_url = None
    response = None
    
    for i, url in enumerate(urls_to_try, 1):
        print(f"\nTrying URL {i}: {url[:80]}...")
        try:
            response = urllib.request.urlopen(url, timeout=30)
            print(f"✅ Success! Status: {response.getcode()}")
            successful_url = url
            break
        except urllib.error.HTTPError as e:
            print(f"❌ HTTPError {e.code}: {e.reason}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if successful_url:
        print(f"\n✅ Successful URL: {successful_url}")
        
        # Passo 5: Processar dados
        print("\n--- STEP 5: Data Processing ---")
        try:
            tsv_data = response.read().decode('utf-8')
            print(f"✅ Content decoded: {len(tsv_data)} characters")
            
            # Processar TSV
            data = parse_tsv_data(tsv_data)
            print(f"✅ TSV parsed: {len(data)} rows")
            
            # Construir deck
            deck = build_remote_deck_from_tsv(data)
            print(f"✅ Deck built: {len(deck.questions)} questions")
            
        except Exception as e:
            print(f"❌ Processing error: {e}")
            traceback.print_exc()
    else:
        print("\n❌ No URL worked!")

def debug_constants_urls():
    """Debug das URLs das constantes"""
    print("\n=== DEBUG CONSTANTS URLS ===")
    
    for i, (name, url) in enumerate(TEST_SHEETS_URLS, 1):
        print(f"\n--- URL {i}: {name} ---")
        print(f"URL: {url}")
        
        try:
            deck = getRemoteDeck(url)
            print(f"✅ SUCCESS! Deck created with {len(deck.questions)} questions")
            
            if deck.questions:
                first_question = deck.questions[0]
                if isinstance(first_question, dict):
                    print(f"First question ID: {first_question.get('id', 'N/A')}")
                else:
                    print(f"First question: {first_question}")
                    
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
            # Analisar erro específico
            if "Colunas obrigatórias" in str(e):
                print("⚠️  Column validation error detected!")
                
                # Download manual para análise
                try:
                    with urllib.request.urlopen(url) as response:
                        content = response.read().decode('utf-8')
                        
                    lines = content.strip().split('\n')
                    if lines:
                        headers = lines[0].split('\t')
                        print(f"Manual download headers: {len(headers)}")
                        
                        missing = [col for col in REQUIRED_COLUMNS if col not in headers]
                        if missing:
                            print(f"Missing columns: {missing}")
                        else:
                            print("✅ All required columns present in manual download")
                            
                except Exception as download_error:
                    print(f"Manual download error: {download_error}")

def main():
    """Função principal de debug"""
    print("🔍 SHEETS2ANKI DEBUG SUITE")
    print("=" * 50)
    
    # Executar todos os debugs
    debug_url_validation()
    debug_header_validation()
    debug_getRemoteDeck_workflow()
    debug_constants_urls()
    
    print("\n" + "=" * 50)
    print("🎉 DEBUG SUITE COMPLETED")

if __name__ == "__main__":
    main()
