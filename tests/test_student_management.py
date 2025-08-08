#!/usr/bin/env python3
"""
Script de teste básico para a funcionalidade de gerenciamento de alunos.
Este script não pode ser executado fora do ambiente Anki, mas serve para
verificar a sintaxe e estrutura do código.
"""

import sys
import os

# Adicionar o diretório src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_student_extraction():
    """Testa extração de alunos de dados simulados."""
    print("Testando extração de alunos...")
    
    # Simular dados de uma planilha
    class MockRemoteDeck:
        def __init__(self):
            self.questions = [
                {'fields': {'ID': '1', 'ALUNO': 'João'}},
                {'fields': {'ID': '2', 'ALUNO': 'Maria, Pedro'}},
                {'fields': {'ID': '3', 'ALUNO': 'João|Ana'}},
                {'fields': {'ID': '4', 'ALUNO': ''}},
                {'fields': {'ID': '5', 'ALUNO': 'Pedro; Ana; Carlos'}},
            ]
    
    try:
        from student_manager import extract_students_from_remote_data
        
        mock_deck = MockRemoteDeck()
        students = extract_students_from_remote_data(mock_deck)
        
        expected_students = {'João', 'Maria', 'Pedro', 'Ana', 'Carlos'}
        
        print(f"Alunos extraídos: {sorted(students)}")
        print(f"Alunos esperados: {sorted(expected_students)}")
        
        if students == expected_students:
            print("✓ Extração de alunos funcionou corretamente!")
            return True
        else:
            print("✗ Erro na extração de alunos")
            return False
            
    except ImportError as e:
        print(f"Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def test_student_filtering():
    """Testa filtragem de questões por alunos selecionados."""
    print("\nTestando filtragem por alunos...")
    
    questions = [
        {'fields': {'ID': '1', 'ALUNO': 'João', 'PERGUNTA': 'Pergunta 1'}},
        {'fields': {'ID': '2', 'ALUNO': 'Maria', 'PERGUNTA': 'Pergunta 2'}},
        {'fields': {'ID': '3', 'ALUNO': 'João, Pedro', 'PERGUNTA': 'Pergunta 3'}},
        {'fields': {'ID': '4', 'ALUNO': 'Ana', 'PERGUNTA': 'Pergunta 4'}},
        {'fields': {'ID': '5', 'ALUNO': '', 'PERGUNTA': 'Pergunta 5'}},
    ]
    
    selected_students = {'João', 'Maria'}
    
    try:
        from student_manager import filter_questions_by_selected_students
        
        filtered = filter_questions_by_selected_students(questions, selected_students)
        
        # Devem passar: questões 1, 2, 3 (João e/ou Maria estão presentes)
        expected_ids = {'1', '2', '3'}
        actual_ids = {q['fields']['ID'] for q in filtered}
        
        print(f"IDs filtrados: {sorted(actual_ids)}")
        print(f"IDs esperados: {sorted(expected_ids)}")
        
        if actual_ids == expected_ids:
            print("✓ Filtragem de questões funcionou corretamente!")
            return True
        else:
            print("✗ Erro na filtragem de questões")
            return False
            
    except ImportError as e:
        print(f"Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def test_subdeck_naming():
    """Testa geração de nomes de subdecks para alunos."""
    print("\nTestando nomes de subdecks...")
    
    try:
        from student_manager import get_student_subdeck_name
        
        main_deck = "Meu Deck"
        student = "João"
        fields = {
            'IMPORTANCIA': 'Alta',
            'TOPICO': 'Matemática',
            'SUBTOPICO': 'Álgebra',
            'CONCEITO': 'Equações'
        }
        
        result = get_student_subdeck_name(main_deck, student, fields)
        expected = "Meu Deck::João::Alta::Matemática::Álgebra::Equações"
        
        print(f"Nome gerado: {result}")
        print(f"Nome esperado: {expected}")
        
        if result == expected:
            print("✓ Geração de nomes de subdeck funcionou corretamente!")
            return True
        else:
            print("✗ Erro na geração de nomes de subdeck")
            return False
            
    except ImportError as e:
        print(f"Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def test_note_type_naming():
    """Testa geração de nomes de note types para alunos."""
    print("\nTestando nomes de note types...")
    
    try:
        from utils import get_note_type_name
        
        url = "https://docs.google.com/spreadsheets/d/1234567890/export?format=tsv"
        deck_name = "TestDeck"
        student = "João"
        
        basic_name = get_note_type_name(url, deck_name, student=student, is_cloze=False)
        cloze_name = get_note_type_name(url, deck_name, student=student, is_cloze=True)
        
        print(f"Nome Basic: {basic_name}")
        print(f"Nome Cloze: {cloze_name}")
        
        # Verificar se contém elementos esperados
        if (student in basic_name and "Basic" in basic_name and 
            student in cloze_name and "Cloze" in cloze_name):
            print("✓ Geração de nomes de note type funcionou corretamente!")
            return True
        else:
            print("✗ Erro na geração de nomes de note type")
            return False
            
    except ImportError as e:
        print(f"Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=== TESTES DE FUNCIONALIDADE DE ALUNOS ===\n")
    
    tests = [
        test_student_extraction,
        test_student_filtering,
        test_subdeck_naming,
        test_note_type_naming
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"Erro durante teste: {e}")
    
    print(f"\n=== RESULTADO: {passed}/{total} testes passaram ===")
    
    if passed == total:
        print("✓ Todos os testes passaram! A implementação parece estar correta.")
    else:
        print("✗ Alguns testes falharam. Verifique a implementação.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
