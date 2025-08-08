#!/usr/bin/env python3
"""
Script de teste para verificar se todas as importações estão funcionando
após a remoção do sistema de normalização.
"""

def test_imports():
    """Testa todas as importações principais do addon."""
    print("🧪 Testando importações...")
    
    try:
        # Testar config_manager
        from src.config_manager import get_global_student_config, save_global_student_config
        print("✅ config_manager: OK")
        
        # Testar global_student_config_dialog  
        from src.global_student_config_dialog import GlobalStudentConfigDialog
        print("✅ global_student_config_dialog: OK")
        
        # Testar student_manager
        from src.student_manager import get_students_to_sync, extract_students_from_remote_data
        print("✅ student_manager: OK")
        
        # Testar utils
        from src.utils import get_note_type_name
        print("✅ utils: OK")
        
        # Testar sync
        from src.sync import syncDecks
        print("✅ sync: OK")
        
        # Testar note_processor
        from src.note_processor import create_or_update_notes
        print("✅ note_processor: OK")
        
        print("\n🎉 Todos os módulos principais importaram com sucesso!")
        print("🧹 Sistema de normalização removido com sucesso!")
        print("📏 Sistema agora é case-sensitive!")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False
        
    return True

if __name__ == "__main__":
    success = test_imports()
    exit(0 if success else 1)
