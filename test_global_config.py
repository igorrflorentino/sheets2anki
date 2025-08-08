#!/usr/bin/env python3
"""
Teste para verificar a configuração global de estudantes.
"""

import json
import os

def test_global_config():
    """Testa a configuração global de estudantes."""
    print("=== VERIFICAÇÃO DE CONFIGURAÇÃO GLOBAL ===")
    
    # Verificar se existe config global 
    config_files = [
        'config.json',
        'global_student_config.json',
        'student_config.json'
    ]
    
    found_config = False
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"📁 Encontrado arquivo: {config_file}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                print(f"Conteúdo de {config_file}:")
                print(json.dumps(config, indent=2, ensure_ascii=False))
                
                # Procurar por configurações de estudantes
                if 'available_students' in config:
                    available = config['available_students']
                    print(f"🎓 Estudantes disponíveis atuais: {available}")
                    if 'Belle' in available and 'Igor2' in available and 'pedro' in available:
                        print("✅ PROBLEMA ENCONTRADO: Todos os estudantes já estão na lista!")
                        print("Isso explica porque 'nenhum novo estudante' foi encontrado.")
                        found_config = True
                
                if 'enabled_students' in config:
                    enabled = config['enabled_students']
                    print(f"✅ Estudantes habilitados atuais: {enabled}")
                
            except Exception as e:
                print(f"❌ Erro ao ler {config_file}: {e}")
    
    if not found_config:
        print("🔍 Nenhum arquivo de configuração de estudantes encontrado.")
        print("Isso pode indicar que é a primeira execução.")
    
    return found_config

def test_meta_student_data():
    """Verifica se há dados de estudantes no meta.json."""
    print("\n=== VERIFICAÇÃO DE DADOS NO META.JSON ===")
    
    try:
        with open('meta.json', 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # Verificar se há dados de estudantes no meta
        if 'students' in meta:
            print(f"📊 Dados de estudantes no meta: {meta['students']}")
        
        if 'global_student_config' in meta:
            print(f"⚙️ Configuração global no meta: {meta['global_student_config']}")
        
        # Verificar decks para configurações de estudantes
        decks = meta.get('decks', {})
        for hash_key, deck_info in decks.items():
            if 'student_selection' in deck_info:
                print(f"👥 Seleção de estudantes no deck {hash_key}: {deck_info['student_selection']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar meta.json: {e}")
        return False

if __name__ == "__main__":
    print("🔍 INVESTIGANDO CONFIGURAÇÃO DE ESTUDANTES...")
    print("Estudantes encontrados no TSV: ['Belle', 'Igor2', 'pedro']")
    print("Vamos verificar se eles já estão cadastrados...\n")
    
    config_found = test_global_config()
    meta_ok = test_meta_student_data()
    
    if not config_found and not meta_ok:
        print("\n❓ SUSPEITA: Nenhuma configuração de estudantes encontrada.")
        print("O addon pode estar com problema na criação/leitura da configuração.")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Execute o addon no Anki e clique em 'Busca Automática'")
    print("2. Verifique o console do Anki para mensagens de debug")  
    print("3. Verifique se os arquivos de configuração são criados")
