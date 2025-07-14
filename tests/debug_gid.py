#!/usr/bin/env python3
"""
Debug do problema de GID não numérico.
"""

import re
from urllib.parse import urlparse, parse_qs

def debug_gid_extraction():
    """Debug da extração de GID."""
    
    test_url = "https://docs.google.com/spreadsheets/d/1ABC123DEF456789012345678901234567890123456/edit#gid=abc"
    print(f"URL de teste: {test_url}")
    
    # Extrair GID se presente
    gid = "0"  # Padrão
    
    print(f"GID inicial: {gid}")
    
    # Tentar extrair GID do fragmento (#gid=123)
    if '#gid=' in test_url:
        print("Encontrou #gid= na URL")
        gid_match = re.search(r'#gid=(\d+)', test_url)
        print(f"Regex match: {gid_match}")
        if gid_match:
            gid = gid_match.group(1)
            print(f"GID extraído: {gid}")
        else:
            print("Regex não fez match - tentando regex mais ampla")
            gid_match2 = re.search(r'#gid=([^&]+)', test_url)
            print(f"Regex ampla match: {gid_match2}")
            if gid_match2:
                gid = gid_match2.group(1)
                print(f"GID extraído (amplo): {gid}")
    
    # Tentar extrair GID dos parâmetros (?gid=123)
    elif '?gid=' in test_url or '&gid=' in test_url:
        print("Encontrou ?gid= ou &gid= na URL")
        parsed = urlparse(test_url)
        params = parse_qs(parsed.query)
        if 'gid' in params:
            gid = params['gid'][0]
            print(f"GID dos parâmetros: {gid}")
    
    print(f"GID final: {gid}")
    print(f"GID é dígito: {gid.isdigit()}")
    
    return gid

if __name__ == "__main__":
    debug_gid_extraction()
