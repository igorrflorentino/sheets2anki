#!/usr/bin/env python3
"""
Teste das funcionalidades de detalhamento de mudanças.
Este arquivo demonstra como funcionam os novos detalhes de mudanças implementados.
"""

def test_update_details_display():
    """Testa a exibição de detalhes de mudanças."""
    
    # Exemplo das estatísticas que seriam retornadas pela sincronização
    total_stats = {
        'created': 2,
        'updated': 3,
        'deleted': 1,
        'errors': 0,
        'skipped': 0,
        'unchanged': 4,
        'total_remote': 10,
        
        # Detalhes das criações
        'creation_details': [
            {
                'student_note_id': 'João_001',
                'student': 'João',
                'note_id': '001',
                'pergunta': 'Qual é a capital do Brasil?'
            },
            {
                'student_note_id': 'Maria_002',
                'student': 'Maria',
                'note_id': '002',
                'pergunta': 'Como calcular a área de um triângulo?'
            }
        ],
        
        # Detalhes das atualizações
        'update_details': [
            {
                'student_note_id': 'João_003',
                'student': 'João',
                'note_id': '003',
                'changes': [
                    "MATCH: 'Brasília' → 'A capital é Brasília'",
                    "IMPORTANCIA: '3' → '4'"
                ]
            },
            {
                'student_note_id': 'Maria_004',
                'student': 'Maria',
                'note_id': '004',
                'changes': [
                    "PERGUNTA: 'Qual a fórmula?' → 'Qual a fórmula da área?'",
                    "MATCH: 'base * altura / 2' → '(base × altura) ÷ 2'",
                    "EXEMPLO_1: '' → 'Triângulo com base 5 e altura 4: (5×4)÷2 = 10'"
                ]
            },
            {
                'student_note_id': '[MISSING A.]_005',
                'student': '[MISSING A.]',
                'note_id': '005',
                'changes': [
                    "TOPICO: 'Geografia' → 'História'"
                ]
            }
        ],
        
        # Detalhes das exclusões
        'deletion_details': [
            {
                'student_note_id': 'Pedro_006',
                'student': 'Pedro',
                'note_id': '006',
                'pergunta': 'Pergunta que não existe mais na planilha'
            }
        ]
    }
    
    # Simular a geração da mensagem como seria exibida ao usuário
    summary = []
    
    # Estatísticas principais
    summary.append("✅ Sincronização concluída com sucesso!")
    summary.append("📊 Decks: 1/1 sincronizados")
    
    # Estatísticas de notas com detalhes
    if total_stats.get('created', 0) > 0:
        summary.append(f"➕ {total_stats['created']} notas criadas")
        # Mostrar detalhes das criações
        if total_stats.get('creation_details'):
            summary.append("   Detalhes das notas criadas:")
            for detail in total_stats['creation_details'][:10]:
                summary.append(f"   • {detail['student']}: {detail['note_id']} - {detail['pergunta']}")
    
    if total_stats.get('updated', 0) > 0:
        summary.append(f"✏️ {total_stats['updated']} notas atualizadas")
        # Mostrar detalhes das atualizações
        if total_stats.get('update_details'):
            summary.append("   Detalhes das mudanças:")
            for detail in total_stats['update_details'][:10]:
                changes_text = "; ".join(detail['changes'][:3])  # Primeiras 3 mudanças
                if len(detail['changes']) > 3:
                    changes_text += f" ... (+{len(detail['changes']) - 3} mais)"
                summary.append(f"   • {detail['student']}: {detail['note_id']} - {changes_text}")
    
    if total_stats.get('deleted', 0) > 0:
        summary.append(f"🗑️ {total_stats['deleted']} notas deletadas")
        # Mostrar detalhes das exclusões
        if total_stats.get('deletion_details'):
            summary.append("   Detalhes das notas removidas:")
            for detail in total_stats['deletion_details'][:10]:
                summary.append(f"   • {detail['student']}: {detail['note_id']} - {detail['pergunta']}")
    
    if total_stats.get('unchanged', 0) > 0:
        summary.append(f"⏭️ {total_stats['unchanged']} notas inalteradas")
    
    # Exibir resultado
    print("=" * 60)
    print("EXEMPLO DE MENSAGEM DE SINCRONIZAÇÃO COM DETALHES")
    print("=" * 60)
    print("\n".join(summary))
    print("=" * 60)

if __name__ == "__main__":
    test_update_details_display()
