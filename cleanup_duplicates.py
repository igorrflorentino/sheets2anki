#!/usr/bin/env python3
"""Script temporário para limpar duplicados no meta.json"""

import sys
import os
import json

def cleanup_duplicate_note_types_in_config():
    """
    Remove note types duplicados da configuração, mantendo apenas os IDs mais recentes
    para cada combinação de student + tipo (Basic/Cloze).
    
    Returns:
        int: Número de duplicados removidos
    """
    try:
        meta_file = "meta.json"
        
        print(f"[CLEANUP_DUPLICATES] Iniciando limpeza de duplicados na configuração...")
        
        # Ler meta.json
        if not os.path.exists(meta_file):
            print(f"[CLEANUP_DUPLICATES] Arquivo {meta_file} não encontrado")
            return 0
        
        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        if not meta or "decks" not in meta:
            print(f"[CLEANUP_DUPLICATES] Nenhuma configuração de decks encontrada")
            return 0
        
        total_removed = 0
        
        for publication_key, deck_info in meta["decks"].items():
            if "note_types" not in deck_info or not deck_info["note_types"]:
                continue
            
            print(f"[CLEANUP_DUPLICATES] Processando deck {publication_key}...")
            
            # Agrupar note types por student + tipo
            student_type_groups = {}  # {student_type: [{'id': id, 'name': name}]}
            
            for note_type_id_str, note_type_name in deck_info["note_types"].items():
                # Extrair student e tipo do nome
                # Formato: "Sheets2Anki - {remote_deck_name} - {student} - {Basic|Cloze}"
                parts = note_type_name.split(" - ")
                if len(parts) >= 3:
                    student_and_type = " - ".join(parts[-2:])  # "{student} - {Basic|Cloze}"
                    
                    if student_and_type not in student_type_groups:
                        student_type_groups[student_and_type] = []
                    
                    student_type_groups[student_and_type].append({
                        'id': note_type_id_str,
                        'name': note_type_name
                    })
            
            # Para cada grupo, manter apenas o ID mais recente (maior valor numérico)
            cleaned_note_types = {}
            removed_count = 0
            
            for student_type, group in student_type_groups.items():
                if len(group) > 1:
                    # Ordenar por ID (mais recente = maior valor)
                    group_sorted = sorted(group, key=lambda x: int(x['id']))
                    keep_item = group_sorted[-1]  # Último (maior ID)
                    
                    print(f"[CLEANUP_DUPLICATES] Duplicados para '{student_type}':")
                    for item in group_sorted:
                        if item['id'] == keep_item['id']:
                            print(f"  ✅ MANTER: ID {item['id']} - '{item['name']}'")
                            cleaned_note_types[item['id']] = item['name']
                        else:
                            print(f"  ❌ REMOVER: ID {item['id']} - '{item['name']}'")
                            removed_count += 1
                else:
                    # Apenas um item, manter
                    item = group[0]
                    cleaned_note_types[item['id']] = item['name']
            
            # Atualizar a configuração se houver mudanças
            if removed_count > 0:
                deck_info["note_types"] = cleaned_note_types
                total_removed += removed_count
                print(f"[CLEANUP_DUPLICATES] Removidos {removed_count} duplicados do deck {publication_key}")
        
        # Salvar se houve mudanças
        if total_removed > 0:
            with open(meta_file, 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=4, ensure_ascii=False)
            print(f"[CLEANUP_DUPLICATES] ✅ Limpeza concluída: {total_removed} duplicados removidos da configuração")
        else:
            print(f"[CLEANUP_DUPLICATES] Nenhum duplicado encontrado")
        
        return total_removed
        
    except Exception as e:
        print(f"[CLEANUP_DUPLICATES] Erro na limpeza: {e}")
        import traceback
        traceback.print_exc()
        return 0

if __name__ == "__main__":
    result = cleanup_duplicate_note_types_in_config()
    print(f'Total de duplicados removidos: {result}')
