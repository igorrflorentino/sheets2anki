# 🧪 Testes do Sheets2Anki

Este diretório contém a suíte de testes completa para o add-on Sheets2Anki, desenvolvida com pytest.

## 📋 Estrutura dos Testes

### 📁 Arquivos de Teste

| Arquivo | Descrição | Cobertura |
|---------|-----------|-----------|
| `conftest.py` | Configurações e fixtures comuns | Fixtures reutilizáveis |
| `test_data_processor.py` | Processamento de dados TSV | Parsing, validação, detecção cloze |
| `test_config_manager.py` | Gerenciamento de configurações | CRUD configurações, persistência |
| `test_utils.py` | Funções utilitárias | URLs, hashes, validações |
| `test_student_manager.py` | Gestão de alunos | Alunos globais, filtragem |
| `test_integration.py` | Testes de integração | Fluxos completos |
| `test_new_tags.py` | Sistema de tags (legado) | Tags hierárquicas |
| `run_tests.py` | Script executor | Automação de testes |

### 🏷️ Categorias de Testes

#### **🔬 Testes Unitários** (`@pytest.mark.unit`)
- Testam funções isoladas
- Execução rápida
- Mocks para dependências externas
- Cobertura de casos extremos

#### **🔗 Testes de Integração** (`@pytest.mark.integration`) 
- Testam fluxos completos
- Interação entre módulos
- Cenários reais de uso
- Validação end-to-end

#### **🐌 Testes Lentos** (`@pytest.mark.slow`)
- Testes de performance
- Datasets grandes
- Operações demoradas
- Pulados em execução rápida

## 🚀 Como Executar os Testes

### Pré-requisitos

```bash
# Instalar dependências de teste
pip install pytest pytest-cov pytest-mock
```

### Execução Básica

```bash
# Todos os testes
python tests/run_tests.py

# Ou diretamente com pytest
python -m pytest tests/
```

### Opções Avançadas

```bash
# 🔬 Apenas testes unitários
python tests/run_tests.py --unit

# 🔗 Apenas testes de integração  
python tests/run_tests.py --integration

# 📊 Com cobertura de código
python tests/run_tests.py --coverage

# 🏃 Execução rápida (pula testes lentos)
python tests/run_tests.py --fast

# 🔍 Saída detalhada
python tests/run_tests.py --verbose

# 📁 Arquivo específico
python tests/run_tests.py --file data_processor

# 🎯 Função específica
python tests/run_tests.py --function test_parse_students

# ℹ️ Informações sobre testes disponíveis
python tests/run_tests.py --info
```

### Combinações Úteis

```bash
# Desenvolvimento: testes unitários com saída detalhada
python tests/run_tests.py --unit --verbose

# CI/CD: todos os testes com cobertura
python tests/run_tests.py --coverage

# Debug: arquivo específico com verbose
python tests/run_tests.py --file utils --verbose

# Performance: apenas testes lentos
python -m pytest tests/ -m slow -v
```

## 🏗️ Fixtures Disponíveis

### 📊 Dados de Teste

- `sample_tsv_data`: Dados TSV estruturados para testes
- `sample_tsv_content`: Conteúdo TSV em formato string  
- `sample_students`: Lista de alunos para testes
- `sample_url`: URL de exemplo do Google Sheets
- `sample_config`: Configuração padrão para testes

### 🎭 Mocks do Anki

- `mock_mw`: Mock do main window do Anki
- `mock_note`: Mock de uma nota do Anki
- `mock_note_type`: Mock de um note type
- `setup_test_environment`: Configuração automática de mocks

### 📁 Arquivos Temporários

- `temp_config_file`: Arquivo de configuração temporário
- `clean_sys_path`: Limpeza do sys.path após testes

## 📝 Escrevendo Novos Testes

### Estrutura Básica

```python
import pytest

@pytest.mark.unit
class TestMyModule:
    """Testes para o módulo MyModule."""
    
    def test_basic_functionality(self):
        """Teste básico de funcionalidade."""
        # Arrange
        input_data = "test_input"
        expected = "expected_output"
        
        # Act  
        result = my_function(input_data)
        
        # Assert
        assert result == expected
    
    def test_edge_cases(self):
        """Teste de casos extremos."""
        assert my_function("") == ""
        assert my_function(None) is None
        
    def test_error_handling(self):
        """Teste de tratamento de erros."""
        with pytest.raises(ValueError):
            my_function("invalid_input")
```

### Usando Fixtures

```python
def test_with_fixtures(self, sample_tsv_data, mock_mw):
    """Teste usando fixtures."""
    # Usar dados de amostra
    assert len(sample_tsv_data) > 0
    
    # Usar mock do Anki
    mock_mw.col.findNotes.return_value = [123, 456]
    result = my_anki_function(mock_mw)
    assert len(result) == 2
```

### Testes de Integração

```python
@pytest.mark.integration
def test_complete_workflow(self, tmp_path):
    """Teste de fluxo completo."""
    # Criar ambiente temporário
    config_file = tmp_path / "test_config.json"
    
    # Executar fluxo completo
    result = complete_workflow(str(config_file))
    
    # Verificar resultado
    assert result['success'] == True
```

## 📊 Cobertura de Código

### Gerar Relatório

```bash
# Relatório HTML (recomendado)
python tests/run_tests.py --coverage

# Abrir no navegador
open htmlcov/index.html
```

### Métricas Alvo

- **Cobertura Total**: > 80%
- **Módulos Críticos**: > 90%
- **Funções Públicas**: 100%

### Visualizar Cobertura

O relatório HTML mostra:
- ✅ Linhas cobertas (verde)
- ❌ Linhas não cobertas (vermelho)  
- ⚠️ Branches parciais (amarelo)
- 📊 Percentual por arquivo

## 🐛 Debugging de Testes

### Execução com Debug

```bash
# Parar no primeiro erro
python -m pytest tests/ -x

# Mostrar variáveis locais em falhas
python -m pytest tests/ -l

# Modo debug interativo
python -m pytest tests/ --pdb

# Capturar prints
python -m pytest tests/ -s
```

### Logs de Debug

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    logger = logging.getLogger(__name__)
    logger.debug("Debug info")
    
    # Teste continua...
```

## 🔧 Configuração Personalizada

### pytest.ini (já configurado)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: mark a test as a unit test
    integration: mark a test as an integration test
    slow: mark a test as slow (skipped in quick mode)
addopts = -v
```

### Personalizar Markers

```bash
# Executar apenas testes marcados
python -m pytest tests/ -m "unit and not slow"

# Executar testes com tag personalizada
python -m pytest tests/ -m "requires_anki"
```

## 🎯 Melhores Práticas

### ✅ Do's

- **Use fixtures** para dados comuns
- **Teste casos extremos** (valores nulos, vazios, inválidos)
- **Nomes descritivos** para funções de teste
- **Documentação** clara do que está sendo testado
- **Arrange-Act-Assert** pattern
- **Mocks** para dependências externas

### ❌ Don'ts

- **Não teste implementação**, teste comportamento
- **Não use dados hardcoded** desnecessariamente
- **Não ignore falhas** intermitentes
- **Não teste código de terceiros**
- **Não faça testes muito complexos**

### 🏗️ Estrutura Recomendada

```python
class TestMyFeature:
    """Testes agrupados por feature."""
    
    def test_happy_path(self):
        """Cenário principal de sucesso."""
        pass
    
    def test_edge_cases(self):
        """Casos extremos."""
        pass
    
    def test_error_handling(self):
        """Tratamento de erros."""
        pass
```

## 📈 Métricas e Relatórios

### Executar Análise Completa

```bash
# Cobertura + relatórios detalhados
python tests/run_tests.py --coverage --verbose

# Ver estatísticas
python tests/run_tests.py --info
```

### CI/CD Integration

```bash
# Para pipelines automatizados
python -m pytest tests/ \
  --cov=src \
  --cov-report=xml \
  --cov-report=term \
  --junitxml=test-results.xml
```

## 🆘 Troubleshooting

### Problemas Comuns

#### Import Errors
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m pytest tests/
```

#### Mock Issues
```python
# Verificar se mocks estão sendo aplicados corretamente
def test_debug_mock(self, mock_mw):
    print(f"Mock type: {type(mock_mw)}")
    print(f"Mock methods: {dir(mock_mw)}")
```

#### Fixture Conflicts
```python
# Usar fixtures específicas quando necessário
def test_specific_fixture(self, sample_tsv_data):
    # Em vez de fixture genérica, criar dados específicos
    specific_data = [{'ID': 'TEST001', 'PERGUNTA': 'Test?'}]
```

### Logs de Debug

```bash
# Ver logs detalhados dos testes
python -m pytest tests/ --log-cli-level=DEBUG
```

## 🚀 Próximos Passos

### Melhorias Planejadas

- [ ] Testes de performance automatizados
- [ ] Cobertura de mutation testing
- [ ] Testes de carga para datasets grandes
- [ ] Integração com GitHub Actions
- [ ] Testes de compatibilidade multi-versão

### Como Contribuir

1. **Identifique gaps** na cobertura
2. **Escreva testes** seguindo os padrões
3. **Execute a suíte** completa antes do commit
4. **Documente** casos complexos
5. **Mantenha fixtures** atualizadas

---

Para mais informações sobre pytest: https://docs.pytest.org/
