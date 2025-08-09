# Opções Compartilhadas de Deck - Sheets2Anki

## 📋 Visão Geral

O sistema de opções compartilhadas permite que todos os decks sincronizados com planilhas do Google Sheets usem automaticamente o mesmo conjunto de configurações de estudo. Isso inclui:

- **Limites diários** (novos cards e revisões)
- **Intervalos de repetição** 
- **Configurações de lapso** (cards esquecidos)
- **Facilidade/dificuldade** dos botões
- **Outras opções de deck**

## 🎯 Como Funciona

### ⚡ Aplicação Totalmente Automática
- **Novos decks** criados pelo Sheets2Anki automaticamente usam o grupo "Sheets2Anki - Default Options"
- **Deck raiz** "Sheets2Anki" usa configurações específicas: "Sheets2Anki - Root Options"
- **Subdecks** também herdam essas configurações automaticamente
- **Sincronizações** aplicam as opções automaticamente a todos os decks
- **Não requer nenhuma ação manual do usuário**

### 🔄 Aplicação Durante Operações
- **Adição de novo deck** → Opções aplicadas automaticamente
- **Sincronização de decks** → Opções aplicadas a todos os decks
- **Criação de subdecks** → Opções herdadas automaticamente
- **Configuração de modos** → Aplicação imediata ao clicar "Aplicar"

## 🛠️ Como Usar

### 1. Configurar as Opções (Única Ação Necessária)

1. No Anki, vá para **Tools → Preferences → Deck Options**
2. Selecione o grupo **"Sheets2Anki - Default Options"** no dropdown
3. Configure as opções desejadas:
   - **New cards/day:** Quantos cards novos por dia
   - **Reviews/day:** Quantas revisões por dia  
   - **Learning steps:** Intervalos para cards novos
   - **Relearning steps:** Intervalos para cards esquecidos
   - **Ease modifier:** Modificador de facilidade

### 2. Aplicação Automática

- **Salve as configurações** no diálogo de opções
- **Todas as alterações** se aplicam automaticamente a todos os decks
- **Novos decks** herdarão essas configurações automaticamente
- **Próxima sincronização** aplicará as opções a todos os decks existentes

## ⚙️ Configurações Padrão

O grupo "Sheets2Anki - Default Options" é criado automaticamente com configurações otimizadas para flashcards de planilhas:

```
• Novos cards por dia: 50
• Revisões por dia: 200  
• Passos de aprendizado: 1min, 10min
• Passos de reaprendizado: 10min
• Intervalo mínimo após lapso: 1 dia
• Multiplicador de lapso: 0% (recomeça do início)
```

O deck raiz "Sheets2Anki" usa "Sheets2Anki - Root Options" com configurações mais conservadoras.

## 🔧 Funcionalidades Técnicas

### Aplicação Automática Total
- **Novos decks:** Opções aplicadas automaticamente na criação
- **Sincronizações:** Opções reaplicadas a todos os decks
- **Deck raiz incluído:** "Sheets2Anki" usa opções específicas do raiz
- **Subdecks incluídos:** Todos os subdecks herdam as mesmas opções
- **Zero configuração:** Funciona sem intervenção do usuário
- **Limpeza automática:** Remove grupos de opções órfãos

### Momentos de Aplicação
1. **Durante adição de deck** → Aplicado ao deck recém-criado
2. **Durante sincronização** → Aplicado a todos os decks remotos + deck raiz
3. **Na criação de qualquer deck** → get_or_create_deck aplica automaticamente
4. **Em subdecks** → Herdam as opções do deck pai automaticamente
5. **Ao configurar modos** → Sistema completo aplicado imediatamente

### Sistema de Limpeza
- **Grupos órfãos:** Remove automaticamente grupos "Sheets2Anki*" sem decks
- **Aplicação inteligente:** Só aplica em modos automáticos (shared/individual)
- **Preservação:** Mantém grupos em uso por outros decks

## 🎁 Benefícios

- ✅ **Totalmente automático** - Sem necessidade de configuração manual
- ✅ **Aplicação universal** - Deck raiz e todos os subdecks incluídos
- ✅ **Consistência garantida** - Todas as operações aplicam as opções
- ✅ **Facilidade máxima** - Configure uma vez, funciona para sempre
- ✅ **Manutenção zero** - Sistema se mantém automaticamente
- ✅ **Otimização específica** - Configurações ideais para flashcards de planilhas
- ✅ **Limpeza automática** - Remove grupos órfãos automaticamente

## 📞 Observações Importantes

1. **Aplicação automática:** As opções são aplicadas automaticamente durante sincronizações e adição de decks
2. **Deck raiz específico:** O deck "Sheets2Anki" usa "Sheets2Anki - Root Options" com configurações próprias
3. **Configuração única:** Você só precisa configurar as opções uma vez
4. **Herança automática:** Novos decks e subdecks herdam as configurações automaticamente
5. **Limpeza inteligente:** Sistema remove grupos órfãos mas preserva grupos em uso
