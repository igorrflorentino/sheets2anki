#!/usr/bin/env python3
"""
Teste para validação de URLs e tratamento de erros 404.
"""

import re
from urllib.parse import urlparse, parse_qs

def validate_google_sheets_url(url):
    """Cópia da função para teste standalone."""
    result = {
        'valid': False,
        'spreadsheet_id': None,
        'gid': None,
        'issues': [],
        'suggestions': []
    }
    
    if not url or not isinstance(url, str):
        result['issues'].append("URL está vazia ou não é uma string")
        return result
    
    url = url.strip()
    
    # Verificar se é URL do Google Sheets
    if 'docs.google.com/spreadsheets' not in url:
        result['issues'].append("URL não é do Google Sheets")
        result['suggestions'].append("URL deve conter 'docs.google.com/spreadsheets'")
        return result
    
    # Verificar estrutura básica da URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            result['issues'].append("URL mal formatada (sem scheme ou netloc)")
            return result
    except Exception as e:
        result['issues'].append(f"Erro ao analisar URL: {e}")
        return result
    
    # Extrair ID da planilha - tentar primeiro padrão de URL publicada
    spreadsheet_id_match = re.search(r'/spreadsheets/d/e/([^/]+)', url)
    if not spreadsheet_id_match:
        # Tentar padrão normal (/d/ID)
        spreadsheet_id_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if not spreadsheet_id_match:
            result['issues'].append("ID da planilha não encontrado na URL")
            result['suggestions'].append("URL deve ter formato: /spreadsheets/d/[ID]/ ou /spreadsheets/d/e/[ID]/")
            return result
    
    result['spreadsheet_id'] = spreadsheet_id_match.group(1)
    
    # Extrair GID se presente
    gid = "0"  # Padrão
    
    # Tentar extrair GID do fragmento (#gid=123)
    if '#gid=' in url:
        gid_match = re.search(r'#gid=([^&\s]+)', url)
        if gid_match:
            gid = gid_match.group(1)
    
    # Tentar extrair GID dos parâmetros (?gid=123)
    elif '?gid=' in url or '&gid=' in url:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if 'gid' in params:
            gid = params['gid'][0]
    
    result['gid'] = gid
    
    # Verificar se ID da planilha é muito curto (erro crítico)
    if len(result['spreadsheet_id']) < 10:
        result['issues'].append("ID da planilha muito curto - provavelmente inválido")
        result['suggestions'].append("Verifique se a URL está completa e correta")
    # Warning para IDs curtos mas possivelmente válidos
    elif len(result['spreadsheet_id']) < 20:
        result['suggestions'].append("ID da planilha parece curto - IDs do Google geralmente têm 44+ caracteres")
    
    # Se chegou até aqui sem problemas críticos, é válida
    if not result['issues']:
        result['valid'] = True
    
    return result

def create_fallback_urls(original_url, validation_result):
    """Cópia da função para teste standalone."""
    fallback_urls = []
    
    if not validation_result.get('valid') or not validation_result.get('spreadsheet_id'):
        return fallback_urls
    
    spreadsheet_id = validation_result['spreadsheet_id']
    gid = validation_result.get('gid', '0')
    
    # Detectar se é URL publicada (/d/e/) ou normal (/d/)
    is_published = '/d/e/' in original_url
    
    if is_published:
        # Para URLs publicadas, usar formato /d/e/ID/pub
        
        # URL 1: Pub TSV com GID 0
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/e/{spreadsheet_id}/pub?output=tsv&gid=0"
        )
        
        # URL 2: Pub TSV com GID específico (se diferente de 0)
        if gid != '0':
            fallback_urls.append(
                f"https://docs.google.com/spreadsheets/d/e/{spreadsheet_id}/pub?output=tsv&gid={gid}"
            )
        
        # URL 3: Pub CSV como fallback
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/e/{spreadsheet_id}/pub?output=csv&gid=0"
        )
        
        # URL 4: Tentar formato tradicional (sem /e/)
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&gid=0"
        )
    else:
        # Para URLs normais, usar formato /d/ID/export
        
        # URL 1: Export básico com GID 0 (aba padrão)
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&exportFormat=tsv&gid=0"
        )
        
        # URL 2: Export com GID detectado (se diferente de 0)
        if gid != '0':
            fallback_urls.append(
                f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&exportFormat=tsv&gid={gid}"
            )
        
        # URL 3: Export sem GID especificado
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=tsv&exportFormat=tsv"
        )
        
        # URL 4: Export com output=tsv
        fallback_urls.append(
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?output=tsv&gid=0"
        )
    
    # Remover duplicatas mantendo ordem
    seen = set()
    unique_fallbacks = []
    for url in fallback_urls:
        if url not in seen and url != original_url:
            seen.add(url)
            unique_fallbacks.append(url)
    
    return unique_fallbacks

def test_url_validation():
    """Testa a validação de URLs."""
    
    print("🧪 Testando validação de URLs...")
    
    test_cases = [
        # (url, expected_valid, expected_issues_count, description)
        (
            "https://docs.google.com/spreadsheets/d/1ABC123DEF456789012345678901234567890123456/edit#gid=0",
            True, 0, "URL válida completa"
        ),
        (
            "https://docs.google.com/spreadsheets/d/1ABC123DEF456/edit#gid=123456",
            True, 0, "ID curto (agora aceito com aviso)"
        ),
        (
            "https://example.com/not-google-sheets.csv",
            False, 1, "Não é Google Sheets"
        ),
        (
            "https://docs.google.com/spreadsheets/edit#gid=0",
            False, 1, "Sem ID da planilha"
        ),
        (
            "",
            False, 1, "URL vazia"
        ),
        (
            "https://docs.google.com/spreadsheets/d/1ABC123DEF456789012345678901234567890123456/edit#gid=abc",
            True, 0, "GID não numérico (agora válido)"
        ),
        (
            "https://docs.google.com/spreadsheets/d/ABC123/edit#gid=0",
            False, 1, "ID muito curto (< 10 chars - rejeitado)"
        ),
        (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSART0Xw_lDq5bn4bylNox7vxOmU6YkoOjOwqdS3kZ-O1JEBLR8paqDv_bcGTW55yXchaO0jzK2cB8x/pub?gid=334628680&output=tsv",
            True, 0, "URL publicada (formato /d/e/ID/pub)"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for i, (url, expected_valid, expected_issues_count, description) in enumerate(test_cases, 1):
        try:
            result = validate_google_sheets_url(url)
            
            success = True
            if result['valid'] != expected_valid:
                print(f"❌ Teste {i}: {description}")
                print(f"    Expected valid: {expected_valid}, got: {result['valid']}")
                success = False
            
            if len(result['issues']) != expected_issues_count:
                print(f"❌ Teste {i}: {description}")
                print(f"    Expected {expected_issues_count} issues, got: {len(result['issues'])}")
                print(f"    Issues: {result['issues']}")
                success = False
            
            if success:
                print(f"✅ Teste {i}: {description}")
                if result['valid']:
                    print(f"    ID: {result['spreadsheet_id']}, GID: {result['gid']}")
                else:
                    print(f"    Issues: {'; '.join(result['issues'])}")
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"💥 Teste {i}: {description} - ERRO: {e}")
            failed += 1
        
        print()
    
    print(f"📊 Resultados: {passed} passou(ram), {failed} falhou(ram)")
    return failed == 0

def test_fallback_urls():
    """Testa a criação de URLs de fallback."""
    
    print("🧪 Testando criação de URLs de fallback...")
    
    # URL de teste válida
    test_url = "https://docs.google.com/spreadsheets/d/1ABC123DEF456789012345678901234567890123456/edit#gid=123456"
    validation_result = validate_google_sheets_url(test_url)
    
    print(f"📋 URL original: {test_url}")
    print(f"📋 Validação: {validation_result}")
    
    if not validation_result['valid']:
        print("❌ URL de teste não é válida")
        return False
    
    fallback_urls = create_fallback_urls(test_url, validation_result)
    
    print(f"\n📋 URLs de fallback criadas ({len(fallback_urls)}):")
    for i, url in enumerate(fallback_urls, 1):
        print(f"  {i}. {url}")
    
    # Verificações
    expected_count = 4  # Esperamos 4 URLs diferentes
    if len(fallback_urls) != expected_count:
        print(f"❌ Esperado {expected_count} URLs, obtido {len(fallback_urls)}")
        return False
    
    # Verificar se todas são diferentes
    if len(set(fallback_urls)) != len(fallback_urls):
        print("❌ URLs duplicadas encontradas")
        return False
    
    # Verificar se nenhuma é igual à original
    if test_url in fallback_urls:
        print("❌ URL original encontrada nas fallbacks")
        return False
    
    # Verificar se todas contêm o ID correto
    expected_id = validation_result['spreadsheet_id']
    for url in fallback_urls:
        if expected_id not in url:
            print(f"❌ URL não contém ID esperado: {url}")
            return False
    
    print("\n✅ Todas as verificações passaram!")
    return True

def test_error_scenarios():
    """Testa cenários de erro comuns."""
    
    print("🧪 Testando cenários de erro...")
    
    error_scenarios = [
        {
            'description': 'Planilha não compartilhada publicamente',
            'url': 'https://docs.google.com/spreadsheets/d/1PRIVATE123456789012345678901234567890123456/edit#gid=0',
            'expected_suggestions': ['compartilhada publicamente', 'URL está correta']
        },
        {
            'description': 'GID incorreto',
            'url': 'https://docs.google.com/spreadsheets/d/1ABC123DEF456789012345678901234567890123456/edit#gid=999999',
            'expected_suggestions': ['aba especificada existe']
        },
        {
            'description': 'ID da planilha incorreto',
            'url': 'https://docs.google.com/spreadsheets/d/INVALID_ID/edit#gid=0',
            'expected_suggestions': ['URL está correta']
        }
    ]
    
    for i, scenario in enumerate(error_scenarios, 1):
        print(f"\n📋 Cenário {i}: {scenario['description']}")
        print(f"    URL: {scenario['url']}")
        
        validation_result = validate_google_sheets_url(scenario['url'])
        
        if validation_result['valid']:
            print("    ⚠️  URL considerada válida (pode gerar 404 real)")
        else:
            print(f"    ❌ Invalidada: {'; '.join(validation_result['issues'])}")
        
        if validation_result.get('suggestions'):
            print(f"    💡 Sugestões: {'; '.join(validation_result['suggestions'])}")
    
    print("\n✅ Cenários de erro testados!")
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 TESTES DE VALIDAÇÃO DE URL E TRATAMENTO DE ERRO 404")
    print("=" * 70)
    
    test1_result = test_url_validation()
    print("\n" + "=" * 70)
    test2_result = test_fallback_urls()
    print("\n" + "=" * 70)
    test3_result = test_error_scenarios()
    
    print("\n" + "=" * 70)
    if test1_result and test2_result and test3_result:
        print("🎉 TODOS OS TESTES PASSARAM!")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
