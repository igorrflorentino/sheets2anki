# 🔄 Guia de Migração - Testes Sheets2Anki

## 🎯 Visão Geral

Este guia ajuda desenvolvedores a migrar testes antigos para a nova estrutura organizada do Sheets2Anki.

## 📋 Estrutura Antiga vs Nova

### 🔴 **Estrutura Antiga (Antes)**
```
projeto/
├── test_sheet.tsv                      # Dados espalhados
├── docs/exemplo_planilha_com_sync.tsv  # Dados separados
├── tests/
│   ├── test_formula_errors_data.tsv    # Dados fragmentados
│   └── [testes individuais]
└── debug_*.py                          # Scripts na raiz
```

### 🟢 **Estrutura Nova (Depois)**
```
projeto/
├── tests/
│   ├── README.md                       # Visão geral
│   ├── run_all_tests.py                # Script principal
│   ├── test_data_consolidated.tsv      # Dados centralizados
│   ├── test_data_helpers.py            # Funções helper
│   ├── docs/                           # Documentação
│   │   ├── STRUCTURE.md
│   │   ├── DATA_GUIDE.md
│   │   └── MIGRATION_GUIDE.md
│   ├── debug/
│   │   └── debug_suite.py
│   ├── integration/
│   │   └── test_integration.py
│   ├── workflow/
│   │   └── test_workflow.py
│   └── [testes organizados]
└── backup_tsv_files/                   # Backup seguro
```

## 🚀 Processo de Migração

### 1. **Migração Automática (Recomendada)**
```bash
cd tests
python migrate_to_consolidated.py
```

**O que faz:**
- ✅ Faz backup dos arquivos originais
- ✅ Cria arquivo consolidado
- ✅ Atualiza referências em testes
- ✅ Cria funções helper
- ✅ Preserva dados originais

### 2. **Migração Manual**
Se preferir fazer manualmente:

#### **Passo 1: Backup**
```bash
mkdir backup_tsv_files
cp test_sheet.tsv backup_tsv_files/
cp docs/exemplo_planilha_com_sync.tsv backup_tsv_files/
cp tests/test_formula_errors_data.tsv backup_tsv_files/
```

#### **Passo 2: Consolidar Dados**
```bash
# Criar arquivo consolidado
cat > tests/test_data_consolidated.tsv << 'EOF'
ID	PERGUNTA	LEVAR PARA PROVA	SYNC?	...
001	Dados do exemplo_planilha_com_sync.tsv
...
EOF
```

#### **Passo 3: Atualizar Testes**
```python
# Antes
data_path = "test_sheet.tsv"

# Depois
from test_data_helpers import load_test_data
data = load_test_data('basic')
```

## 📊 Migração de Dados

### 🔄 **Consolidação de Arquivos TSV**

#### **Origem → Destino**
1. **`test_sheet.tsv`** → Linhas 014 do consolidado
2. **`docs/exemplo_planilha_com_sync.tsv`** → Linhas 001-008
3. **`tests/test_formula_errors_data.tsv`** → Linhas 009-013
4. **Dados adicionais** → Linhas 015-020

#### **Formato Padronizado**
```tsv
ID	PERGUNTA	LEVAR PARA PROVA	SYNC?	INFO COMPLEMENTAR	INFO DETALHADA	EXEMPLO 1	EXEMPLO 2	EXEMPLO 3	TOPICO	SUBTOPICO	CONCEITO	BANCAS	ULTIMO ANO EM PROVA	CARREIRA	IMPORTANCIA	TAGS ADICIONAIS
001	Pergunta exemplo	Resposta exemplo	true	Info complementar	Info detalhada	Ex1	Ex2	Ex3	Tópico	Subtópico	Conceito	Banca	2023	Carreira	Alta	tags
```

### 🔧 **Atualização de Código**

#### **Carregamento de Dados**
```python
# ❌ Antes
import pandas as pd
df = pd.read_csv("test_sheet.tsv", sep='\t')

# ✅ Depois
from test_data_helpers import load_test_data
data = load_test_data('basic')
```

#### **Filtros Específicos**
```python
# ❌ Antes
formula_errors = df[df['INFO DETALHADA'].str.contains('#')]

# ✅ Depois
formula_errors = load_test_data('formula_errors')
```

#### **Subconjuntos**
```python
# ❌ Antes
small_data = df.head(3)

# ✅ Depois
small_data = create_test_subset(3)
```

## 🧪 Migração de Testes

### 📝 **Padrão de Teste Antigo**
```python
# test_antigo.py
import pandas as pd
import os

def test_funcionalidade():
    # Carregar dados
    data_path = os.path.join("..", "test_sheet.tsv")
    df = pd.read_csv(data_path, sep='\t')
    
    # Processar
    result = process_data(df)
    
    # Verificar
    assert len(result) > 0
    print("✅ Teste passou")
```

### 🔄 **Padrão de Teste Novo**
```python
# test_novo.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from test_data_helpers import load_test_data

def test_funcionalidade():
    # Carregar dados
    data = load_test_data('basic')
    
    # Processar
    result = process_data(data)
    
    # Verificar
    assert len(result) > 0
    print("✅ Teste passou")

if __name__ == "__main__":
    test_funcionalidade()
```

## 🔧 Funções Helper Disponíveis

### 📥 **Carregamento**
```python
# Dados básicos (5 primeiras linhas)
basic_data = load_test_data('basic')

# Dados com erros de fórmula
formula_data = load_test_data('formula_errors')

# Dados para sincronização
sync_data = load_test_data('sync_tests')

# Dados de exemplo originais
examples = load_test_data('examples')

# Todos os dados
all_data = load_test_data()
```

### 📊 **Análise**
```python
# Variações de SYNC?
sync_vars = get_sync_variations()

# Erros de fórmula
errors = get_formula_errors()

# Subconjunto pequeno
subset = create_test_subset(3)
```

## 🎯 Benefícios da Migração

### ✅ **Organização**
- **Antes**: Arquivos espalhados, difíceis de manter
- **Depois**: Estrutura organizada, fácil navegação

### ✅ **Dados**
- **Antes**: 3 arquivos TSV separados
- **Depois**: 1 arquivo consolidado + funções helper

### ✅ **Testes**
- **Antes**: Execução manual, sem padronização
- **Depois**: Scripts automatizados, execução organizada

### ✅ **Manutenção**
- **Antes**: Mudanças em múltiplos arquivos
- **Depois**: Atualização centralizada

## 📋 Checklist de Migração

### 🔄 **Preparação**
- [ ] Fazer backup dos arquivos originais
- [ ] Verificar que todos os testes passam antes da migração
- [ ] Entender a nova estrutura

### � **Execução**
- [ ] Executar script de migração (`migrate_to_consolidated.py`)
- [ ] Verificar criação do arquivo consolidado
- [ ] Validar funções helper
- [ ] Testar execução dos testes

### ✅ **Validação**
- [ ] Executar testes rápidos (`python run_tests.py quick`)
- [ ] Verificar 100% de sucesso
- [ ] Confirmar que dados estão íntegros
- [ ] Testar funções helper

### 🧹 **Limpeza**
- [ ] Confirmar que backup foi criado
- [ ] Remover arquivos TSV antigos (se desejar)
- [ ] Atualizar documentação
- [ ] Comunicar mudanças à equipe

## � Problemas Comuns

### ❌ **Problema**: Paths não encontrados
```python
# Solução
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
```

### ❌ **Problema**: Dados não carregam
```python
# Verificar se arquivo existe
data_path = get_consolidated_data_path()
print(f"Arquivo existe: {data_path.exists()}")
```

### ❌ **Problema**: Funções helper não funcionam
```python
# Executar teste das funções
python test_data_helpers.py
```

### ❌ **Problema**: Testes falham após migração
```python
# Verificar dados consolidados
data = load_test_data()
print(f"Linhas carregadas: {len(data)}")
```

## 🏆 Resultado Final

### ✅ **Antes da Migração**
- 3 arquivos TSV espalhados
- Testes sem padronização
- Manutenção complexa
- Execução manual

### 🎯 **Depois da Migração**
- 1 arquivo consolidado
- Funções helper especializadas
- Testes organizados e automatizados
- Estrutura profissional

### 📊 **Validação de Sucesso**
```bash
# Executar testes rápidos
python run_tests.py quick

# Resultado esperado: 5/5 (100%)
✅ test_case_insensitive.py
✅ test_sync_selective.py
✅ test_formula_errors_simple.py
✅ test_url_validation.py
✅ integration/test_integration.py
```

**🎉 Migração completa e sistema funcionando perfeitamente!**
python run_all_tests.py quick
```

### 3. Executar Teste Específico
```bash
cd tests
python test_case_insensitive.py
```

### 4. Executar Debug
```bash
cd tests
python debug/debug_suite.py
```

### 5. Executar Testes de Integração
```bash
cd tests
python integration/test_integration.py
```

### 6. Executar Testes de Workflow
```bash
cd tests
python workflow/test_workflow.py
```

## Script Principal do Projeto

O script principal `run_tests.py` na raiz do projeto ainda funciona:

```bash
python run_tests.py
```

## Testes Corrigidos

Os seguintes testes foram atualizados para usar todas as colunas obrigatórias:

- ✅ **test_debug_sync.py** - Corrigido para usar `REQUIRED_COLUMNS`
- ✅ **test_real_csv.py** - Dados de exemplo completos com todas as colunas
- ✅ **test_integration.py** - Testes de integração com dados completos

## Problemas Resolvidos

### 1. URLs Publicadas do Google Sheets
- **Problema**: URLs com formato `/d/e/ID/pub` não funcionavam
- **Solução**: Função `ensure_values_only_url` corrigida para detectar URLs publicadas

### 2. Validação de Colunas
- **Problema**: Testes falhavam por falta de colunas `CARREIRA` e `IMPORTANCIA`
- **Solução**: Todos os testes atualizados para usar `REQUIRED_COLUMNS` completo

### 3. Organização dos Testes
- **Problema**: Testes espalhados pela raiz do projeto
- **Solução**: Estrutura organizada em subpastas temáticas

## Estrutura de Dados de Teste

### Colunas Obrigatórias (17 total):
1. ID
2. PERGUNTA
3. LEVAR PARA PROVA
4. SYNC?
5. INFO COMPLEMENTAR
6. INFO DETALHADA
7. EXEMPLO 1
8. EXEMPLO 2
9. EXEMPLO 3
10. TOPICO
11. SUBTOPICO
12. CONCEITO
13. BANCAS
14. ULTIMO ANO EM PROVA
15. CARREIRA
16. IMPORTANCIA
17. TAGS ADICIONAIS

### Valores de SYNC? Suportados:

**Valores para Sincronizar (True):**
- `true`, `1`, `sim`, `yes`, `verdadeiro`, `v`
- Versões em maiúsculas: `TRUE`, `SIM`, `YES`, etc.
- Valor vazio: `""` (padrão é sincronizar)
- Valores não reconhecidos (padrão é sincronizar)

**Valores para Não Sincronizar (False):**
- `false`, `0`, `não`, `nao`, `no`, `falso`, `f`
- Versões em maiúsculas: `FALSE`, `NÃO`, `NO`, etc.

## Relatório de Testes

O script `run_all_tests.py` fornece relatórios detalhados com:

- ✅ Total de testes executados
- ✅ Taxa de sucesso por categoria
- ✅ Detalhes de erros quando aplicável
- ✅ Tempo de execução
- ✅ Organização por tipo de teste

## Manutenção

Para adicionar novos testes:

1. Crie o arquivo na subpasta apropriada (`debug/`, `integration/`, `workflow/`)
2. Adicione ao `test_structure` em `run_all_tests.py`
3. Siga o padrão de nomenclatura `test_*.py`
4. Use `REQUIRED_COLUMNS` para dados de teste completos

## Debugging

Para debug de problemas específicos:

```bash
# Debug completo
python debug/debug_suite.py

# Debug específico de URL
python -c "from debug.debug_suite import debug_url_validation; debug_url_validation()"

# Debug específico de headers
python -c "from debug.debug_suite import debug_header_validation; debug_header_validation()"
```
