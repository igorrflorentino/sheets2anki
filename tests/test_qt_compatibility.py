#!/usr/bin/env python3
"""
Teste de compatibilidade Qt para verificar se as constantes estão funcionando.
"""

import sys
import os

# Adicionar o diretório src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_qt_compatibility():
    """Testa se as constantes Qt são importadas corretamente."""
    try:
        from compat import (
            QDialog, QDialogButtonBox, QMessageBox,
            ButtonBox_Ok, ButtonBox_Cancel, ButtonBox_Yes, ButtonBox_No,
            MessageBox_Yes, MessageBox_No, MessageBox_Ok, MessageBox_Cancel,
            DialogAccepted, DialogRejected,
            safe_exec_dialog
        )
        
        print("✓ Importações Qt básicas funcionaram!")
        
        # Testar se as constantes existem
        test_constants = [
            ('ButtonBox_Ok', ButtonBox_Ok),
            ('ButtonBox_Cancel', ButtonBox_Cancel),
            ('MessageBox_Yes', MessageBox_Yes),
            ('MessageBox_No', MessageBox_No),
            ('DialogAccepted', DialogAccepted),
        ]
        
        for name, constant in test_constants:
            if constant is not None:
                print(f"✓ {name} = {constant}")
            else:
                print(f"✗ {name} é None")
                return False
        
        print("✓ Todas as constantes Qt foram definidas corretamente!")
        return True
        
    except ImportError as e:
        print(f"✗ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado: {e}")
        return False

def test_student_manager_import():
    """Testa se o student_manager pode ser importado."""
    try:
        # Primeiro testar se podemos importar as dependências
        from compat import (
            QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
            QLabel, QPushButton, QScrollArea, QWidget, QFrame, QGroupBox,
            QDialogButtonBox, QTextEdit, ButtonBox_Ok, ButtonBox_Cancel,
            safe_exec_dialog, DialogAccepted
        )
        
        print("✓ Dependências do student_manager importadas!")
        
        # Agora tentar importar o student_manager
        import student_manager
        print("✓ student_manager importado com sucesso!")
        
        # Testar se a classe principal pode ser instanciada (sem executar)
        students = ["João", "Maria", "Pedro"]
        deck_url = "test_url"
        current_selection = {"João"}
        
        # Não vamos realmente instanciar, apenas verificar se a classe existe
        if hasattr(student_manager, 'StudentSelectionDialog'):
            print("✓ Classe StudentSelectionDialog encontrada!")
        else:
            print("✗ Classe StudentSelectionDialog não encontrada!")
            return False
            
        return True
        
    except ImportError as e:
        print(f"✗ Erro de importação do student_manager: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro inesperado no student_manager: {e}")
        return False

def main():
    """Executa todos os testes de compatibilidade."""
    print("=== TESTES DE COMPATIBILIDADE QT ===\n")
    
    tests = [
        ("Compatibilidade Qt", test_qt_compatibility),
        ("Importação Student Manager", test_student_manager_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSOU\n")
            else:
                print(f"✗ {test_name} FALHOU\n")
        except Exception as e:
            print(f"✗ {test_name} ERRO: {e}\n")
    
    print(f"=== RESULTADO: {passed}/{total} testes passaram ===")
    
    if passed == total:
        print("✓ Todos os testes de compatibilidade passaram!")
        print("O addon deve funcionar corretamente agora.")
    else:
        print("✗ Alguns testes falharam. Verificar logs acima.")
        
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
