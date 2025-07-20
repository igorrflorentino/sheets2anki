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
    ("sheet2anki Layout - Notas", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=36065074&single=true&output=tsv"),
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
DEFAULT_IMPORTANCE = "MISSING I."
DEFAULT_TOPIC = "MISSING T."
DEFAULT_SUBTOPIC = "MISSING S."
DEFAULT_CONCEPT = "MISSING C."

# Prefixos para tags
TAG_ROOT = "sheet2anki"
TAG_TOPICS = "topicos"
TAG_SUBTOPICS = "subtopicos"
TAG_CONCEPTS = "conceitos"
