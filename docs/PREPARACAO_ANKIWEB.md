# Preparação para AnkiWeb - Sheets2Anki

## Arquivos Necessários para AnkiWeb

### ✅ Arquivos Obrigatórios Presentes
- `__init__.py` - Ponto de entrada do add-on
- `manifest.json` - Metadados do add-on
- `config.json` - Configuração padrão

### ✅ Estrutura Otimizada
```
sheets2anki/
├── __init__.py           # Ponto de entrada
├── manifest.json        # Metadados (versioning correto)
├── config.json          # Configuração modernizada
├── src/                 # Código principal
│   ├── compat.py        # Compatibilidade Qt/Anki
│   ├── main.py          # Funcionalidades principais
│   ├── parseRemoteDeck.py
│   └── column_definitions.py
├── libs/                # Dependências
└── docs/                # Documentação técnica
```

## Checklist de Compatibilidade AnkiWeb

### ✅ Versioning
- `min_point_version`: 231000 (Anki 23.10.0+)
- `max_point_version`: 260000 (até Anki 26.0)
- Suporta Anki 25.x atual

### ✅ Compatibilidade Qt
- Layer de compatibilidade para Qt5/Qt6
- Imports seguros com fallbacks
- Constantes adaptáveis

### ✅ Configuração
- `config.json` com estrutura moderna
- Configurações sensatas por padrão
- Sem dados hardcoded de teste

### ✅ Imports Limpos
- Sem imports de desenvolvimento
- Tratamento de erros robusto
- Fallbacks apropriados

## Melhorias Implementadas

### 1. Módulo de Compatibilidade (`src/compat.py`)
- Detecção automática de versão Anki/Qt
- Imports seguros com fallbacks
- Constantes de compatibilidade
- Funções utilitárias modernizadas

### 2. Manifest.json Atualizado
- Versioning correto para Anki 25.x
- Descrição melhorada
- Configuração limpa (sem dados de teste)

### 3. Config.json Modernizado
- Configurações adicionais úteis
- Estrutura limpa
- Compatível com padrões AnkiWeb

### 4. Imports Refatorados
- Uso do módulo de compatibilidade
- Type hints onde apropriado
- Código mais robusto

## Antes de Publicar

### Checklist Final
- [ ] Testar no Anki 25.x real
- [ ] Verificar todas as funcionalidades principais
- [ ] Remover/comentar código de debug
- [ ] Limpar URLs de teste hardcoded
- [ ] Testar instalação/desinstalação
- [ ] Verificar se não há dependências externas problemas

### Preparação do Pacote
1. Remover pasta `tests/` do pacote final
2. Remover pasta `docs/` do pacote final  
3. Manter apenas: `__init__.py`, `manifest.json`, `config.json`, `src/`, `libs/`
4. Testar pacote mínimo

### Validação AnkiWeb
- Estrutura de arquivos correta ✅
- Metadados válidos ✅
- Código compatível ✅
- Sem dependências externas problemáticas ✅

## Status: PRONTO PARA TESTES

O add-on foi refatorado e está tecnicamente pronto para o AnkiWeb. 
Próximo passo: testar no Anki 25.x real antes da publicação.
