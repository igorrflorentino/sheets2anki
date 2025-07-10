#!/usr/bin/env python3
"""
Validador de Pacotes Anki Add-on

Este script valida se um pacote .ankiaddon está correto de acordo com as especificações
do AnkiWeb e melhores práticas para add-ons do Anki.
"""

import zipfile
import json
import sys
from pathlib import Path

def validate_ankiaddon(ankiaddon_path):
    """
    Valida um arquivo .ankiaddon
    
    Args:
        ankiaddon_path: Caminho para o arquivo .ankiaddon
        
    Returns:
        bool: True se válido, False caso contrário
    """
    print(f"🔍 VALIDANDO: {ankiaddon_path}")
    print("=" * 50)
    
    if not Path(ankiaddon_path).exists():
        print("❌ ERRO: Arquivo não encontrado")
        return False
    
    try:
        with zipfile.ZipFile(ankiaddon_path, 'r') as zipf:
            return validate_zip_contents(zipf)
    except zipfile.BadZipFile:
        print("❌ ERRO: Arquivo ZIP corrompido")
        return False
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def validate_zip_contents(zipf):
    """Valida o conteúdo do arquivo ZIP"""
    
    # Obter lista de arquivos
    files = zipf.namelist()
    
    print("1. Verificando estrutura do ZIP...")
    
    # Verificar se há pasta raiz (não deve ter)
    root_folders = [f for f in files if f.endswith('/') and '/' not in f.rstrip('/')]
    if root_folders:
        print(f"❌ ERRO: ZIP contém pastas raiz - AnkiWeb não aceita!")
        print(f"   Pastas encontradas: {root_folders}")
        return False
    
    print("   ✅ Estrutura sem pasta raiz: OK")
    
    # Verificar arquivos obrigatórios
    print("\n2. Verificando arquivos obrigatórios...")
    
    root_files = [f for f in files if '/' not in f and f != '']
    
    if '__init__.py' not in root_files:
        print("❌ ERRO: __init__.py não encontrado na raiz")
        return False
    print("   ✅ __init__.py: OK")
    
    if 'manifest.json' not in root_files:
        print("❌ ERRO: manifest.json não encontrado na raiz")
        return False
    print("   ✅ manifest.json: OK")
    
    # Verificar cache Python
    print("\n3. Verificando cache Python...")
    
    cache_files = [f for f in files if '__pycache__' in f or f.endswith(('.pyc', '.pyo'))]
    if cache_files:
        print("❌ ERRO CRÍTICO: Cache Python encontrado - AnkiWeb não aceita!")
        print("   Arquivos problemáticos:")
        for f in cache_files[:5]:  # Mostrar apenas os primeiros 5
            print(f"   - {f}")
        if len(cache_files) > 5:
            print(f"   ... e mais {len(cache_files) - 5} arquivos")
        return False
    
    print("   ✅ Sem cache Python: OK")
    
    # Validar manifest.json
    print("\n4. Validando manifest.json...")
    
    try:
        manifest_data = zipf.read('manifest.json')
        manifest = json.loads(manifest_data.decode('utf-8'))
    except Exception as e:
        print(f"❌ ERRO: Não foi possível ler manifest.json: {e}")
        return False
    
    # Verificar campos obrigatórios
    required_fields = ['package', 'name']
    for field in required_fields:
        if field not in manifest:
            print(f"❌ ERRO: Campo obrigatório ausente: {field}")
            return False
        if not manifest[field] or not isinstance(manifest[field], str):
            print(f"❌ ERRO: Campo '{field}' deve ser uma string não vazia")
            return False
        print(f"   ✅ {field}: {manifest[field]}")
    
    # Verificar campos opcionais
    optional_fields = ['version', 'author', 'description', 'conflicts', 'mod']
    for field in optional_fields:
        if field in manifest:
            if field == 'conflicts' and not isinstance(manifest[field], list):
                print(f"❌ ERRO: Campo '{field}' deve ser uma lista")
                return False
            print(f"   ✅ {field}: {manifest[field]}")
    
    # Verificar arquivos suspeitos
    print("\n5. Verificando arquivos suspeitos...")
    
    suspicious_files = [f for f in files if f.startswith('.') or f.endswith('.tmp')]
    if suspicious_files:
        print("⚠️  Arquivos suspeitos encontrados:")
        for f in suspicious_files:
            print(f"   - {f}")
    else:
        print("   ✅ Nenhum arquivo suspeito encontrado")
    
    # Estatísticas
    print("\n6. Estatísticas do pacote...")
    
    total_files = len(files)
    total_size = sum(zipf.getinfo(f).file_size for f in files)
    
    print(f"   📁 Total de arquivos: {total_files}")
    print(f"   📦 Tamanho descompactado: {total_size / 1024:.1f} KB")
    
    # Listar arquivos por tipo
    python_files = [f for f in files if f.endswith('.py')]
    json_files = [f for f in files if f.endswith('.json')]
    other_files = [f for f in files if not f.endswith(('.py', '.json'))]
    
    print(f"   🐍 Arquivos Python: {len(python_files)}")
    print(f"   📄 Arquivos JSON: {len(json_files)}")
    print(f"   📎 Outros arquivos: {len(other_files)}")
    
    return True

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python validate_ankiaddon.py <arquivo.ankiaddon>")
        sys.exit(1)
    
    ankiaddon_path = sys.argv[1]
    
    if validate_ankiaddon(ankiaddon_path):
        print("\n🎉 VALIDAÇÃO COMPLETA!")
        print("✅ O arquivo está pronto para distribuição")
        print("🚀 Pode ser enviado para o AnkiWeb")
    else:
        print("\n❌ VALIDAÇÃO FALHOU!")
        print("🔧 Corrija os problemas antes de distribuir")
        sys.exit(1)

if __name__ == "__main__":
    main()
