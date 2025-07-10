#!/usr/bin/env python3
"""
Script de Diagnóstico de Conectividade

Este script testa a conectividade com as URLs de teste do Sheets2Anki
para diagnosticar problemas de rede.
"""

import urllib.request
import urllib.error
import socket
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# URLs de teste hardcoded
TEST_URLS = [
    ("Mais importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv"),
    ("Menos importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=1869088045&output=tsv"),
]

def test_url_connectivity(name, url):
    """Testa conectividade com uma URL específica"""
    print(f"\n🔍 Testando: {name}")
    print(f"📍 URL: {url}")
    
    try:
        # Configurar request com headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon/Test'
        }
        request = urllib.request.Request(url, headers=headers)
        
        # Configurar timeout
        socket.setdefaulttimeout(30)
        
        print("⏳ Tentando conectar...")
        response = urllib.request.urlopen(request)
        
        print(f"✅ Sucesso! Status: {response.getcode()}")
        print(f"📄 Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # Ler primeiras linhas para verificar conteúdo
        content = response.read().decode('utf-8')
        lines = content.split('\n')[:3]
        print(f"📝 Primeiras linhas:")
        for i, line in enumerate(lines, 1):
            print(f"   {i}: {line[:80]}{'...' if len(line) > 80 else ''}")
            
        return True
        
    except socket.timeout:
        print("❌ ERRO: Timeout de conexão (30s)")
        return False
    except urllib.error.HTTPError as e:
        print(f"❌ ERRO HTTP {e.code}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            print("❌ ERRO: Timeout de conexão")
        elif isinstance(e.reason, socket.gaierror):
            print("❌ ERRO: Problema de DNS - verifique sua conexão")
        else:
            print(f"❌ ERRO de URL: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")
        return False
    finally:
        socket.setdefaulttimeout(None)

def main():
    print("🚀 SHEETS2ANKI - DIAGNÓSTICO DE CONECTIVIDADE")
    print("=" * 50)
    
    successful_tests = 0
    total_tests = len(TEST_URLS)
    
    for name, url in TEST_URLS:
        if test_url_connectivity(name, url):
            successful_tests += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {successful_tests}/{total_tests} testes bem-sucedidos")
    
    if successful_tests == total_tests:
        print("🎉 Todas as URLs estão acessíveis!")
    elif successful_tests == 0:
        print("💥 Nenhuma URL está acessível. Verifique sua conexão com a internet.")
    else:
        print("⚠️  Algumas URLs apresentaram problemas.")
    
    print("\n💡 DICAS DE SOLUÇÃO:")
    print("   1. Verifique sua conexão com a internet")
    print("   2. Teste em outro navegador se as URLs funcionam")
    print("   3. Verifique se há firewall bloqueando conexões")
    print("   4. Tente novamente em alguns minutos")

if __name__ == "__main__":
    main()
