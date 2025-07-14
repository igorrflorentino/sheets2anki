# 📊 Guia dos Dados de Teste - Sheets2Anki

## 🎯 Visão Geral

Este guia detalha o arquivo consolidado `test_data_consolidated.tsv` que centraliza todos os dados de teste do projeto Sheets2Anki.

## 📁 Arquivo: `test_data_consolidated.tsv`

### 📊 **Estrutura Básica**
- **Formato**: TSV (Tab-separated values)
- **Encoding**: UTF-8
- **Separador**: Tab (\t)
- **Linhas**: 20 dados + 1 header
- **Colunas**: 17 (todas obrigatórias)

### 📋 **Colunas Obrigatórias**
1. **ID** - Identificador único
2. **PERGUNTA** - Pergunta do card
3. **LEVAR PARA PROVA** - Resposta do card
4. **SYNC?** - Controle de sincronização
5. **INFO COMPLEMENTAR** - Informação adicional
6. **INFO DETALHADA** - Informação detalhada
7. **EXEMPLO 1** - Primeiro exemplo
8. **EXEMPLO 2** - Segundo exemplo
9. **EXEMPLO 3** - Terceiro exemplo
10. **TOPICO** - Tópico principal
11. **SUBTOPICO** - Subtópico
12. **CONCEITO** - Conceito abordado
13. **BANCAS** - Bancas de concurso
14. **ULTIMO ANO EM PROVA** - Último ano em prova
15. **CARREIRA** - Carreira/área
16. **IMPORTANCIA** - Nível de importância
17. **TAGS ADICIONAIS** - Tags extras

## 🔄 Dados Consolidados

### 📊 **Seção 1: Exemplos Originais (001-008)**
**Origem**: `docs/exemplo_planilha_com_sync.tsv`
- **Propósito**: Dados realistas para demonstração
- **Características**: Diferentes tipos de SYNC?, áreas variadas
- **Uso**: Testes de funcionalidade completa

**Exemplo:**
```tsv
001	Qual é a capital do Brasil?	Brasília	true	Brasília foi fundada em 1960	A capital federal do Brasil é Brasília	...
002	Quem foi o primeiro presidente do Brasil?	Deodoro da Fonseca	1	Deodoro da Fonseca foi o primeiro presidente	...
```

### 🧪 **Seção 2: Erros de Fórmula (009-013)**
**Origem**: `tests/test_formula_errors_data.tsv`
- **Propósito**: Teste de limpeza de erros de fórmula
- **Características**: Contém diversos tipos de erros
- **Uso**: Testes de limpeza e validação

**Tipos de Erros Incluídos:**
- `#NAME?` - Erro de nome de função
- `#REF!` - Erro de referência
- `#VALUE!` - Erro de valor
- `#DIV/0!` - Divisão por zero
- `#N/A` - Valor não disponível
- `#NULL!` - Erro de nulo
- `#ERROR!` - Erro genérico
- `#NUM!` - Erro numérico
- `#CUSTOM!` - Erro customizado
- `=FORMULA` - Fórmulas Excel/Google Sheets

### 📝 **Seção 3: Teste Básico (014)**
**Origem**: `test_sheet.tsv`
- **Propósito**: Teste básico de importação
- **Características**: Dados simples e diretos
- **Uso**: Testes unitários rápidos

### 🔧 **Seção 4: Casos Adicionais (015-020)**
**Origem**: Criados durante consolidação
- **Propósito**: Completar cobertura de testes
- **Características**: Cenários específicos
- **Uso**: Testes de edge cases

## 🎯 Tipos de Sincronização

### ✅ **Valores Verdadeiros (SYNC?)**
- `true` - Valor booleano verdadeiro
- `1` - Valor numérico verdadeiro
- `SIM` - Valor em português maiúsculo
- `TRUE` - Valor booleano maiúsculo
- `sim` - Valor em português minúsculo
- `yes` - Valor em inglês
- `verdadeiro` - Valor completo em português

### ❌ **Valores Falsos (SYNC?)**
- `false` - Valor booleano falso
- `0` - Valor numérico falso
- `f` - Valor abreviado falso

### 📝 **Valores Especiais**
- Campo vazio (linha 008) - Para testes de validação
- Diferentes formatações - Para testes de case insensitive

## 📊 Áreas de Conhecimento

### 🌍 **Geografia**
- Capitais do Brasil e mundo
- Continentes e países
- Características geográficas

### 📚 **História**
- Presidentes do Brasil
- Descobrimentos
- Períodos históricos

### 🧪 **Química**
- Fórmulas químicas
- Elementos da tabela periódica
- Reações químicas

### 🌌 **Astronomia**
- Planetas do sistema solar
- Características astronômicas
- Fenômenos espaciais

### ⚡ **Física**
- Constantes físicas
- Leis da física
- Fenômenos físicos

### 🔢 **Matemática**
- Operações básicas
- Funções matemáticas
- Conceitos numéricos

### 📖 **Português**
- Gramática
- Textos e interpretação
- Regras linguísticas

### 💻 **Planilhas**
- Funções do Excel
- Fórmulas avançadas
- Processamento de dados

## 🔧 Funções Helper

### 📥 **Carregar Dados**
```python
from test_data_helpers import load_test_data

# Dados básicos (primeiras 5 linhas)
basic_data = load_test_data('basic')

# Dados com erros de fórmula (linhas 009-013)
formula_data = load_test_data('formula_errors')

# Dados para testes de sincronização
sync_data = load_test_data('sync_tests')

# Dados dos exemplos originais (linhas 001-008)
examples = load_test_data('examples')

# Todos os dados
all_data = load_test_data()
```

### 📊 **Análise de Dados**
```python
from test_data_helpers import get_sync_variations, get_formula_errors

# Variações de SYNC?
sync_vars = get_sync_variations()
print(f"Valores verdadeiros: {sync_vars['true_values']}")
print(f"Valores falsos: {sync_vars['false_values']}")

# Erros de fórmula encontrados
errors = get_formula_errors()
print(f"Total de erros: {len(errors)}")
```

### 🎯 **Subconjuntos**
```python
from test_data_helpers import create_test_subset

# Subconjunto pequeno para testes rápidos
small_subset = create_test_subset(3)  # 3 linhas
```

## 🧪 Casos de Uso

### 1. **Testes de Sincronização Seletiva**
```python
# Filtrar dados por tipo de SYNC?
sync_true = [row for row in data if row['SYNC?'] in ['true', '1', 'SIM', 'TRUE']]
sync_false = [row for row in data if row['SYNC?'] in ['false', '0', 'f']]
```

### 2. **Testes de Limpeza de Fórmulas**
```python
# Usar dados com erros de fórmula
formula_data = load_test_data('formula_errors')
cleaned_data = clean_formula_errors(formula_data)
```

### 3. **Testes de Importação Básica**
```python
# Usar dados básicos
basic_data = load_test_data('basic')
result = import_cards(basic_data)
```

### 4. **Testes de Compatibilidade**
```python
# Filtrar por características específicas
compatibility_data = [row for row in data if 'compatibilidade' in row.get('TAGS ADICIONAIS', '')]
```

## 📈 Estatísticas dos Dados

### 📊 **Distribuição por Seção**
- **Exemplos**: 8 linhas (40%)
- **Erros de Fórmula**: 5 linhas (25%)
- **Teste Básico**: 1 linha (5%)
- **Casos Adicionais**: 6 linhas (30%)

### 🎯 **Distribuição por SYNC?**
- **Verdadeiros**: 14 linhas (70%)
- **Falsos**: 5 linhas (25%)
- **Vazios**: 1 linha (5%)

### 📚 **Distribuição por Área**
- **Geografia**: 4 linhas (20%)
- **História**: 2 linhas (10%)
- **Química**: 2 linhas (10%)
- **Matemática**: 2 linhas (10%)
- **Outros**: 10 linhas (50%)

## 🔄 Migração e Manutenção

### 📝 **Adicionar Novos Dados**
1. Editar `test_data_consolidated.tsv`
2. Manter formato TSV
3. Usar ID sequencial
4. Incluir todas as 17 colunas
5. Documentar mudanças

### 🔄 **Atualizar Dados Existentes**
1. Localizar por ID
2. Manter compatibilidade
3. Validar com testes
4. Atualizar documentação

### 🧪 **Validar Integridade**
```python
# Testar funções helper
python test_data_helpers.py

# Executar testes rápidos
python run_tests.py quick
```

## 🏆 Benefícios

### ✅ **Centralização**
- Todos os dados em um arquivo
- Fácil manutenção e atualização
- Consistência garantida

### ✅ **Flexibilidade**
- Filtros especializados
- Subconjuntos personalizados
- Acesso via funções helper

### ✅ **Cobertura Completa**
- Todos os tipos de SYNC?
- Todos os erros de fórmula
- Diferentes áreas de conhecimento
- Casos edge incluídos

**🎯 Dados organizados, documentados e prontos para uso profissional!**
- **História**: Presidentes, descobrimentos
- **Química**: Fórmulas, elementos
- **Astronomia**: Planetas, sistema solar
- **Física**: Constantes, óptica
- **Matemática**: Aritmética, funções
- **Português**: Gramática, textos
- **Planilhas**: Funções Excel
- **Teste**: Cenários específicos

### 🎯 Casos de Uso

#### **1. Testes de Sincronização Seletiva**
```python
# Usar linhas com diferentes valores de SYNC?
data = load_tsv("test_data_consolidated.tsv")
sync_true = [row for row in data if row['SYNC?'] in ['true', '1', 'SIM', 'TRUE']]
sync_false = [row for row in data if row['SYNC?'] in ['false', '0', 'f']]
```

#### **2. Testes de Limpeza de Fórmulas**
```python
# Usar linhas 009-013 que contêm erros de fórmula
formula_errors = data[8:13]  # Linhas 009-013
clean_data = clean_formula_errors(formula_errors)
```

#### **3. Testes de Importação Básica**
```python
# Usar qualquer linha para teste básico
basic_test = data[0:5]  # Primeiras 5 linhas
result = import_cards(basic_test)
```

#### **4. Testes de Compatibilidade**
```python
# Usar linha 018 específica para compatibilidade
compatibility_test = [row for row in data if 'compatibilidade' in row.get('TAGS ADICIONAIS', '')]
```

### 🔧 Vantagens da Consolidação

#### **1. Manutenção Simplificada**
- ✅ Um único arquivo para atualizar
- ✅ Dados consistentes entre todos os testes
- ✅ Fácil adição de novos casos de teste

#### **2. Cobertura Completa**
- ✅ Todos os tipos de SYNC? cobertos
- ✅ Todos os erros de fórmula incluídos
- ✅ Diferentes áreas de conhecimento
- ✅ Casos edge incluídos

#### **3. Organização Clara**
- ✅ IDs sequenciais (001-020)
- ✅ Dados agrupados por origem
- ✅ Documentação completa
- ✅ Fácil navegação

### 📋 Como Usar

#### **1. Nos Testes Python**
```python
import pandas as pd

# Carregar dados consolidados
df = pd.read_csv('tests/test_data_consolidated.tsv', sep='\t')

# Filtrar por tipo de teste
formula_errors = df[df['ID'].astype(str).str.startswith('00')][8:13]
sync_tests = df[df['SYNC?'].isin(['true', '1', 'SIM', 'TRUE'])]
```

#### **2. Para Diferentes Cenários**
```python
# Teste rápido - primeiras 5 linhas
quick_test = df.head(5)

# Teste completo - todos os dados
full_test = df

# Teste específico - apenas erros de fórmula
formula_test = df[df['INFO DETALHADA'].str.contains('#|=', na=False)]
```

### 🚀 Próximos Passos

1. **Atualizar todos os testes** para usar `test_data_consolidated.tsv`
2. **Remover arquivos TSV antigos** após validação
3. **Adicionar novos casos** conforme necessário
4. **Manter documentação** atualizada

### 📝 Notas Importantes

- **Formato**: TSV (Tab-separated values)
- **Encoding**: UTF-8
- **Separador**: Tab (\t)
- **Headers**: 17 colunas obrigatórias
- **IDs**: Formato 001-020 para ordenação consistente

**Este arquivo centraliza todos os dados de teste e serve como única fonte de verdade para testes do Sheets2Anki!** 🎯
