# Uso da Coluna "ILUSTRAÇÃO HTML"

A coluna "ILUSTRAÇÃO HTML" permite inserir imagens e elementos HTML interativos nos seus cards do Anki.

## Como usar

### 1. Imagens simples
```html
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Google_Images_2015_logo.svg/1200px-Google_Images_2015_logo.svg.png">
```

### 2. Imagens clicáveis (links)
```html
<a href="https://www.google.com">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Google_Images_2015_logo.svg/1200px-Google_Images_2015_logo.svg.png">
</a>
```

### 3. Imagens com tamanho controlado
```html
<img src="https://exemplo.com/imagem.jpg" width="300" height="200">
```

### 4. Múltiplas imagens
```html
<div>
    <img src="https://exemplo.com/imagem1.jpg" width="150">
    <img src="https://exemplo.com/imagem2.jpg" width="150">
</div>
```

### 5. Imagens com legendas
```html
<figure>
    <img src="https://exemplo.com/diagrama.png" width="400">
    <figcaption>Diagrama explicativo do conceito</figcaption>
</figure>
```

## Características importantes

- O Anki renderiza HTML em tempo real, então as imagens aparecerão nos cards
- As imagens devem estar hospedadas online (URLs públicas)
- Se o campo estiver vazio, não aparecerá no card
- **O HTML aparece no VERSO do card**, após a resposta e informações complementares
- Ideal para ilustrar e contextualizar a resposta da pergunta
- Suporta qualquer tag HTML válida (divs, spans, links, etc.)

## Exemplo prático

Na sua planilha, na coluna "ILUSTRAÇÃO HTML", você pode inserir:

```html
<a href="https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Google_Images_2015_logo.svg/1200px-Google_Images_2015_logo.svg.png">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Google_Images_2015_logo.svg/1200px-Google_Images_2015_logo.svg.png" width="200">
</a>
```

Isso criará uma imagem clicável do logo do Google que aparecerá no card.
