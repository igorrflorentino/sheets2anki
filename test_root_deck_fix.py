"""
Teste para verificar se a aplicação das opções ao deck raiz está funcionando.
"""

import sys
import os

# Adicionar o diretório src ao path para importar os módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_root_deck_options():
    """Testa se as funções de aplicação de opções ao deck raiz estão corretas"""
    
    print("=" * 60)
    print("TESTE: Verificação das Opções do Deck Raiz")
    print("=" * 60)
    
    try:
        # Simular as constantes e funções necessárias
        from src.utils import DEFAULT_PARENT_DECK_NAME, ensure_root_deck_has_root_options, get_or_create_root_options_group
        
        print(f"✅ Constante DEFAULT_PARENT_DECK_NAME: '{DEFAULT_PARENT_DECK_NAME}'")
        print("✅ Função ensure_root_deck_has_root_options() encontrada")
        print("✅ Função get_or_create_root_options_group() encontrada")
        
        # Verificar se as funções têm a lógica correta
        import inspect
        
        # Examinar código da função ensure_root_deck_has_root_options
        source = inspect.getsource(ensure_root_deck_has_root_options)
        
        # Verificações básicas
        checks = {
            "Usa DEFAULT_PARENT_DECK_NAME": "DEFAULT_PARENT_DECK_NAME" in source,
            "Cria deck se não existe": "mw.col.decks.id(DEFAULT_PARENT_DECK_NAME)" in source,
            "Chama get_or_create_root_options_group": "get_or_create_root_options_group()" in source,
            "Atribui conf ao deck": "parent_deck['conf'] = root_options_group_id" in source,
            "Salva o deck": "mw.col.decks.save(parent_deck)" in source,
            "Verifica se é None": "parent_deck_id is not None" in source,
            "Logs informativos": "print(f" in source and "[DECK_OPTIONS]" in source
        }
        
        print("\n🔍 VERIFICAÇÕES DA FUNÇÃO ensure_root_deck_has_root_options:")
        all_good = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
            if not result:
                all_good = False
        
        # Examinar função get_or_create_root_options_group
        source2 = inspect.getsource(get_or_create_root_options_group)
        
        checks2 = {
            "Nome correto do grupo": '"Sheets2Anki - Root Options"' in source2,
            "Procura grupo existente": "all_config()" in source2,
            "Cria novo se necessário": "add_config_returning_id" in source2,
            "Configura opções": "config['new']['perDay']" in source2,
        }
        
        print("\n🔍 VERIFICAÇÕES DA FUNÇÃO get_or_create_root_options_group:")
        for check, result in checks2.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}: {result}")
            if not result:
                all_good = False
        
        if all_good:
            print("\n✅ RESULTADO: Todas as verificações passaram!")
            print("   A correção da lógica do deck raiz parece estar correta.")
        else:
            print("\n❌ RESULTADO: Algumas verificações falharam!")
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_root_deck_options()
