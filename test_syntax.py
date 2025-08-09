#!/usr/bin/env python3
"""
Script de teste para verificar a sintaxe dos arquivos refatorados
"""

def test_syntax():
    import ast
    import os
    
    # Lista de arquivos para testar
    files_to_test = [
        'src/data_processor.py',
        'src/student_manager.py',
        'src/config_manager.py'
    ]
    
    all_ok = True
    
    for file_path in files_to_test:
        if not os.path.exists(file_path):
            print(f"❌ Arquivo não encontrado: {file_path}")
            all_ok = False
            continue
            
        try:
            print(f"Testando sintaxe de {file_path}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tentar fazer parse do AST
            ast.parse(content, filename=file_path)
            print(f"✅ {file_path} - sintaxe OK")
            
        except SyntaxError as e:
            print(f"❌ {file_path} - Erro de sintaxe na linha {e.lineno}: {e.msg}")
            all_ok = False
        except Exception as e:
            print(f"❌ {file_path} - Erro inesperado: {e}")
            all_ok = False
    
    if all_ok:
        print("🎉 Todos os arquivos passaram no teste de sintaxe!")
    else:
        print("❌ Alguns arquivos têm problemas de sintaxe")
    
    return all_ok

if __name__ == "__main__":
    test_syntax()
