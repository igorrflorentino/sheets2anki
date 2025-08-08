#!/usr/bin/env python3
import re
import hashlib

def get_publication_key(url):
    """Extrai a chave de publicação da URL."""
    match = re.search(r'/spreadsheets/d/e/([^/]+)/', url)
    return match.group(1) if match else None

def get_deck_hash(url):
    """Gera hash MD5 da chave de publicação."""
    pub_key = get_publication_key(url)
    if not pub_key:
        return None
    return hashlib.md5(pub_key.encode()).hexdigest()[:8]

def get_model_suffix_from_url(url):
    """Função original para compatibilidade."""
    return get_deck_hash(url)

# Teste
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSsNCEFZvBR3UjBwTbyaPPz-B1SKw17I7Jb72XWweS1y75HmzXfgdFJ1TpZX6_S06m9_phJTy5XnCI6/pub?gid=36065074&single=true&output=tsv'
pub_key = get_publication_key(url)
hash_val = get_deck_hash(url)
print(f'URL: {url}')
print(f'Chave de publicação: {pub_key}')
print(f'Hash gerado: {hash_val}')
print(f'Padrão de busca: "Sheets2Anki - {hash_val} -"')
