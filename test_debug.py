#!/usr/bin/env python3
"""
Script de teste para verificar o sistema de debug messages.
"""

def test_debug_format():
    """Testa a formatação das mensagens de debug."""
    from datetime import datetime
    
    debug_messages = []
    
    def add_debug_msg(message, category="DEBUG"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] [{category}] {message}"
        debug_messages.append(formatted_msg)
        print(formatted_msg)
    
    # Simular algumas mensagens
    add_debug_msg("🚀 INICIANDO sincronização para deck: https://example.com/sheet", "SYNC")
    add_debug_msg("📋 Deck ID: 1234567890", "SYNC")
    add_debug_msg("Iniciando captura de note type IDs para deck: TestDeck", "SYNC")
    add_debug_msg("Hash da URL: abc123def456", "NOTE_TYPE_IDS")
    add_debug_msg("✅ MATCH encontrado: 'TestSheet_abc123' (ID: 9876543210)", "NOTE_TYPE_IDS")
    add_debug_msg("✅ SUCESSO: Adicionado note type ID 9876543210", "CONFIG")
    
    print("\n" + "="*50)
    print("DEBUG MESSAGES ACUMULADAS:")
    print("="*50)
    for msg in debug_messages:
        print(msg)
    
    print(f"\nTotal de mensagens: {len(debug_messages)}")

if __name__ == "__main__":
    test_debug_format()
