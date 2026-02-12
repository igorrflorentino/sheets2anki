# Image Processor Config Dialog - Redesign Plan

## Padrões Identificados nos Outros Dialogs

### 1. **Color Scheme**
```python
# Dark Mode
{
    'bg': '#1e1e1e',
    'card_bg': '#2d2d2d',
    'text': '#ffffff',
    'text_secondary': '#b0b0b0',
    'border': '#404040',
    'accent_primary': '#2196F3',
    'accent_success': '#4CAF50',
    'button_bg': '#3d3d3d',
    'button_hover': '#4a4a4a',
}

# Light Mode  
{
    'bg': '#f5f5f5',
    'card_bg': '#ffffff',
    'text': '#1a1a1a',
    'text_secondary': '#666666',
    'border': '#d0d0d0',
    'accent_primary': '#1976D2',
    'accent_success': '#4CAF50',
    'button_bg': '#e0e0e0',
    'button_hover': '#d0d0d0',
}
```

### 2. **Header Style**
- QFrame com gradient
- border-radius: 12px
- padding: 5px no frame, 20/15 no layout interno
- Título: 18pt bold
- Descrição: 12pt opacity 0.9

### 3. **Layout Structure**
- Main layout: spacing 15, margins 20
- **SEM ScrollArea** nas outras janelas (elas usam tamanho fixo adequado)
- GroupBox com fontes 12pt, padding 12px, margin-top 16px

### 4. **Buttons**
- Cancel: button_bg com border
- OK/Save: accent_success sem border
- padding: 12px 25px
- font-size: 12pt

### 5. **Window Size**
- Minimum: ~550-750px width, 500-700px height
- Resize: sim, mas sem scroll

## Redesign Decisions

1. **REMOVER ScrollArea** - outros dialogs não usam
2. **Ajustar tamanho da janela** para caber todo conteúdo
3. **Usar color scheme padrão** do addon
4. **Simplificar estrutura** - sem containers extras
5. **Manter header gradient** mas seguir exato padrão
6. **QGroupBox simples** - sem cards elaborados

## New Target Size
- Window: 700x720 (sem scroll, tudo visível)
- Layout: 20px margins, 15px spacing entre sections
