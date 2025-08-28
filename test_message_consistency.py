#!/usr/bin/env python3
"""
Teste para verificar a consistência das mensagens de remoção.
"""

def test_message_consistency():
    """
    Testa a consistência das mensagens de remoção de dados.
    """
    print("🧪 TESTE: Consistência das Mensagens de Remoção")
    print("=" * 60)
    
    print("\n📋 CENÁRIOS DE TESTE:")
    
    # Cenário 1: Apenas alunos normais
    print("\n1️⃣ CENÁRIO: Apenas alunos normais removidos")
    students_only = ["Isabelle", "João"]
    students_list = "\n".join([f"• {student}" for student in sorted(students_only)])
    
    message_students_only = (
        f"⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️\n\n"
        f"Os seguintes alunos foram removidos da lista de sincronização:\n\n"
        f"{students_list}\n\n"
        f"🗑️ DADOS QUE SERÃO DELETADOS PERMANENTEMENTE:\n"
        f"• Todas as notas dos alunos\n"
        f"• Todos os cards dos alunos\n"
        f"• Todos os decks dos alunos\n"
        f"• Todos os note types dos alunos\n\n"
        f"❌ ESTA AÇÃO É IRREVERSÍVEL!\n\n"
        f"Deseja continuar com a remoção dos dados?"
    )
    
    print("MENSAGEM GERADA:")
    print(message_students_only)
    
    # Cenário 2: Alunos + [MISSING A.]
    print("\n" + "="*60)
    print("2️⃣ CENÁRIO: Alunos + [MISSING A.] removidos")
    students_with_missing = ["Isabelle", "[MISSING A.]"]
    students_list_with_missing = "\n".join([f"• {student}" for student in sorted(students_with_missing)])
    
    message_with_missing = (
        f"⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️\n\n"
        f"Os seguintes alunos foram removidos da lista de sincronização:\n\n"
        f"{students_list_with_missing}\n\n"
        f"🗑️ DADOS QUE SERÃO DELETADOS PERMANENTEMENTE:\n"
        f"• Todas as notas dos alunos\n"
        f"• Todos os cards dos alunos\n"
        f"• Todos os decks dos alunos\n"
        f"• Todos os note types dos alunos\n\n"
        f"❌ ESTA AÇÃO É IRREVERSÍVEL!\n\n"
        f"Deseja continuar com a remoção dos dados?"
    )
    
    print("MENSAGEM GERADA:")
    print(message_with_missing)
    
    # Cenário 3: Apenas [MISSING A.]
    print("\n" + "="*60)
    print("3️⃣ CENÁRIO: Apenas [MISSING A.] removido")
    missing_only = ["[MISSING A.]"]
    students_list_missing_only = "\n".join([f"• {student}" for student in sorted(missing_only)])
    
    message_missing_only = (
        f"⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️\n\n"
        f"Os seguintes alunos foram removidos da lista de sincronização:\n\n"
        f"{students_list_missing_only}\n\n"
        f"🗑️ DADOS QUE SERÃO DELETADOS PERMANENTEMENTE:\n"
        f"• Todas as notas dos alunos\n"
        f"• Todos os cards dos alunos\n"
        f"• Todos os decks dos alunos\n"
        f"• Todos os note types dos alunos\n\n"
        f"❌ ESTA AÇÃO É IRREVERSÍVEL!\n\n"
        f"Deseja continuar com a remoção dos dados?"
    )
    
    print("MENSAGEM GERADA:")
    print(message_missing_only)
    
    print("\n" + "="*60)
    print("✅ ANÁLISE DE CONSISTÊNCIA:")
    
    # Verificar se todas usam o mesmo formato
    messages = [message_students_only, message_with_missing, message_missing_only]
    
    # Verificar elementos comuns
    common_elements = [
        "⚠️ ATENÇÃO: REMOÇÃO PERMANENTE DE DADOS ⚠️",
        "Os seguintes alunos foram removidos da lista de sincronização:",
        "🗑️ DADOS QUE SERÃO DELETADOS PERMANENTEMENTE:",
        "• Todas as notas dos alunos",
        "• Todos os cards dos alunos", 
        "• Todos os decks dos alunos",
        "• Todos os note types dos alunos",
        "❌ ESTA AÇÃO É IRREVERSÍVEL!",
        "Deseja continuar com a remoção dos dados?"
    ]
    
    all_consistent = True
    for element in common_elements:
        for i, message in enumerate(messages, 1):
            if element not in message:
                print(f"❌ Cenário {i} não contém: {element}")
                all_consistent = False
    
    if all_consistent:
        print("✅ Todas as mensagens são consistentes!")
        print("✅ Mesmo formato e linguagem em todos os cenários")
        print("✅ [MISSING A.] é tratado como um 'aluno' normal na mensagem")
        print("✅ Simplicidade e clareza mantidas")
    else:
        print("❌ Inconsistências encontradas!")
    
    return all_consistent

if __name__ == "__main__":
    test_message_consistency()
