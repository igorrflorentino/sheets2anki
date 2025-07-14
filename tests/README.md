# 📋 Testes - Sheets2Anki

## 🎯 Visão Geral

Esta pasta contém todos os testes organizados para o addon Sheets2Anki. O sistema de testes foi completamente reorganizado para ser profissional, escalável e fácil de manter.

## 📁 Estrutura Organizada

```
tests/
├── README.md                          # ← Este arquivo (visão geral)
├── run_all_tests.py                   # Script principal de execução
├── test_data_consolidated.tsv         # Dados de teste consolidados
├── test_data_helpers.py               # Funções helper para dados
├── docs/                              # Documentação detalhada
│   ├── STRUCTURE.md                   # Estrutura detalhada dos testes
│   ├── DATA_GUIDE.md                  # Guia dos dados de teste
│   └── MIGRATION_GUIDE.md             # Guia de migração
├── debug/                             # Scripts de debug
│   └── debug_suite.py                 # Suite de debug consolidada
├── integration/                       # Testes de integração
│   └── test_integration.py            # Testes de integração completos
├── workflow/                          # Testes de workflow
│   └── test_workflow.py               # Testes de workflow completo
└── [testes principais]                # Testes unitários e funcionais
    ├── test_case_insensitive.py       # Case insensitive SYNC?
    ├── test_sync_selective.py         # Sincronização seletiva
    ├── test_sync_basic.py             # Sincronização básica
    ├── test_sync_internal_only.py     # Campos internos apenas
    ├── test_formula_errors_simple.py  # Limpeza de erros de fórmula
    ├── test_formula_advanced.py       # Fórmulas avançadas
    ├── test_url_validation.py         # Validação de URLs
    ├── test_ignored_cards.py          # Cards ignorados
    ├── test_data_validation.py        # Validação de dados
    ├── test_card_templates.py         # Templates de cards
    ├── test_config.py                 # Configurações
    ├── test_compatibility.py          # Compatibilidade Anki 25.x
    ├── test_deck_sync_counting.py     # Contagem de decks
    ├── test_structure.py              # Estrutura do projeto
    ├── test_imports.py                # Importações
    └── [outros testes...]
```

## 🚀 Como Executar

### 1. **Execução Rápida (Recomendado)**
```bash
# Da raiz do projeto
python run_tests.py quick

# Ou diretamente da pasta tests
cd tests
python run_all_tests.py quick
```

### 2. **Suite Completa**
```bash
# Da raiz do projeto
python run_tests.py

# Ou diretamente da pasta tests
cd tests
python run_all_tests.py
```

### 3. **Testes Específicos**
```bash
cd tests

# Testes por categoria
python debug/debug_suite.py             # Debug completo
python integration/test_integration.py  # Integração
python workflow/test_workflow.py        # Workflow

# Testes individuais
python test_case_insensitive.py         # Case insensitive
python test_sync_selective.py           # Sincronização seletiva
python test_sync_basic.py               # Sincronização básica
python test_formula_errors_simple.py    # Limpeza de fórmulas
python test_data_validation.py          # Validação de dados
python test_card_templates.py           # Templates de cards
python test_config.py                   # Configurações
```

## 📊 Status dos Testes

### ✅ **Testes Rápidos (Essenciais)**
- `test_case_insensitive.py` ✅
- `test_sync_selective.py` ✅
- `test_sync_internal_only.py` ✅
- `test_formula_errors_simple.py` ✅
- `test_url_validation.py` ✅
- `test_structure.py` ✅
- `test_imports.py` ✅
- `test_data_validation.py` ✅
- `integration/test_integration.py` ✅

### ✅ **Funcionalidades Testadas**
1. **Sincronização Seletiva** - Coluna SYNC? com múltiplos valores
2. **Sincronização Básica** - Funcionalidades core de sincronização
3. **Limpeza de Fórmulas** - Erros #NAME?, #REF!, =FORMULA
4. **Validação de URLs** - URLs publicadas e normais
5. **Case Insensitive** - SYNC? aceita variações de case
6. **Contagem de Cards** - Cards sincronizados vs ignorados
7. **Validação de Dados** - Dados malformados e robustez
8. **Templates de Cards** - Geração e formatação HTML
9. **Configurações** - Carregamento e persistência
10. **Compatibilidade** - Anki 25.x
11. **Estrutura** - Imports e arquivos organizados

## 🔧 Dados de Teste

### 📄 **Arquivo Principal:** `test_data_consolidated.tsv`
- **20 linhas** de dados + header
- **17 colunas** obrigatórias
- **Todos os cenários** de teste cobertos

### 🔍 **Tipos de Dados Incluídos:**
- **Sincronização**: `true`, `1`, `SIM`, `false`, `0`, `f`, etc.
- **Erros de Fórmula**: `#NAME?`, `#REF!`, `#VALUE!`, `=FORMULA`
- **Áreas**: Geografia, História, Química, Matemática, etc.

### 🧰 **Funções Helper:**
```python
from test_data_helpers import load_test_data

# Dados básicos para testes rápidos
basic_data = load_test_data('basic')

# Dados com erros de fórmula
formula_data = load_test_data('formula_errors')

# Dados para testes de sincronização
sync_data = load_test_data('sync_tests')
```

## 📚 Documentação

### 📖 **Guias Detalhados:**
- **`docs/STRUCTURE.md`** - Estrutura completa dos testes
- **`docs/DATA_GUIDE.md`** - Guia detalhado dos dados
- **`docs/MIGRATION_GUIDE.md`** - Como migrar testes antigos

### 🔧 **Scripts Utilitários:**
- **`migrate_to_consolidated.py`** - Migração de dados antigos
- **`test_data_helpers.py`** - Funções para trabalhar com dados

## 🎯 Benefícios da Organização

### ✅ **Estrutura Profissional**
- Testes organizados por categoria
- Documentação completa
- Dados centralizados

### ✅ **Execução Flexível**
- Testes rápidos para desenvolvimento
- Suite completa para CI/CD
- Testes específicos para debug

### ✅ **Manutenção Facilitada**
- Scripts centralizados
- Imports padronizados
- Estrutura escalável

## 🛠️ Desenvolvimento

### 📝 **Adicionar Novo Teste:**
1. Criar arquivo `test_nova_funcionalidade.py`
2. Usar `test_data_helpers.py` para dados
3. Seguir padrão dos testes existentes
4. Documentar no README apropriado

### 🔄 **Atualizar Dados:**
1. Editar `test_data_consolidated.tsv`
2. Usar funções helper para acessar
3. Validar com testes existentes
4. Atualizar documentação

## 🏆 Resultado

**✅ Sistema de testes 100% organizado e funcional!**

- ✅ Estrutura profissional e escalável
- ✅ Todos os testes funcionando (100% sucesso)
- ✅ Dados centralizados e documentados
- ✅ Fácil manutenção e desenvolvimento
- ✅ Execução flexível e rápida

**🎉 Pronto para desenvolvimento profissional!**
