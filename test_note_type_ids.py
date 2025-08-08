#!/usr/bin/env python3
"""
Script de teste para capturar manualmente note type IDs.
Para usar no console do Anki:

1. Abra o Anki
2. Vá em Tools -> Add-ons -> (selecione o Sheets2Anki) -> Config
3. Cole e execute este código no console Python do Anki:

exec(open('/Users/igorflorentino/Git/Coding/anki/sheets2anki/test_note_type_ids.py').read())

Ou copie e cole o código abaixo diretamente:
"""

try:
    # Importar o config_manager do addon
    import sys
    import os
    addon_path = os.path.dirname(__file__)
    if addon_path not in sys.path:
        sys.path.insert(0, addon_path)
    
    from src.config_manager import test_note_type_id_capture
    
    print("🚀 EXECUTANDO TESTE MANUAL DE CAPTURA DE NOTE TYPE IDS")
    print("=" * 60)
    
    # Executar o teste
    test_note_type_id_capture()
    
    print("=" * 60)
    print("✅ TESTE CONCLUÍDO!")
    print("\nVerifique se o campo 'note_type_ids' apareceu no meta.json")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que o addon está instalado e ativo")
except Exception as e:
    print(f"❌ Erro durante o teste: {e}")
    import traceback
    traceback.print_exc()
