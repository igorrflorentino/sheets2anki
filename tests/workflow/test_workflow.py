#!/usr/bin/env python3
"""
Teste de workflow completo do Sheets2Anki.
Simula o fluxo completo de importação de uma planilha.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.parseRemoteDeck import getRemoteDeck
from src.constants import TEST_SHEETS_URLS
from src.column_definitions import REQUIRED_COLUMNS

def test_complete_workflow():
    """Testa o workflow completo de importação."""
    print("🔄 TESTE DE WORKFLOW COMPLETO")
    print("=" * 50)
    
    # Usar primeira URL das constantes
    deck_name, url = TEST_SHEETS_URLS[0]
    print(f"📋 Testando deck: {deck_name}")
    print(f"🔗 URL: {url}")
    
    try:
        # Passo 1: Importar deck
        print("\n--- PASSO 1: Importar Deck ---")
        deck = getRemoteDeck(url)
        print(f"✅ Deck importado com sucesso!")
        print(f"📊 Questões encontradas: {len(deck.questions)}")
        
        # Passo 2: Validar estrutura do deck
        print("\n--- PASSO 2: Validar Estrutura ---")
        if hasattr(deck, 'deckName'):
            print(f"✅ Nome do deck: {deck.deckName}")
        else:
            print("❌ Deck sem nome")
            
        if hasattr(deck, 'questions') and deck.questions:
            print(f"✅ Questões disponíveis: {len(deck.questions)}")
            
            # Analisar primeira questão
            first_question = deck.questions[0]
            if isinstance(first_question, dict):
                print(f"📝 Primeira questão (dict):")
                for key, value in first_question.items():
                    if isinstance(value, str) and len(value) > 50:
                        print(f"  {key}: {value[:50]}...")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"📝 Primeira questão (objeto): {type(first_question)}")
                if hasattr(first_question, '__dict__'):
                    for key, value in first_question.__dict__.items():
                        if isinstance(value, str) and len(value) > 50:
                            print(f"  {key}: {value[:50]}...")
                        else:
                            print(f"  {key}: {value}")
        else:
            print("❌ Deck sem questões")
            
        # Passo 3: Verificar campos obrigatórios
        print("\n--- PASSO 3: Verificar Campos ---")
        if deck.questions:
            question = deck.questions[0]
            if isinstance(question, dict):
                available_fields = set(question.keys())
                required_fields = set(REQUIRED_COLUMNS)
                
                missing_fields = required_fields - available_fields
                extra_fields = available_fields - required_fields
                
                if not missing_fields:
                    print("✅ Todos os campos obrigatórios presentes")
                else:
                    print(f"❌ Campos faltantes: {missing_fields}")
                    
                if extra_fields:
                    print(f"ℹ️  Campos extras: {extra_fields}")
                    
                print(f"📊 Total de campos: {len(available_fields)}")
        
        # Passo 4: Analisar conteúdo
        print("\n--- PASSO 4: Analisar Conteúdo ---")
        if deck.questions:
            non_empty_questions = 0
            with_sync_true = 0
            with_formula_errors = 0
            
            for question in deck.questions:
                if isinstance(question, dict):
                    # Verificar se tem conteúdo
                    if question.get('PERGUNTA', '').strip():
                        non_empty_questions += 1
                    
                    # Verificar SYNC
                    sync_value = question.get('SYNC?', '').strip().lower()
                    if sync_value in ['true', '1', 'sim', 'yes', 'verdadeiro', 'v', '']:
                        with_sync_true += 1
                    
                    # Verificar erros de fórmula
                    for field_name, field_value in question.items():
                        if isinstance(field_value, str) and (field_value.startswith('#') or field_value.startswith('=')):
                            with_formula_errors += 1
                            break
            
            print(f"📊 Questões com conteúdo: {non_empty_questions}")
            print(f"📊 Questões para sincronizar: {with_sync_true}")
            print(f"📊 Questões com erros de fórmula: {with_formula_errors}")
        
        print(f"\n✅ WORKFLOW COMPLETO EXECUTADO COM SUCESSO!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO WORKFLOW: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_urls():
    """Testa múltiplas URLs das constantes."""
    print("\n🔄 TESTE DE MÚLTIPLAS URLS")
    print("=" * 50)
    
    results = []
    for i, (name, url) in enumerate(TEST_SHEETS_URLS, 1):
        print(f"\n--- URL {i}: {name} ---")
        
        try:
            deck = getRemoteDeck(url)
            print(f"✅ Sucesso: {len(deck.questions)} questões")
            results.append(True)
        except Exception as e:
            print(f"❌ Erro: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) if results else 0
    print(f"\n📊 Taxa de sucesso: {success_rate:.1%}")
    
    return success_rate == 1.0

def test_workflow_with_local_data():
    """Testa workflow com dados locais."""
    print("\n🔄 TESTE DE WORKFLOW COM DADOS LOCAIS")
    print("=" * 50)
    
    from src.parseRemoteDeck import build_remote_deck_from_tsv
    
    # Dados de teste locais
    test_data = [
        REQUIRED_COLUMNS,
        ['1', 'Pergunta teste', 'Resposta teste', 'true', 'Info complementar', 'Info detalhada', 'Ex1', 'Ex2', 'Ex3', 'Tópico', 'Subtópico', 'Conceito', 'Banca', '2023', 'Carreira', 'Alta', 'tag1,tag2']
    ]
    
    try:
        deck = build_remote_deck_from_tsv(test_data)
        print(f"✅ Deck local criado: {len(deck.questions)} questões")
        
        if deck.questions:
            question = deck.questions[0]
            print(f"📝 Questão de teste:")
            if isinstance(question, dict):
                print(f"  ID: {question.get('id', 'N/A')}")
                print(f"  Pergunta: {question.get('question', 'N/A')}")
                print(f"  Resposta: {question.get('levar_para_prova', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no workflow local: {e}")
        return False

def main():
    """Executa todos os testes de workflow."""
    print("🔍 TESTES DE WORKFLOW - SHEETS2ANKI")
    print("=" * 60)
    
    # Executar todos os testes
    results = []
    results.append(test_complete_workflow())
    results.append(test_multiple_urls())
    results.append(test_workflow_with_local_data())
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES DE WORKFLOW")
    
    passed = sum(results)
    total = len(results)
    success_rate = passed / total if total > 0 else 0
    
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {passed}")
    print(f"Testes falharam: {total - passed}")
    print(f"Taxa de sucesso: {success_rate:.1%}")
    
    if success_rate == 1.0:
        print("🎉 TODOS OS TESTES DE WORKFLOW PASSARAM!")
    else:
        print("⚠️  ALGUNS TESTES DE WORKFLOW FALHARAM!")
    
    return success_rate == 1.0

if __name__ == "__main__":
    main()
