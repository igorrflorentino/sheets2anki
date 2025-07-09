# Análise de Compatibilidade - Anki 25.x

## Problemas Identificados

### 1. Versioning no manifest.json
- `min_point_version`: 20100 (muito antigo, para Anki 2.1.0)
- `max_point_version`: 20199 (limitado ao Anki 2.1.x)
- **Problema:** Anki 25.x usa versioning diferente

### 2. Imports Qt
- Uso de imports Qt antigos
- Constantes Qt podem ter mudado
- **Problema:** Qt 6.6.2 tem mudanças na API

### 3. API do Anki
- Algumas APIs podem ter sido depreciadas
- Novos métodos recomendados para algumas operações
- **Problema:** Compatibilidade com novas versões

### 4. Estrutura de Add-on
- Configuração pode não seguir padrões mais recentes
- **Problema:** AnkiWeb pode rejeitar estruturas antigas

## Plano de Refatoração

### Fase 1: Atualizar manifest.json
- Ajustar versioning para Anki 25.x
- Limpar configuração desnecessária
- Adicionar campos obrigatórios para AnkiWeb

### Fase 2: Modernizar imports Qt
- Atualizar imports para Qt6
- Criar layer de compatibilidade mais robusto
- Testar com Anki 25.x

### Fase 3: Verificar APIs do Anki
- Revisar uso de APIs depreciadas
- Atualizar para métodos recomendados
- Melhorar tratamento de erros

### Fase 4: Preparar para AnkiWeb
- Limpar código desnecessário
- Adicionar documentação obrigatória
- Testar instalação e desinstalação

## Próximos Passos
1. Começar com manifest.json
2. Atualizar imports
3. Testar funcionalidades básicas
4. Validar para publicação
