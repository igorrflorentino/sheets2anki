# Sistema de Consistência Automática de Nomes - Documentação

## 📋 Visão Geral

O **NameConsistencyManager** é um sistema robusto que garante automaticamente a consistência de nomes durante a sincronização de decks no addon Sheets2Anki. Ele implementa a lógica especificada para manter todos os nomes (decks, note types, deck options) sempre consistentes com o `remote_deck_name`, mesmo após modificações manuais pelo usuário no Anki.

## 🎯 Funcionalidades Principais

### 1. **Consistência Automática Durante Sincronização**
- ✅ Executa automaticamente após cada sincronização
- ✅ Não interrompe o processo em caso de erro
- ✅ Log detalhado de todas as operações

### 2. **Geração de Nomes Padrão**
- ✅ `local_deck_name`: `"Sheets2Anki::{remote_deck_name}"`
- ✅ `note_types`: `"Sheets2Anki - {remote_deck_name} - {aluno} - Basic/Cloze"`
- ✅ `deck_option_name`: `"Sheets2Anki - {remote_deck_name}"`

### 3. **Verificação e Atualização Inteligente**
- ✅ Compara nomes atuais com padrões esperados
- ✅ Atualiza apenas quando necessário
- ✅ Preserva alunos válidos nos note types
- ✅ Suporte para aluno especial `[MISSING A.]`

### 4. **Integração com Configuração**
- ✅ Atualiza `meta.json` com novos nomes
- ✅ Sincroniza objetos físicos no Anki
- ✅ Mantém IDs corretos

## 🔧 Implementação Técnica

### Classe Principal: `NameConsistencyManager`

```python
class NameConsistencyManager:
    @staticmethod
    def ensure_consistency_during_sync(deck_url: str, debug_callback=None)
    
    @staticmethod
    def enforce_name_consistency(deck_url, remote_deck_name, local_deck_id, note_types_config, debug_callback)
    
    @staticmethod
    def generate_standard_names(remote_deck_name: str)
```

### Integração no Processo de Sincronização

O sistema é chamado automaticamente em `src/sync.py` na função `_sync_single_deck()`:

```python
# Logo após captura de note type IDs
try:
    consistency_result = NameConsistencyManager.ensure_consistency_during_sync(
        deck_url=remote_deck_url,
        debug_callback=lambda msg: add_debug_message(msg, "NAME_CONSISTENCY")
    )
    # Processing dos resultados...
except Exception as consistency_error:
    # Log de erro sem interromper sincronização
```

## 📊 Lógica de Funcionamento

### 1. **Salvar `remote_deck_name`**
- ✅ Source of truth para todos os nomes
- ✅ Extraído da URL do deck remoto

### 2. **Recriar Strings de Referência**
```python
local_deck_name = f"Sheets2Anki::{remote_deck_name}"
note_type_basic = f"Sheets2Anki - {remote_deck_name} - {{student}} - Basic"
note_type_cloze = f"Sheets2Anki - {remote_deck_name} - {{student}} - Cloze"
deck_option_name = f"Sheets2Anki - {remote_deck_name}"
```

### 3. **Comparar com Nomes Reais**
- ✅ Verifica deck name no Anki vs `local_deck_name`
- ✅ Verifica cada note type vs padrão esperado
- ✅ Verifica deck options vs `deck_option_name`

### 4. **Atualizar Automaticamente**
- ✅ Deck name no Anki
- ✅ Note type names no Anki
- ✅ Deck options name no Anki (modo individual)
- ✅ Configuração no `meta.json`

## 🛡️ Robustez e Segurança

### Tratamento de Erros
- ✅ Nunca interrompe a sincronização
- ✅ Log detalhado de todos os erros
- ✅ Fallback para manter nomes atuais

### Validações
- ✅ Verifica disponibilidade do Anki
- ✅ Valida existência de decks e note types
- ✅ Confirma alunos habilitados

### Modo Seguro
- ✅ Apenas atualiza se modo deck options = "individual"
- ✅ Preserva configuração padrão do Anki
- ✅ Backup automático via save operations

## 📈 Exemplos de Uso

### Exemplo 1: Deck Básico
```
Remote: "Matemática Básica"
├── Local deck: "Sheets2Anki::Matemática Básica"
├── Note type (Igor): "Sheets2Anki - Matemática Básica - Igor - Basic"
├── Note type (Ana): "Sheets2Anki - Matemática Básica - Ana - Cloze"
└── Deck options: "Sheets2Anki - Matemática Básica"
```

### Exemplo 2: Deck com Caracteres Especiais
```
Remote: "• Sheets2Anki Template - Igor"
├── Local deck: "Sheets2Anki::• Sheets2Anki Template - Igor"
├── Note type: "Sheets2Anki - • Sheets2Anki Template - Igor - Igor - Basic"
└── Deck options: "Sheets2Anki - • Sheets2Anki Template - Igor"
```

### Exemplo 3: Aluno Especial
```
Note type missing: "Sheets2Anki - Química - [MISSING A.] - Basic"
```

## 🔍 Logs e Debug

### Categorias de Log
- `[NAME_CONSISTENCY]`: Operações principais
- `[SYNC_CONSISTENCY]`: Integração com sincronização
- `[DECK_UPDATE]`: Atualizações de deck
- `[NOTE_TYPE_UPDATE]`: Atualizações de note types
- `[OPTIONS_UPDATE]`: Atualizações de deck options

### Exemplo de Log
```
[NAME_CONSISTENCY] 🔧 Iniciando consistência de nomes para: 'Matemática Básica'
[NAME_CONSISTENCY] Deck atual: 'User Modified Name' vs esperado: 'Sheets2Anki::Matemática Básica'
[NAME_CONSISTENCY] 📝 Atualizando nome do deck: 'User Modified Name' → 'Sheets2Anki::Matemática Básica'
[NAME_CONSISTENCY] ✅ Nome do deck atualizado
[NAME_CONSISTENCY] Note type 123: 'Old Name' vs 'Sheets2Anki - Matemática Básica - Igor - Basic'
[NAME_CONSISTENCY] 📝 Atualizando note type: 'Old Name' → 'Sheets2Anki - Matemática Básica - Igor - Basic'
[NAME_CONSISTENCY] ✅ Consistência aplicada: deck name, 2 note types atualizados
```

## 🧪 Testes

### Arquivo de Teste: `test_name_consistency.py`
- ✅ Geração de nomes padrão
- ✅ Determinação de nomes esperados
- ✅ Integração básica (mock)

### Executar Testes
```bash
cd /path/to/sheets2anki
python test_name_consistency.py
```

## 🚀 Benefícios do Sistema

### Para o Usuário
1. **Transparente**: Funciona automaticamente sem intervenção
2. **Consistente**: Nomes sempre seguem o padrão estabelecido
3. **Robusto**: Não quebra mesmo com modificações manuais
4. **Informativo**: Logs claros sobre o que foi alterado

### Para o Desenvolvedor
1. **Modular**: Sistema isolado e testável
2. **Extensível**: Fácil adição de novas regras
3. **Seguro**: Não afeta sincronização em caso de erro
4. **Observável**: Debug detalhado de todas as operações

## 📝 Notas de Implementação

### Dependências
- `src/config_manager.py`: Funções de configuração
- `src/utils.py`: Utilidades existentes
- `aqt/mw`: Interface do Anki

### Arquivos Modificados
- `src/sync.py`: Integração automática
- `src/name_consistency_manager.py`: Nova classe principal

### Arquivos Criados
- `test_name_consistency.py`: Testes de verificação

## 🔮 Evolução Futura

### Melhorias Possíveis
1. **Cache de Nomes**: Evitar verificações desnecessárias
2. **Configuração**: Permitir personalização dos padrões
3. **Histórico**: Manter log de mudanças aplicadas
4. **Interface**: Tela para verificar/aplicar consistência manualmente

### Compatibilidade
- ✅ Compatível com sistema existente
- ✅ Não quebra configurações atuais
- ✅ Suporte para todos os tipos de deck
