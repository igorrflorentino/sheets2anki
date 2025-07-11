#!/usr/bin/env python3
"""
Teste para verificar se o campo SYNC? não é incluído nas notas do Anki.
"""

import sys
import os

# Adicionar os diretórios necessários ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_sync_field_not_in_notes():
    """Testa se o campo SYNC? não é incluído nas notas do Anki."""
    from src.column_definitions import NOTE_FIELDS, REQUIRED_COLUMNS, SYNC
    
    print("🧪 Testando se SYNC? não é incluído nas notas...")
    
    # Verificar se SYNC? não está em NOTE_FIELDS
    sync_not_in_notes = SYNC not in NOTE_FIELDS
    status = "✅" if sync_not_in_notes else "❌"
    print(f"  {status} SYNC? não está em NOTE_FIELDS: {sync_not_in_notes}")
    
    # Verificar se SYNC? ainda está em REQUIRED_COLUMNS (para validação)
    sync_in_required = SYNC in REQUIRED_COLUMNS
    status = "✅" if sync_in_required else "❌"
    print(f"  {status} SYNC? ainda está em REQUIRED_COLUMNS: {sync_in_required}")
    
    # Verificar se NOTE_FIELDS tem uma coluna a menos que REQUIRED_COLUMNS
    expected_difference = 1  # Apenas SYNC? deve estar faltando
    actual_difference = len(REQUIRED_COLUMNS) - len(NOTE_FIELDS)
    difference_ok = actual_difference == expected_difference
    status = "✅" if difference_ok else "❌"
    print(f"  {status} Diferença entre REQUIRED_COLUMNS e NOTE_FIELDS: {actual_difference} (esperado: {expected_difference})")
    
    print(f"  📋 Total de colunas obrigatórias: {len(REQUIRED_COLUMNS)}")
    print(f"  📋 Total de campos nas notas: {len(NOTE_FIELDS)}")
    print(f"  📋 Campos excluídos das notas: {set(REQUIRED_COLUMNS) - set(NOTE_FIELDS)}")
    
    return sync_not_in_notes and sync_in_required and difference_ok

def test_note_processing_excludes_sync():
    """Testa se o processamento de notas exclui o campo SYNC?."""
    from src.column_definitions import NOTE_FIELDS, SYNC
    
    print("\n🧪 Testando se processamento de notas exclui SYNC?...")
    
    # Simular campos de uma questão (incluindo SYNC?)
    test_fields = {
        'ID': '001',
        'PERGUNTA': 'Qual é a capital do Brasil?',
        'LEVAR PARA PROVA': 'Brasília',
        'SYNC?': 'true',  # Este campo não deve ser processado na nota
        'INFO COMPLEMENTAR': 'Informação complementar',
        'TOPICO': 'Geografia'
    }
    
    # Contar quantos campos seriam processados para a nota
    note_fields_count = 0
    excluded_fields = []
    
    for field_name, value in test_fields.items():
        if field_name in NOTE_FIELDS:
            note_fields_count += 1
        else:
            excluded_fields.append(field_name)
    
    # Verificar se apenas SYNC? foi excluído
    sync_only_excluded = excluded_fields == ['SYNC?']
    status = "✅" if sync_only_excluded else "❌"
    print(f"  {status} Apenas SYNC? foi excluído: {sync_only_excluded}")
    
    print(f"  📋 Campos que seriam incluídos na nota: {note_fields_count}")
    print(f"  📋 Campos excluídos: {excluded_fields}")
    print(f"  📋 Total de campos no teste: {len(test_fields)}")
    
    return sync_only_excluded

def test_card_template_excludes_sync():
    """Testa se o template do card não inclui o campo SYNC?."""
    from src.card_templates import create_card_template
    
    print("\n🧪 Testando se template do card exclui SYNC?...")
    
    # Criar template padrão
    template = create_card_template(is_cloze=False)
    
    # Verificar se SYNC? não está presente nos templates
    qfmt_has_sync = 'SYNC?' in template['qfmt']
    afmt_has_sync = 'SYNC?' in template['afmt']
    
    template_clean = not qfmt_has_sync and not afmt_has_sync
    status = "✅" if template_clean else "❌"
    print(f"  {status} Template não contém SYNC?: {template_clean}")
    
    if qfmt_has_sync:
        print(f"  ❌ SYNC? encontrado no template da pergunta")
    if afmt_has_sync:
        print(f"  ❌ SYNC? encontrado no template da resposta")
    
    return template_clean

def main():
    """Função principal do teste."""
    print("🔍 Testando se SYNC? não é incluído nas notas do Anki...\n")
    
    try:
        test1 = test_sync_field_not_in_notes()
        test2 = test_note_processing_excludes_sync()
        test3 = test_card_template_excludes_sync()
        
        success = test1 and test2 and test3
        
        print(f"\n{'✅' if success else '❌'} Resultado final:")
        print(f"  {'✅' if test1 else '❌'} SYNC? não está em NOTE_FIELDS")
        print(f"  {'✅' if test2 else '❌'} Processamento exclui SYNC?")
        print(f"  {'✅' if test3 else '❌'} Template não contém SYNC?")
        
        if success:
            print("\n🎉 Todos os testes passaram!")
            print("   A coluna SYNC? é usada apenas para controle interno.")
            print("   Ela não aparece nas notas do Anki.")
        else:
            print("\n⚠️  Alguns testes falharam!")
            print("   Verifique se SYNC? está sendo incluído nas notas.")
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
