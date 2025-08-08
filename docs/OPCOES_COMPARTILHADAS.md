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
- **Novos decks** criados pelo Sheets2Anki automaticamente usam o grupo "Sheets2Anki"
- **Deck pai** "Sheets2Anki" também usa as opções compartilhadas
- **Subdecks** também herdam essas configurações automaticamente
- **Sincronizações** aplicam as opções automaticamente a todos os decks
- **Não requer nenhuma ação manual do usuário**

### 🔄 Aplicação Durante Operações
- **Adição de novo deck** → Opções aplicadas automaticamente
- **Sincronização de decks** → Opções aplicadas a todos os decks
- **Criação de subdecks** → Opções herdadas automaticamente

## 🛠️ Como Usar

### 1. Configurar as Opções (Única Ação Necessária)

1. No Anki, vá para **Tools → Preferences → Deck Options**
2. Selecione o grupo **"Sheets2Anki"** no dropdown
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

O grupo "Sheets2Anki" é criado automaticamente com configurações otimizadas para flashcards de planilhas:

```
• Novos cards por dia: 50
• Revisões por dia: 200  
• Passos de aprendizado: 1min, 10min
• Passos de reaprendizado: 10min
• Intervalo mínimo após lapso: 1 dia
• Multiplicador de lapso: 0% (recomeça do início)
```

## 🔧 Funcionalidades Técnicas

### Aplicação Automática Total
- **Novos decks:** Opções aplicadas automaticamente na criação
- **Sincronizações:** Opções reaplicadas a todos os decks
- **Deck pai incluído:** "Sheets2Anki" também usa as opções compartilhadas
- **Subdecks incluídos:** Todos os subdecks herdam as mesmas opções
- **Zero configuração:** Funciona sem intervenção do usuário

### Momentos de Aplicação
1. **Durante adição de deck** → Aplicado ao deck recém-criado
2. **Durante sincronização** → Aplicado a todos os decks remotos + deck pai
3. **Na criação de qualquer deck** → get_or_create_deck aplica automaticamente
4. **Em subdecks** → Herdam as opções do deck pai automaticamente

## 🎁 Benefícios

- ✅ **Totalmente automático** - Sem necessidade de configuração manual
- ✅ **Aplicação universal** - Deck pai e todos os subdecks incluídos
- ✅ **Consistência garantida** - Todas as operações aplicam as opções
- ✅ **Facilidade máxima** - Configure uma vez, funciona para sempre
- ✅ **Manutenção zero** - Sistema se mantém automaticamente
- ✅ **Otimização específica** - Configurações ideais para flashcards de planilhas

## 📞 Observações Importantes

1. **Aplicação automática:** As opções são aplicadas automaticamente durante sincronizações e adição de decks
2. **Deck pai incluído:** O deck "Sheets2Anki" também usa as opções compartilhadas
3. **Configuração única:** Você só precisa configurar as opções uma vez
4. **Herança automática:** Novos decks e subdecks herdam as configurações automaticamente
