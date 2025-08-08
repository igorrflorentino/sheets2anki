"""
Função corrigida para restaurar decks remotos
"""

import json
from .config_manager import get_meta, save_meta

def _restore_remote_decks(self, temp_dir):
    """Restaura configurações de decks remotos"""
    try:
        decks_dir = temp_dir / "decks"
        if not decks_dir.exists():
            return True  # Não há decks para restaurar
        
        # Carregar configurações atuais
        meta_data = get_meta()
        current_decks = meta_data.get('decks', {})
        
        # Restaurar cada deck
        for deck_file in decks_dir.glob('*.json'):
            with open(deck_file, 'r', encoding='utf-8') as f:
                deck_backup = json.load(f)
            
            url = deck_backup['url']
            config = deck_backup['config']
            
            current_decks[url] = config
            deck_name = config.get('local_deck_name') or config.get('deck_name', url)
            print(f"✅ Deck restaurado: {deck_name}")
        
        # Salvar configurações atualizadas
        meta_data['decks'] = current_decks
        save_meta(meta_data)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao restaurar decks remotos: {e}")
        return False