#!/usr/bin/env python3
"""
Teste específico para validar as métricas refatoradas do deck remoto.
Este teste verifica se a lógica de contabilização está funcionando corretamente.
"""

import sys
import os

# Adicionar o diretório src ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_remote_deck_metrics():
    """Testa as métricas refatoradas da classe RemoteDeck."""
    
    try:
        from data_processor import RemoteDeck
        import column_definitions as cols
        
        print("=== TESTE DAS MÉTRICAS REFATORADAS ===\n")
        
        # Criar deck de teste
        deck = RemoteDeck('Test Deck', 'http://test.com')
        
        # Dados de teste simulando diferentes cenários de uma planilha
        test_notes = [
            # Linha 1: nota válida com alunos específicos, marcada para sync
            {
                cols.ID: '001', 
                cols.PERGUNTA: 'Pergunta 1', 
                cols.ALUNOS: 'João, Maria', 
                cols.SYNC: 'true'
            },
            
            # Linha 2: nota válida sem alunos, marcada para sync (vai para [MISSING A.])
            {
                cols.ID: '002', 
                cols.PERGUNTA: 'Pergunta 2', 
                cols.ALUNOS: '', 
                cols.SYNC: 'true'
            },
            
            # Linha 3: nota válida com alunos, NÃO marcada para sync
            {
                cols.ID: '003', 
                cols.PERGUNTA: 'Pergunta 3', 
                cols.ALUNOS: 'Pedro', 
                cols.SYNC: 'false'
            },
            
            # Linha 4: linha inválida (sem ID)
            {
                cols.ID: '', 
                cols.PERGUNTA: 'Pergunta 4', 
                cols.ALUNOS: 'Ana', 
                cols.SYNC: 'true'
            },
            
            # Linha 5: nota válida com múltiplos alunos, marcada para sync
            {
                cols.ID: '005', 
                cols.PERGUNTA: 'Pergunta 5', 
                cols.ALUNOS: 'João, Pedro, Ana', 
                cols.SYNC: 'true'
            }
        ]
        
        print("📊 Dados de teste:")
        print(f"- Total de linhas na simulação: {len(test_notes)}")
        print(f"- Linhas com ID preenchido: 4 (001, 002, 003, 005)")
        print(f"- Linhas com ID vazio: 1 (linha 4)")
        print(f"- Linhas marcadas para sync: 4 (001, 002, 005, linha 4)")
        print(f"- Linhas sem aluno: 1 (002)")
        print(f"- Alunos únicos: João, Maria, Pedro, Ana (4 alunos)")
        print()
        
        # Adicionar notas ao deck
        for i, note in enumerate(test_notes, 1):
            print(f"Processando linha {i}: ID='{note.get(cols.ID)}', ALUNOS='{note.get(cols.ALUNOS)}', SYNC='{note.get(cols.SYNC)}'")
            deck.add_note(note)
        
        print()
        
        # Finalizar métricas
        deck.finalize_metrics()
        
        # Obter e mostrar estatísticas
        stats = deck.get_statistics()
        
        print("=== MÉTRICAS CALCULADAS ===")
        print(f"1. Total de linhas na tabela: {stats['total_table_lines']}")
        print(f"2. Linhas com notas válidas (ID preenchido): {stats['valid_note_lines']}")
        print(f"3. Linhas inválidas (ID vazio): {stats['invalid_note_lines']}")
        print(f"4. Linhas marcadas para sincronizar: {stats['sync_marked_lines']}")
        print(f"5. Total potencial de notas no Anki: {stats['total_potential_anki_notes']}")
        print(f"6. Potencial de notas para alunos específicos: {stats['potential_student_notes']}")
        print(f"7. Potencial de notas para [MISSING A.]: {stats['potential_missing_a_notes']}")
        print(f"8. Total de alunos únicos: {stats['unique_students_count']}")
        print(f"9. Notas por aluno (detalhado):")
        for student, count in sorted(stats['notes_per_student'].items()):
            print(f"   • {student}: {count} notas")
        
        print("\n=== VALIDAÇÃO DAS MÉTRICAS ===")
        
        # Validações esperadas
        expected_total_lines = 5
        expected_valid_lines = 4  # 001, 002, 003, 005
        expected_invalid_lines = 1  # linha sem ID
        expected_sync_lines = 3  # 001, 002, 005 (linha 4 tem sync=true mas ID vazio, não conta)
        expected_missing_a = 1  # nota 002
        expected_student_notes = 6  # 001(2 alunos) + 003(1 aluno) + 005(3 alunos)
        expected_total_potential = 7  # 6 student notes + 1 missing_a
        expected_unique_students = 4  # João, Maria, Pedro, Ana
        
        # Verificar cada métrica
        errors = []
        
        if stats['total_table_lines'] != expected_total_lines:
            errors.append(f"total_table_lines: esperado {expected_total_lines}, obtido {stats['total_table_lines']}")
        
        if stats['valid_note_lines'] != expected_valid_lines:
            errors.append(f"valid_note_lines: esperado {expected_valid_lines}, obtido {stats['valid_note_lines']}")
        
        if stats['invalid_note_lines'] != expected_invalid_lines:
            errors.append(f"invalid_note_lines: esperado {expected_invalid_lines}, obtido {stats['invalid_note_lines']}")
        
        if stats['sync_marked_lines'] != expected_sync_lines:
            errors.append(f"sync_marked_lines: esperado {expected_sync_lines}, obtido {stats['sync_marked_lines']}")
        
        if stats['potential_missing_a_notes'] != expected_missing_a:
            errors.append(f"potential_missing_a_notes: esperado {expected_missing_a}, obtido {stats['potential_missing_a_notes']}")
        
        if stats['potential_student_notes'] != expected_student_notes:
            errors.append(f"potential_student_notes: esperado {expected_student_notes}, obtido {stats['potential_student_notes']}")
        
        if stats['total_potential_anki_notes'] != expected_total_potential:
            errors.append(f"total_potential_anki_notes: esperado {expected_total_potential}, obtido {stats['total_potential_anki_notes']}")
        
        if stats['unique_students_count'] != expected_unique_students:
            errors.append(f"unique_students_count: esperado {expected_unique_students}, obtido {stats['unique_students_count']}")
        
        # Validar notas por aluno individual
        expected_per_student = {'João': 2, 'Maria': 1, 'Pedro': 2, 'Ana': 1, '[MISSING A.]': 1}
        for student, expected_count in expected_per_student.items():
            actual_count = stats['notes_per_student'].get(student, 0)
            if actual_count != expected_count:
                errors.append(f"notes_per_student[{student}]: esperado {expected_count}, obtido {actual_count}")
        
        # Mostrar resultado da validação
        if errors:
            print("❌ ERROS ENCONTRADOS:")
            for error in errors:
                print(f"   • {error}")
            return False
        else:
            print("✅ TODAS AS MÉTRICAS ESTÃO CORRETAS!")
            print("✅ Validação das métricas passou com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_remote_deck_metrics()
    sys.exit(0 if success else 1)
