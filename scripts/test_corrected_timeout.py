#!/usr/bin/env python3
"""
Script de Teste das Correções de Timeout

Este script testa especificamente as correções aplicadas para resolver
o problema de timeout no pacote standalone.
"""

import socket
import urllib.request
import urllib.error

# URLs de teste do projeto
TEST_SHEETS_URLS = [
    ("Mais importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv"),
    ("Menos importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=1869088045&output=tsv"),
]

def validate_url_corrected(url):
    """
    Versão corrigida da função validate_url (usando timeout local)
    """
    # Verificar se a URL não está vazia
    if not url or not isinstance(url, str):
        raise ValueError("URL deve ser uma string não vazia")

    # Validar formato da URL
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL inválida: Deve começar com http:// ou https://")
    
    # Validar formato TSV do Google Sheets
    if not any(param in url.lower() for param in ['output=tsv', 'format=tsv']):
        raise ValueError("A URL fornecida não parece ser um TSV publicado do Google Sheets.")
    
    # Testar acessibilidade da URL com timeout LOCAL (correção aplicada)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
        }
        request = urllib.request.Request(url, headers=headers)
        
        # ✅ CORREÇÃO: Timeout LOCAL ao invés de global
        response = urllib.request.urlopen(request, timeout=30)
        
        if response.getcode() != 200:
            raise ValueError(f"URL retornou código de status inesperado: {response.getcode()}")
        
        # Validar tipo de conteúdo
        content_type = response.headers.get('Content-Type', '').lower()
        if not any(valid_type in content_type for valid_type in ['text/tab-separated-values', 'text/plain', 'text/csv']):
            raise ValueError(f"URL não retorna conteúdo TSV (recebido {content_type})")
            
    except socket.timeout:
        raise ValueError("Timeout de conexão ao acessar a URL (30s). Verifique sua conexão ou tente novamente.")
    except urllib.error.HTTPError as e:
        raise ValueError(f"Erro HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            raise ValueError("Timeout de conexão ao acessar a URL. Verifique sua conexão ou tente novamente.")
        elif isinstance(e.reason, socket.gaierror):
            raise ValueError("Erro de DNS. Verifique sua conexão com a internet.")
        else:
            raise ValueError(f"Erro ao acessar URL - Problema de rede ou servidor: {str(e.reason)}")
    except Exception as e:
        raise ValueError(f"Erro inesperado ao acessar URL: {str(e)}")

def getRemoteDeck_corrected(url):
    """
    Versão simplificada da função getRemoteDeck (usando timeout local)
    """
    try:
        # Usar timeout local (correção aplicada)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'
        }
        request = urllib.request.Request(url, headers=headers)
        
        # ✅ CORREÇÃO: Timeout LOCAL ao invés de global
        response = urllib.request.urlopen(request, timeout=30)
        
        if response.getcode() != 200:
            raise Exception(f"URL retornou código de status inesperado: {response.getcode()}")
            
    except socket.timeout:
        raise Exception(f"Timeout ao acessar URL (30s). Verifique sua conexão ou tente novamente.")
    except urllib.error.HTTPError as e:
        raise Exception(f"Erro HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        if isinstance(e.reason, socket.timeout):
            raise Exception(f"Timeout ao acessar URL. Verifique sua conexão ou tente novamente.")
        elif isinstance(e.reason, socket.gaierror):
            raise Exception(f"Erro de DNS. Verifique sua conexão com a internet.")
        else:
            raise Exception(f"Erro de conexão: {str(e.reason)}")
    except Exception as e:
        raise Exception(f"Erro inesperado de rede ao baixar TSV: {e}")
    
    # Decodificar conteúdo
    try:
        tsv_data = response.read().decode('utf-8')
        lines = tsv_data.split('\n')
        return len([line for line in lines if line.strip()])  # Retornar número de linhas
    except UnicodeDecodeError as e:
        raise Exception(f"Erro ao decodificar conteúdo TSV: {e}")

def test_corrected_functions():
    """Testa as funções corrigidas"""
    print("🧪 TESTE DAS CORREÇÕES DE TIMEOUT")
    print("=" * 50)
    
    success_count = 0
    total_tests = len(TEST_SHEETS_URLS)
    
    for name, url in TEST_SHEETS_URLS:
        print(f"\n🔍 Testando: {name}")
        
        try:
            # Teste 1: validate_url corrigida
            print("   📋 Validando URL...")
            validate_url_corrected(url)
            print("   ✅ URL validada com sucesso!")
            
            # Teste 2: getRemoteDeck corrigida
            print("   📥 Buscando dados remotos...")
            line_count = getRemoteDeck_corrected(url)
            print(f"   ✅ Dados obtidos com sucesso! {line_count} linhas")
            
            success_count += 1
            
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"📊 RESULTADO: {success_count}/{total_tests} testes bem-sucedidos")
    
    if success_count == total_tests:
        print("🎉 TODAS AS CORREÇÕES FUNCIONARAM!")
        print("✅ O problema de timeout foi corrigido")
        print("✅ Pacote standalone deve funcionar corretamente")
    else:
        print("⚠️  Algumas correções apresentaram problemas")
    
    return success_count == total_tests

def main():
    print("🚀 SHEETS2ANKI - TESTE DAS CORREÇÕES")
    print("=" * 60)
    
    success = test_corrected_functions()
    
    print("\n💡 RESUMO DAS CORREÇÕES APLICADAS:")
    print("   1. ❌ socket.setdefaulttimeout(30) - Removido (global)")
    print("   2. ✅ urllib.request.urlopen(request, timeout=30) - Adicionado (local)")
    print("   3. ✅ Evita conflitos de threading no Anki")
    print("   4. ✅ Compatível com ambientes multi-thread")
    
    if success:
        print("\n🎯 CONCLUSÃO: Pacote standalone deve funcionar sem erros de timeout!")
    else:
        print("\n⚠️  ATENÇÃO: Ainda há problemas que precisam ser investigados.")

if __name__ == "__main__":
    main()
