
# """
# Módulo de Comparação de Decks do Anki

# Este módulo implementa funcionalidades para comparar decks do Anki e identificar
# diferenças entre o estado atual e uma fonte remota, permitindo sincronização
# bidirecional inteligente.

# Funcionalidades principais:
# - Comparação entre deck remoto e deck local do Anki
# - Identificação de notas novas, atualizadas e removidas
# - Detecção automática de campos-chave ("Text" ou "Front")
# - Suporte a diferentes estruturas de notas
# - Análise de diferenças campo por campo

# Fluxo de processamento:
# 1. Construção de índice de notas existentes no Anki
# 2. Comparação nota por nota do deck remoto
# 3. Identificação de notas novas e atualizadas
# 4. Detecção de notas removidas da fonte remota
# 5. Retorno de relatório estruturado de diferenças

# Funções principais:
# - diffAnkiDecks(): Função principal de comparação
# - determine_key_field(): Determina campo-chave da nota
# - _build_stored_notes_index(): Constrói índice de notas armazenadas
# - _find_new_and_updated_questions(): Identifica notas novas e atualizadas
# - _find_removed_questions(): Identifica notas removidas

# Autor: Sheets2Anki Project
# """

# # =============================================================================
# # IMPORTS
# # =============================================================================

# try:
#     from aqt.utils import showInfo
# except ImportError:
#     # Graceful fallback para ambientes sem Anki
#     pass

# from .libs.org_to_anki.ankiConnectWrapper.AnkiNoteBuilder import AnkiNoteBuilder

# # =============================================================================
# # UTILITY FUNCTIONS
# # =============================================================================

# def determine_key_field(note):
#     """
#     Determina qual campo usar como chave para uma nota ("Text" ou "Front").
    
#     Esta função identifica automaticamente o campo-chave baseado na estrutura
#     da nota, priorizando "Text" sobre "Front" quando ambos estão presentes.
    
#     Args:
#         note (dict): Dicionário representando a nota do Anki
        
#     Returns:
#         str or None: Nome do campo-chave ("Text", "Front") ou None se não encontrado
        
#     Examples:
#         >>> note = {"fields": {"Text": {"value": "Pergunta"}, "Back": {"value": "Resposta"}}}
#         >>> determine_key_field(note)
#         'Text'
        
#         >>> note = {"fields": {"Front": {"value": "Pergunta"}, "Back": {"value": "Resposta"}}}
#         >>> determine_key_field(note)
#         'Front'
#     """
#     if not isinstance(note, dict):
#         return None
    
#     fields = note.get("fields", {})
    
#     # Priorizar "Text" sobre "Front"
#     if "Text" in fields:
#         return "Text"
#     elif "Front" in fields:
#         return "Front"
    
#     return None

# # =============================================================================
# # MAIN COMPARISON FUNCTION
# # =============================================================================

# def diffAnkiDecks(orgAnkiDeck, ankiBaseDeck):
#     """
#     Compara um deck remoto com um deck base do Anki e identifica diferenças.
    
#     Esta função realiza uma comparação completa entre dois decks, identificando:
#     - Notas novas que precisam ser adicionadas
#     - Notas existentes que foram atualizadas
#     - Notas que foram removidas da fonte remota
    
#     Args:
#         orgAnkiDeck: Deck remoto/origem com as novas questões
#         ankiBaseDeck (dict): Deck base do Anki para comparação
        
#     Returns:
#         dict: Dicionário com três listas:
#             - newQuestions: Notas que precisam ser adicionadas
#             - questionsUpdated: Notas que precisam ser atualizadas  
#             - removedQuestions: Notas que foram removidas da fonte
            
#     Raises:
#         TypeError: Se ankiBaseDeck não for um dicionário válido
        
#     Examples:
#         >>> result = diffAnkiDecks(remote_deck, anki_deck)
#         >>> print(f"Novas: {len(result['newQuestions'])}")
#         >>> print(f"Atualizadas: {len(result['questionsUpdated'])}")
#         >>> print(f"Removidas: {len(result['removedQuestions'])}")
#     """
#     # Validar parâmetros de entrada
#     if not isinstance(ankiBaseDeck, dict):
#         raise TypeError("AnkiBaseDeck (2º parâmetro) deve ser um dicionário")

#     # 1. Construir índice de notas armazenadas no Anki
#     storedNotes, potentialKeys = _build_stored_notes_index(ankiBaseDeck)
    
#     # 2. Identificar notas novas e atualizadas
#     newQuestions, questionsUpdated = _find_new_and_updated_questions(
#         orgAnkiDeck, storedNotes
#     )
    
#     # 3. Identificar notas removidas da fonte remota
#     removedQuestions = _find_removed_questions(
#         orgAnkiDeck, storedNotes
#     )

#     return {
#         "newQuestions": newQuestions,
#         "questionsUpdated": questionsUpdated,
#         "removedQuestions": removedQuestions
#     }

# # =============================================================================
# # HELPER FUNCTIONS
# # =============================================================================

# def _build_stored_notes_index(ankiBaseDeck):
#     """
#     Constrói um índice das notas armazenadas no deck base do Anki.
    
#     Args:
#         ankiBaseDeck (dict): Deck base do Anki
        
#     Returns:
#         tuple: (storedNotes, potentialKeys) onde:
#             - storedNotes: dict mapeando chaves para notas
#             - potentialKeys: set de tipos de campos-chave encontrados
#     """
#     storedNotes = {}
#     potentialKeys = set()
    
#     for question in ankiBaseDeck.get("result", []):
#         keyField = determine_key_field(question)
#         potentialKeys.add(keyField)
        
#         fields = question.get("fields", {})
#         keyFieldDict = fields.get(keyField, {})
#         key = keyFieldDict.get("value")
        
#         if key is not None:
#             storedNotes[key] = question
    
#     return storedNotes, potentialKeys

# def _find_new_and_updated_questions(orgAnkiDeck, storedNotes):
#     """
#     Identifica questões novas e atualizadas comparando com as armazenadas.
    
#     Args:
#         orgAnkiDeck: Deck remoto com questões atualizadas
#         storedNotes (dict): Índice de notas já armazenadas
        
#     Returns:
#         tuple: (newQuestions, questionsUpdated) listas de questões novas e atualizadas
#     """
#     newQuestions = []
#     questionsUpdated = []
#     noteBuilder = AnkiNoteBuilder()

#     for question in orgAnkiDeck.getQuestions():
#         builtQuestion = noteBuilder.buildNote(question)
#         keyField = determine_key_field(builtQuestion)
#         fields = builtQuestion.get("fields", {})
#         key = fields.get(keyField)

#         savedQuestion = storedNotes.get(key, None)
        
#         if savedQuestion is None:
#             # Nova questão
#             noteId = -1
#             newQuestions.append({"question": question, "noteId": noteId})
#         else:
#             # Verificar se questão foi atualizada
#             if _is_question_updated(savedQuestion, fields):
#                 noteId = savedQuestion.get("noteId", -1)
#                 questionsUpdated.append({"question": question, "noteId": noteId})

#     return newQuestions, questionsUpdated

# def _is_question_updated(savedQuestion, newFields):
#     """
#     Verifica se uma questão foi atualizada comparando campos.
    
#     Args:
#         savedQuestion (dict): Questão salva no Anki
#         newFields (dict): Campos da nova versão da questão
        
#     Returns:
#         bool: True se a questão foi atualizada, False caso contrário
#     """
#     savedFields = savedQuestion.get("fields", {})
    
#     for field_name in savedFields.keys():
#         saved_value = savedFields.get(field_name, {}).get("value")
#         built_value = newFields.get(field_name)
        
#         # built_value pode ser dict ou valor direto
#         if isinstance(built_value, dict):
#             built_value = built_value.get("value")
            
#         if saved_value != built_value:
#             return True
    
#     return False

# def _find_removed_questions(orgAnkiDeck, storedNotes):
#     """
#     Identifica questões que foram removidas da fonte remota.
    
#     Args:
#         orgAnkiDeck: Deck remoto atual
#         storedNotes (dict): Índice de notas armazenadas
        
#     Returns:
#         list: Lista de questões que foram removidas
#     """
#     # Construir conjunto de chaves das questões remotas atuais
#     remoteQuestionKeys = _build_remote_keys_set(orgAnkiDeck)
    
#     removedQuestions = []
    
#     for note_key, storedNote in storedNotes.items():
#         if storedNote is None:
#             continue
            
#         keyField = determine_key_field(storedNote)
#         fields = storedNote.get("fields", {})
#         keyFieldDict = fields.get(keyField, {})
#         key = keyFieldDict.get("value")
        
#         if key not in remoteQuestionKeys:
#             noteId = storedNote.get("noteId", -1)
#             removedQuestions.append({"question": storedNote, "noteId": noteId})
    
#     return removedQuestions

# def _build_remote_keys_set(orgAnkiDeck):
#     """
#     Constrói conjunto de chaves das questões remotas.
    
#     Args:
#         orgAnkiDeck: Deck remoto
        
#     Returns:
#         set: Conjunto com todas as chaves das questões remotas
#     """
#     remoteQuestionKeys = set()
#     noteBuilder = AnkiNoteBuilder()
    
#     for question in orgAnkiDeck.getQuestions():
#         builtQuestion = noteBuilder.buildNote(question)
#         fields = builtQuestion.get("fields", {})
        
#         # Adicionar tanto "Front" quanto "Text" para compatibilidade
#         remoteQuestionKeys.add(fields.get("Front", None))
#         remoteQuestionKeys.add(fields.get("Text", None))
    
#     # Remover None do conjunto
#     remoteQuestionKeys.discard(None)
    
#     return remoteQuestionKeys