#!/usr/bin/env python3
"""
Test to verify if deck configuration functionality is working correctly.
"""

import json
import sys
import os

# Get project root and source directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(base_dir, "src")
sys.path.insert(0, src_dir)

META_JSON_PATH = os.path.join(base_dir, "meta.json")


def test_deck_configurations():
    """
    Tests deck configuration functionalities.
    """
    print("🧪 Testing deck configuration functionalities...")
    
    try:
        # Load meta.json to verify
        if not os.path.exists(META_JSON_PATH):
            print(f"⚠️ meta.json not found at {META_JSON_PATH}")
            return

        with open(META_JSON_PATH, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        # Check if all decks have configuration
        decks = meta.get("decks", {})
        mode = meta.get("config", {}).get("deck_options_mode", "individual")
        
        print(f"📊 Current mode: {mode}")
        print(f"📁 Total decks: {len(decks)}")
        
        for deck_hash, deck_info in decks.items():
            deck_name = deck_info.get("remote_deck_name", "Unknown")
            config_name = deck_info.get("local_deck_configurations_package_name")
            
            print(f"✅ Deck: {deck_name}")
            print(f"   🎯 Configuration: {config_name}")
            
            # Check if configuration is correct for the mode
            expected_config = None
            if mode == "individual":
                expected_config = f"Sheets2Anki - {deck_name}"
            elif mode == "shared":
                expected_config = "Sheets2Anki - Default Options"
            else:  # manual
                expected_config = None
            
            if config_name == expected_config or mode == "manual":
                print(f"   ✅ Correct configuration for mode '{mode}'")
            else:
                print(f"   ❌ Incorrect configuration!")
                print(f"      Expected: {expected_config}")
                print(f"      Actual: {config_name}")
        
        print("\n🎉 Configuration test completed!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()


def test_configuration_functions():
    """
    Tests new deck configuration functions.
    """
    print("\n🧪 Testing configuration functions...")
    
    try:
        from config_manager import (
            get_deck_configurations_package_name,
            set_deck_configurations_package_name,
            get_deck_options_mode
        )
        
        # Test with an existing deck URL (using a sample)
        test_url = "https://docs.google.com/spreadsheets/d/1N-Va4ZzLUJBsD6wBaOkoeFTE6EnbZdaPBB88FYl2hrs/edit?usp=sharing"
        
        print(f"🔍 Testing with URL: {test_url}")
        
        # Get current configuration
        current_config = get_deck_configurations_package_name(test_url)
        print(f"📋 Current configuration: {current_config}")
        
        # Get current mode
        current_mode = get_deck_options_mode()
        print(f"📊 Current mode: {current_mode}")
        
        # Check if configuration is valid
        if current_config and "Sheets2Anki" in current_config:
            print("✅ Valid configuration found")
        else:
            print("❌ Invalid or missing configuration")
        
        print("🎉 Function test completed!")
        
    except Exception as e:
        print(f"❌ Error during function test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Deck Configuration Test - Sheets2Anki")
    print("=" * 60)
    
    test_deck_configurations()
    test_configuration_functions()
    
    print("\n" + "=" * 60)
    print("✨ All tests finished!")
