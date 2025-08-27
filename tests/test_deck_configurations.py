#!/usr/bin/env python3
"""
Teste para verificar se a funcionalidade de configurações de deck está funcionando
corretamente.
"""

import json
import sys
import os

# Adicionar path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "..", "src"))

META_JSON_PATH = "/Users/igorflorentino/• Principais do Home/Git/Coding/anki/sheets2anki/meta.json"


def test_deck_configurations():
    """
    Testa as funcionalidades de configuração de deck.
    """
    print("🧪 Testando funcionalidades de configuração de deck...")
    
    try:
        # Carregar meta.json para verificar
        with open(META_JSON_PATH, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # Verificar se todos os decks têm a configuração
        decks = meta.get("decks", {})
        mode = meta.get("config", {}).get("deck_options_mode", "individual")
        
        print(f"📊 Modo atual: {mode}")
        print(f"📁 Total de decks: {len(decks)}")
        
        for deck_hash, deck_info in decks.items():
            deck_name = deck_info.get("remote_deck_name", "Unknown")
            config_name = deck_info.get("local_deck_configurations_package_name")
            
            print(f"✅ Deck: {deck_name}")
            print(f"   🎯 Configuração: {config_name}")
            
            # Verificar se a configuração está correta para o modo
            expected_config = None
            if mode == "individual":
                expected_config = f"Sheets2Anki - {deck_name}"
            elif mode == "shared":
                expected_config = "Sheets2Anki - Default Options"
            else:  # manual
                expected_config = None
            
            if config_name == expected_config:
                print(f"   ✅ Configuração correta para modo '{mode}'")
            else:
                print(f"   ❌ Configuração incorreta!")
                print(f"      Esperado: {expected_config}")
                print(f"      Atual: {config_name}")
        
        print("\n🎉 Teste de configurações concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()


def test_configuration_functions():
    """
    Testa as novas funções de configuração de deck.
    """
    print("\n🧪 Testando funções de configuração...")
    
    try:
        from config_manager import (
            get_deck_configurations_package_name,
            set_deck_configurations_package_name,
            get_deck_options_mode
        )
        
        # Teste com URL de deck existente
        test_url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing"
        
        print(f"🔍 Testando com URL: {test_url}")
        
        # Obter configuração atual
        current_config = get_deck_configurations_package_name(test_url)
        print(f"📋 Configuração atual: {current_config}")
        
        # Obter modo atual
        current_mode = get_deck_options_mode()
        print(f"📊 Modo atual: {current_mode}")
        
        # Verificar se a configuração está correta
        if current_config and "Sheets2Anki" in current_config:
            print("✅ Configuração válida encontrada")
        else:
            print("❌ Configuração inválida ou ausente")
        
        print("🎉 Teste de funções concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante teste de funções: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Teste de Configurações de Deck - Sheets2Anki")
    print("=" * 60)
    
    test_deck_configurations()
    test_configuration_functions()
    
    print("\n" + "=" * 60)
    print("✨ Todos os testes finalizados!")
