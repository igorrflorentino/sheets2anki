"""
Constantes e dados de teste para o addon Sheets2Anki.

Este módulo contém todas as constantes utilizadas no projeto,
incluindo URLs de teste e templates de cards.
"""

# Constante para identificar se estamos em modo de desenvolvimento
# Esta constante será alterada para False durante o processo de build
IS_DEVELOPMENT_MODE = True

# URLs hardcoded para testes e simulações
TEST_SHEETS_URLS = [
    ("Sheets2Anki Template", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsNCEFZvBR3UjBwTbyaPPz-B1SKw17I7Jb72XWweS1y75HmzXfgdFJ1TpZX6_S06m9_phJTy5XnCI6/pub?gid=36065074&single=true&output=tsv"),
]

# Template constants para geração de cards
CARD_SHOW_ALLWAYS_TEMPLATE = """
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
"""

CARD_SHOW_HIDE_TEMPLATE = """
{{{{#{field_value}}}}}
<b>{field_name}:</b><br>
{{{{{field_value}}}}}<br><br>
{{{{/{field_value}}}}}
"""

# Valores padrão para campos vazios
DEFAULT_IMPORTANCE = "[MISSING I.]"
DEFAULT_TOPIC = "[MISSING T.]"
DEFAULT_SUBTOPIC = "[MISSING S.]"
DEFAULT_CONCEPT = "[MISSING C.]"

# Nome do deck raiz - constante não modificável pelo usuário
DEFAULT_PARENT_DECK_NAME = "Sheets2Anki"

# Prefixos para tags
TAG_ROOT = "Sheets2Anki"
TAG_TOPICS = "topicos"
TAG_SUBTOPICS = "subtopicos"
TAG_CONCEPTS = "conceitos"
