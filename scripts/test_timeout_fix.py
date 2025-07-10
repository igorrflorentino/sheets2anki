#!/usr/bin/env python3
"""
Script de Diagnóstico de Timeout - Sheets2Anki

Este script simula exatamente o comportamento da função import_test_deck
para diagnosticar o problema de timeout.
"""

import sys
import socket
import urllib.request
import urllib.error
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# URLs de teste do projeto
TEST_SHEETS_URLS = [
    ("Mais importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv"),
    ("Menos importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=1869088045&output=tsv"),
]

def test_timeout_configuration():
    """Testa diferentes configurações de timeout"""
    print("🧪 TESTE 1: Timeout Global (método antigo)")
    url = TEST_SHEETS_URLS[0][1]
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'}
        request = urllib.request.Request(url, headers=headers)
        
        # Método antigo - timeout global
        socket.setdefaulttimeout(30)
        response = urllib.request.urlopen(request)
        print("✅ Timeout global funcionou!")
        socket.setdefaulttimeout(None)
        
    except Exception as e:
        print(f"❌ Timeout global falhou: {e}")
        socket.setdefaulttimeout(None)
    
    print("\n🧪 TESTE 2: Timeout Local (método novo)")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'}
        request = urllib.request.Request(url, headers=headers)
        
        # Método novo - timeout local
        response = urllib.request.urlopen(request, timeout=30)
        print("✅ Timeout local funcionou!")
        
    except Exception as e:
        print(f"❌ Timeout local falhou: {e}")

def test_validate_url_function():
    """Testa a função validate_url corrigida"""
    print("\n🧪 TESTE 3: Função validate_url corrigida")
    
    try:
        # Importar a função validate_url
        from main import validate_url
        
        url = TEST_SHEETS_URLS[0][1]
        validate_url(url)
        print("✅ validate_url() funcionou!")
        
    except Exception as e:
        print(f"❌ validate_url() falhou: {e}")

def test_getRemoteDeck_function():
    """Testa a função getRemoteDeck corrigida"""
    print("\n🧪 TESTE 4: Função getRemoteDeck corrigida")
    
    try:
        # Importar a função getRemoteDeck
        from parseRemoteDeck import getRemoteDeck
        
        url = TEST_SHEETS_URLS[0][1]
        deck = getRemoteDeck(url)
        print(f"✅ getRemoteDeck() funcionou! Deck com {len(deck.questions)} questões")
        
    except Exception as e:
        print(f"❌ getRemoteDeck() falhou: {e}")

def test_import_test_deck_simulation():
    """Simula o fluxo completo da função import_test_deck"""
    print("\n🧪 TESTE 5: Simulação completa import_test_deck")
    
    try:
        from main import validate_url
        from parseRemoteDeck import getRemoteDeck
        
        # Simular seleção do primeiro deck
        selection = TEST_SHEETS_URLS[0][0]
        url = dict(TEST_SHEETS_URLS)[selection]
        deckName = f"Deck de Teste :: {selection}"
        
        print(f"📋 Seleção: {selection}")
        print(f"🔗 URL: {url[:80]}...")
        print(f"📛 Nome: {deckName}")
        
        # Passo 1: Validar URL
        print("🔍 Validando URL...")
        validate_url(url)
        print("✅ URL validada com sucesso!")
        
        # Passo 2: Buscar deck remoto
        print("📥 Buscando deck remoto...")
        deck = getRemoteDeck(url)
        deck.deckName = deckName
        print(f"✅ Deck obtido com sucesso! {len(deck.questions)} questões")
        
        print("🎉 SIMULAÇÃO COMPLETA BEM-SUCEDIDA!")
        
    except Exception as e:
        print(f"❌ Simulação falhou: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🚀 SHEETS2ANKI - DIAGNÓSTICO DE TIMEOUT")
    print("=" * 60)
    
    test_timeout_configuration()
    test_validate_url_function()
    test_getRemoteDeck_function()
    test_import_test_deck_simulation()
    
    print("\n" + "=" * 60)
    print("📋 DIAGNÓSTICO CONCLUÍDO")
    print("💡 Se todos os testes passaram, o problema de timeout foi corrigido!")

if __name__ == "__main__":
    main()
