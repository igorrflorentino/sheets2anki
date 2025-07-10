"""
Constantes e dados de teste para o addon Sheets2Anki.

Este módulo contém todas as constantes utilizadas no projeto,
incluindo URLs de teste e templates de cards.
"""

# URLs hardcoded para testes e simulações
TEST_SHEETS_URLS = [
    ("Mais importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv"),
    ("Menos importantes", "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=1869088045&output=tsv"),
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
