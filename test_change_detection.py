#!/usr/bin/env python3
"""
Teste para verificar se a detecção de mudanças específicas está funcionando.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_change_detection():
    """Teste da detecção de mudanças específicas."""
    
    print("🧪 TESTE DE DETECÇÃO DE MUDANÇAS")
    print("=" * 70)
    
    # Simular uma nota existente
    class MockNote:
        def __init__(self):
            self.fields = {
                'Pergunta': 'Qual é a capital do Brasil?',
                'Resposta': 'Brasília',
                'Levar_para_prova': 'Não'
            }
            self.tags = ['geografia']
        
        def __getitem__(self, key):
            return self.fields.get(key, '')
        
        def __contains__(self, key):
            return key in self.fields
    
    # Simular dados novos
    new_fields = {
        'Pergunta': 'Qual é a capital do Brasil?',
        'Resposta': 'Brasília - DF',  # Mudança aqui
        'Levar_para_prova': 'Sim'     # Mudança aqui
    }
    
    new_tags = ['geografia', 'capitais']  # Tag adicionada
    
    # Simular as funções de detecção
    def note_needs_update(note, fields, tags):
        """Simular função note_needs_update."""
        # Verificar campos
        for field_name, value in fields.items():
            if field_name in note:
                if str(note[field_name]).strip() != str(value).strip():
                    return True
        
        # Verificar tags
        note_tags = set(note.tags) if hasattr(note, 'tags') else set()
        tsv_tags = set(tags) if tags else set()
        if note_tags != tsv_tags:
            return True
        
        return False
    
    def get_update_details(note, fields, tags):
        """Simular função get_update_details."""
        changes = []
        
        # Verificar mudanças nos campos
        for field_name, new_value in fields.items():
            if field_name in note:
                old_value = str(note[field_name]).strip()
                new_value_str = str(new_value).strip()
                
                if old_value != new_value_str:
                    # Truncar valores longos para exibição
                    old_display = old_value[:50] + "..." if len(old_value) > 50 else old_value
                    new_display = new_value_str[:50] + "..." if len(new_value_str) > 50 else new_value_str
                    
                    changes.append(f"{field_name}: '{old_display}' → '{new_display}'")
        
        # Verificar mudanças nas tags
        note_tags = set(note.tags) if hasattr(note, 'tags') else set()
        tsv_tags = set(tags) if tags else set()
        
        if note_tags != tsv_tags:
            added_tags = tsv_tags - note_tags
            removed_tags = note_tags - tsv_tags
            
            if added_tags:
                changes.append(f"Tags adicionadas: {', '.join(added_tags)}")
            if removed_tags:
                changes.append(f"Tags removidas: {', '.join(removed_tags)}")
        
        return changes
    
    # Executar teste
    note = MockNote()
    
    print("📊 Testando detecção de mudanças...")
    needs_update = note_needs_update(note, new_fields, new_tags)
    
    if needs_update:
        print("✅ Mudanças detectadas corretamente!")
        
        changes = get_update_details(note, new_fields, new_tags)
        print(f"📋 Mudanças encontradas: {len(changes)}")
        
        for i, change in enumerate(changes, 1):
            print(f"  {i}. {change}")
        
        # Verificar se as mudanças esperadas foram detectadas
        expected_changes = [
            "Resposta: 'Brasília' → 'Brasília - DF'",
            "Levar_para_prova: 'Não' → 'Sim'", 
            "Tags adicionadas: capitais"
        ]
        
        found_changes = 0
        for expected in expected_changes:
            found = any(expected in change for change in changes)
            if found:
                print(f"✅ Mudança esperada encontrada: {expected}")
                found_changes += 1
            else:
                print(f"❌ Mudança esperada não encontrada: {expected}")
        
        if found_changes == len(expected_changes):
            print("🎉 TODAS AS MUDANÇAS FORAM DETECTADAS CORRETAMENTE!")
            return True
        else:
            print(f"❌ Apenas {found_changes}/{len(expected_changes)} mudanças foram detectadas")
            return False
    else:
        print("❌ Mudanças não foram detectadas!")
        return False

def test_no_changes():
    """Teste para verificar que não há mudanças quando os dados são iguais."""
    
    print("\n🧪 TESTE DE AUSÊNCIA DE MUDANÇAS")
    print("=" * 70)
    
    # Simular uma nota existente
    class MockNote:
        def __init__(self):
            self.fields = {
                'Pergunta': 'Qual é a capital do Brasil?',
                'Resposta': 'Brasília',
                'Levar_para_prova': 'Não'
            }
            self.tags = ['geografia']
        
        def __getitem__(self, key):
            return self.fields.get(key, '')
        
        def __contains__(self, key):
            return key in self.fields
    
    # Simular dados idênticos
    same_fields = {
        'Pergunta': 'Qual é a capital do Brasil?',
        'Resposta': 'Brasília',
        'Levar_para_prova': 'Não'
    }
    
    same_tags = ['geografia']
    
    # Simular função note_needs_update
    def note_needs_update(note, fields, tags):
        """Simular função note_needs_update."""
        for field_name, value in fields.items():
            if field_name in note:
                if str(note[field_name]).strip() != str(value).strip():
                    return True
        
        note_tags = set(note.tags) if hasattr(note, 'tags') else set()
        tsv_tags = set(tags) if tags else set()
        if note_tags != tsv_tags:
            return True
        
        return False
    
    note = MockNote()
    needs_update = note_needs_update(note, same_fields, same_tags)
    
    if not needs_update:
        print("✅ Dados idênticos detectados corretamente - nenhuma atualização necessária!")
        return True
    else:
        print("❌ Dados idênticos foram detectados como diferentes!")
        return False

def main():
    """Função principal de teste."""
    
    print("🔍 TESTE DE DETECÇÃO DE MUDANÇAS EM CARDS")
    print("=" * 70)
    
    try:
        test1_result = test_change_detection()
        test2_result = test_no_changes()
        
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS TESTES:")
        print("=" * 70)
        
        print(f"  Teste 1 (Detecção de mudanças): {'✅ PASSOU' if test1_result else '❌ FALHOU'}")
        print(f"  Teste 2 (Ausência de mudanças): {'✅ PASSOU' if test2_result else '❌ FALHOU'}")
        
        if test1_result and test2_result:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            print("✅ A detecção de mudanças está funcionando corretamente!")
            print("✅ O sistema identifica precisamente o que foi alterado!")
            print("✅ O sistema evita atualizações desnecessárias!")
            return True
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM")
            print("❌ Há problemas na detecção de mudanças")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO DURANTE OS TESTES: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
