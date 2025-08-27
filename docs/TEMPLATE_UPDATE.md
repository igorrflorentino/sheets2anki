# Atualização Automática de Templates

## Visão Geral

O sistema agora inclui atualização automática de templates para note types existentes, garantindo que todos os cards criados anteriormente possam usar a nova funcionalidade da coluna **ILUSTRAÇÃO HTML**.

## Como Funciona

### 1. Atualização Automática Durante a Sincronização

Sempre que você executar uma sincronização, o sistema automaticamente:

- 🔍 **Detecta** todos os note types do Sheets2Anki existentes
- ➕ **Adiciona** o campo "ILUSTRAÇÃO HTML" se não existir
- 🔄 **Atualiza** os templates de card para incluir a ilustração no **verso** do card
- 💾 **Salva** as alterações no Anki

### 2. Processo Seguro e Inteligente

O sistema é projetado para ser seguro:

- ✅ **Não duplica campos**: Verifica se o campo já existe antes de adicionar
- ✅ **Preserva dados**: Não remove ou modifica campos existentes
- ✅ **Atualização inteligente**: Só atualiza templates que realmente precisam
- ✅ **Log detalhado**: Registra todas as ações para debugging

## Posicionamento da ILUSTRAÇÃO HTML

A **ILUSTRAÇÃO HTML** é posicionada estrategicamente no **verso do card** (afmt):

### Localização no Template
```html
{{#INFO DETALHADA}}
<b>Info detalhada:</b><br>
{{INFO DETALHADA}}<br><br>
{{/INFO DETALHADA}}

{{#ILUSTRAÇÃO HTML}}<br><br>{{ILUSTRAÇÃO HTML}}<br><br>{{/ILUSTRAÇÃO HTML}}

{{#EXEMPLO 1}}
<b>Exemplo 1:</b><br>
{{EXEMPLO 1}}<br><br>
{{/EXEMPLO 1}}
```

### Por que no Verso?
- 🎯 **Contextualização**: A ilustração aparece depois da resposta, ajudando a contextualizar
- 📚 **Pedagogia**: Evita "dar a resposta" na pergunta
- 🎨 **Layout**: Mantém a frente do card limpa e focada na pergunta

## Compatibilidade

### Note Types Suportados
- ✅ **Sheets2Anki - [Nome do Deck]** (Normal)
- ✅ **Sheets2Anki - [Nome do Deck]** (Cloze)
- ❌ Note types que não começam com "Sheets2Anki" (ignorados)

### Versões do Anki
- ✅ **Anki 2.1.x**: Totalmente compatível
- ✅ **AnkiMobile**: Suporta HTML e imagens
- ✅ **AnkiDroid**: Suporta HTML e imagens

## Logging e Debug

O sistema fornece logging detalhado durante a atualização:

```
[UPDATE_TEMPLATES] Encontrados 3 note types do Sheets2Anki
[UPDATE_TEMPLATES] Processando: Sheets2Anki - Direito Civil (cloze: False)
[UPDATE_TEMPLATES] Campo ILUSTRAÇÃO HTML já existe
[UPDATE_TEMPLATES] Template 1 atualizado para Sheets2Anki - Direito Civil
[UPDATE_TEMPLATES] ✅ Sheets2Anki - Direito Civil processado com sucesso
[UPDATE_TEMPLATES] 🎯 Total de note types processados: 3
```

## Troubleshooting

### Problema: Templates não atualizaram
**Solução**: Execute uma sincronização. A atualização acontece automaticamente.

### Problema: Campo aparece mas sem conteúdo
**Solução**: Verifique se sua planilha tem a coluna "ILUSTRAÇÃO HTML" com conteúdo HTML válido.

### Problema: Imagens não aparecem
**Solução**: Certifique-se de que as URLs das imagens são acessíveis e o HTML está correto.

## Exemplo de Uso

### Planilha (TSV)
```
PERGUNTA	RESPOSTA	ILUSTRAÇÃO HTML
O que é um contrato?	Acordo de vontades	<img src="https://exemplo.com/contrato.jpg" style="max-width:300px;">
```

### Resultado no Anki
- **Frente**: Mostra apenas "O que é um contrato?"
- **Verso**: Mostra "Acordo de vontades" + a imagem do contrato

## Código Relevante

A funcionalidade está implementada em:
- `src/templates_and_definitions.py`: Função `update_existing_note_type_templates()`
- `src/sync.py`: Chamada automática durante sincronização
- Documentação de teste: `test_template_update.py`

## Próximos Passos

Para usar a nova funcionalidade:

1. 📊 **Adicione a coluna**: "ILUSTRAÇÃO HTML" na sua planilha
2. 🖼️ **Insira HTML**: Imagens, links ou qualquer HTML válido
3. 🔄 **Sincronize**: Execute uma sincronização normal
4. ✅ **Verifique**: Os cards existentes agora mostrarão as ilustrações no verso

---

*Esta funcionalidade garante que todos os seus cards antigos sejam automaticamente atualizados para suportar a nova coluna ILUSTRAÇÃO HTML, sem perder nenhum dado ou configuração existente.*
