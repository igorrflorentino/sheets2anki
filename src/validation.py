"""
Funções de validação para o addon Sheets2Anki.

Este módulo contém funções para validar URLs e dados
antes da sincronização.
"""

import urllib.request
import urllib.error
import socket

def validate_url(url):
    """
    Valida se a URL é uma URL válida do Google Sheets em formato TSV.
    
    Args:
        url (str): A URL a ser validada
        
    Raises:
        ValueError: Se a URL for inválida ou inacessível
        URLError: Se houver problemas de conectividade de rede
        HTTPError: Se o servidor retornar um erro de status
    """
    # Verificar se a URL não está vazia
    if not url or not isinstance(url, str):
        raise ValueError("URL deve ser uma string não vazia")

    # Validar formato da URL
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL inválida: Deve começar com http:// ou https://")
    
    # Validar formato TSV do Google Sheets
    if not any(param in url.lower() for param in ['output=tsv', 'format=tsv']):
        raise ValueError("A URL fornecida não parece ser um TSV publicado do Google Sheets. "
                        "Certifique-se de publicar a planilha em formato TSV.")
    
    # Testar acessibilidade da URL com timeout e tratamento de erros adequado
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Sheets2Anki) AnkiAddon'  # User agent mais específico
        }
        request = urllib.request.Request(url, headers=headers)
        
        # USAR TIMEOUT LOCAL ao invés de global para evitar conflitos
        response = urllib.request.urlopen(request, timeout=30)  # ✅ TIMEOUT LOCAL
        
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
