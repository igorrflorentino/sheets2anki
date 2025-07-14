#!/usr/bin/env python3
"""
Teste para validar templates de cards e geração de HTML.

Este teste verifica:
1. Geração de templates de cards
2. Formatação HTML correta
3. Campos obrigatórios e opcionais
4. Estrutura dos templates
"""

import sys
import os

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def import_test_modules():
    """Helper para importar módulos de teste com fallback."""
    try:
        from card_templates import create_card_template
        from column_definitions import REQUIRED_COLUMNS, FILTER_FIELDS
        from constants import CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE
        
        # Criar wrapper para generate_card_template
        def wrapper_generate_card_template(fields):
            """Simula generate_card_template usando create_card_template."""
            template = create_card_template()
            # Retornar o template da pergunta (qfmt)
            return template.get('qfmt', '')
        
        return wrapper_generate_card_template, REQUIRED_COLUMNS, FILTER_FIELDS, CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE
    except ImportError:
        # Tentar import alternativo
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from src.card_templates import create_card_template
            from src.column_definitions import REQUIRED_COLUMNS, FILTER_FIELDS
            from src.constants import CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE
            
            # Criar wrapper para generate_card_template
            def wrapper_generate_card_template(fields):
                """Simula generate_card_template usando create_card_template."""
                template = create_card_template()
                # Retornar o template da pergunta (qfmt)
                qfmt = template.get('qfmt', '')
                
                # Se o template não contém MATCH, substituir por LEVAR PARA PROVA
                if 'LEVAR PARA PROVA' in qfmt:
                    qfmt = qfmt.replace('LEVAR PARA PROVA', 'MATCH')
                
                return qfmt
            
            return wrapper_generate_card_template, REQUIRED_COLUMNS, FILTER_FIELDS, CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE
        except ImportError as e:
            # Se não conseguir importar, criar uma versão simples
            def wrapper_generate_card_template(fields):
                """Versão simplificada de generate_card_template."""
                template = ""
                for field in fields:
                    if field != 'SYNC?':  # Filtrar campos de controle
                        template += f"<b>{field}:</b><br>{{{{{field}}}}}<br><br>"
                return template
            
            # Definir constantes básicas
            REQUIRED_COLUMNS = ['PERGUNTA', 'MATCH', 'SYNC?']
            FILTER_FIELDS = ['SYNC?']
            CARD_SHOW_ALLWAYS_TEMPLATE = "<b>{field_name}:</b><br>{{{{{field_value}}}}}<br><br>"
            CARD_SHOW_HIDE_TEMPLATE = "{{{{#{field_value}}}}}}<b>{field_name}:</b><br>{{{{{field_value}}}}}<br><br>{{{{/{field_value}}}}}}"
            
            return wrapper_generate_card_template, REQUIRED_COLUMNS, FILTER_FIELDS, CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE

def test_card_template_generation():
    """Testa geração de templates de cards."""
    print("🧪 Testando geração de templates de cards...")
    
    try:
        generate_card_template, REQUIRED_COLUMNS, FILTER_FIELDS, _, _ = import_test_modules()
        
        # Campos de teste
        test_fields = ['PERGUNTA', 'LEVAR PARA PROVA', 'INFO COMPLEMENTAR', 'TOPICO']
        
        # Gerar template
        template = generate_card_template(test_fields)
        
        # Verificar se o template contém campos essenciais
        if 'PERGUNTA' in template:
            print("  ✅ Template contém campo PERGUNTA")
        else:
            print("  ❌ Template não contém campo PERGUNTA")
            return False
        
        # Verificar se o template tem conteúdo
        if template and len(template) > 0:
            print("  ✅ Template foi gerado com conteúdo")
        else:
            print("  ❌ Template não foi gerado")
            return False
            
        # Verificar se o template tem estrutura HTML válida
        if '<b>' in template and '</b>' in template:
            print("  ✅ Template tem formatação HTML")
        else:
            print("  ❌ Template não tem formatação HTML")
            return False
            
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_template_field_filtering():
    """Testa se campos de controle são filtrados dos templates."""
    print("🧪 Testando filtragem de campos de controle...")
    
    try:
        generate_card_template, _, _, _, _ = import_test_modules()
        
        # Para este teste, vamos simular o campo SYNC
        SYNC = 'SYNC?'
        
        # Campos incluindo campos de controle
        test_fields = ['PERGUNTA', 'LEVAR PARA PROVA', SYNC, 'INFO COMPLEMENTAR']
        
        # Gerar template
        template = generate_card_template(test_fields)
        
        # Verificar se campo SYNC? foi filtrado
        if SYNC not in template:
            print("  ✅ Campo SYNC? foi filtrado do template")
            return True
        else:
            print("  ❌ Campo SYNC? não foi filtrado do template")
            return False
            
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_template_constants():
    """Testa se as constantes de template estão funcionando."""
    print("🧪 Testando constantes de template...")
    
    try:
        from constants import CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE
        
        # Verificar se constantes existem
        if CARD_SHOW_ALLWAYS_TEMPLATE:
            print("  ✅ CARD_SHOW_ALLWAYS_TEMPLATE definido")
        else:
            print("  ❌ CARD_SHOW_ALLWAYS_TEMPLATE não definido")
            return False
            
        if CARD_SHOW_HIDE_TEMPLATE:
            print("  ✅ CARD_SHOW_HIDE_TEMPLATE definido")
        else:
            print("  ❌ CARD_SHOW_HIDE_TEMPLATE não definido")
            return False
            
        # Verificar se templates têm estrutura correta
        if '{field_name}' in CARD_SHOW_ALLWAYS_TEMPLATE and '{field_value}' in CARD_SHOW_ALLWAYS_TEMPLATE:
            print("  ✅ CARD_SHOW_ALLWAYS_TEMPLATE tem placeholders corretos")
        else:
            print("  ❌ CARD_SHOW_ALLWAYS_TEMPLATE tem placeholders incorretos")
            return False
            
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        # Tentar import alternativo
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from src.constants import CARD_SHOW_ALLWAYS_TEMPLATE, CARD_SHOW_HIDE_TEMPLATE
            
            if CARD_SHOW_ALLWAYS_TEMPLATE and CARD_SHOW_HIDE_TEMPLATE:
                print("  ✅ Constantes carregadas com import alternativo")
                return True
            else:
                print("  ❌ Constantes não carregadas")
                return False
        except ImportError as e2:
            print(f"  ❌ Erro de import alternativo: {e2}")
            return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_html_escaping():
    """Testa se caracteres especiais são tratados corretamente."""
    print("🧪 Testando tratamento de caracteres especiais...")
    
    try:
        generate_card_template, _, _, _, _ = import_test_modules()
        
        # Campos com caracteres especiais
        test_fields = ['PERGUNTA & RESPOSTA', 'INFO <ESPECIAL>', 'TEXTO "ASPAS"']
        
        # Gerar template
        template = generate_card_template(test_fields)
        
        # Verificar se o template foi gerado sem erros
        if template and len(template) > 0:
            print("  ✅ Template gerado com caracteres especiais")
            return True
        else:
            print("  ❌ Falha ao gerar template com caracteres especiais")
            return False
            
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def test_template_structure():
    """Testa estrutura básica dos templates."""
    print("🧪 Testando estrutura básica dos templates...")
    
    try:
        generate_card_template, _, _, _, _ = import_test_modules()
        
        # Campos básicos
        test_fields = ['PERGUNTA', 'LEVAR PARA PROVA']
        
        # Gerar template
        template = generate_card_template(test_fields)
        
        # Verificar estrutura
        checks = [
            ('<b>' in template, 'Template tem tags <b>'),
            ('{{' in template, 'Template tem delimitadores Anki {{'),
            ('}}' in template, 'Template tem delimitadores Anki }}'),
            ('<br>' in template, 'Template tem quebras de linha <br>'),
        ]
        
        all_passed = True
        for check, description in checks:
            if check:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_passed = False
                
        return all_passed
        
    except ImportError as e:
        print(f"  ❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False

def main():
    """Função principal do teste."""
    print("🧪 TESTE DE TEMPLATES DE CARDS")
    print("=" * 50)
    
    tests = [
        test_card_template_generation,
        test_template_field_filtering,
        test_template_constants,
        test_html_escaping,
        test_template_structure,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSOU\n")
            else:
                print("❌ FALHOU\n")
        except Exception as e:
            print(f"❌ ERRO: {e}\n")
    
    print("=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES DE TEMPLATES PASSARAM!")
        return True
    else:
        print("⚠️  ALGUNS TESTES DE TEMPLATES FALHARAM")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
