# Documentação - Sheets2Anki

Esta pasta contém a documentação técnica e guias relacionados ao desenvolvimento e manutenção do add-on Sheets2Anki.

## Arquivos

### `CORRECAO_IMPORTS.md`
- **Descrição:** Documentação detalhada sobre a correção do erro de importação
- **Conteúdo:** 
  - Análise do problema original (`No module named 'sheet2anki-v2.remote_decks'`)
  - Correções aplicadas nos imports e estrutura
  - Verificação das mudanças
  - Status da resolução do problema

### `ANALISE_COMPATIBILIDADE.md`
- **Descrição:** Análise de compatibilidade com Anki 25.x
- **Conteúdo:**
  - Problemas identificados na versão original
  - Plano de refatoração implementado
  - Melhorias para compatibilidade

### `PREPARACAO_ANKIWEB.md`
- **Descrição:** Guia completo para preparação e publicação no AnkiWeb
- **Conteúdo:**
  - Checklist de compatibilidade
  - Arquivos necessários
  - Processo de validação
  - Status de preparação

### `MIGRACAO_MANIFEST.md`
- **Descrição:** Documentação sobre migração para manifest.json moderno
- **Conteúdo:**
  - Por que a mudança foi necessária
  - Diferenças entre os formatos
  - Migração implementada
  - Benefícios da atualização

### `EXTENSAO_ANKIADDON.md`
- **Descrição:** Explicação sobre uso de .ankiaddon vs .zip
- **Conteúdo:**
  - Diferenças entre extensões
  - Vantagens do .ankiaddon
  - Como o AnkiWeb processa arquivos
  - Nossa implementação

## Estrutura da Documentação

```
docs/
├── README.md                   # Este arquivo
├── CORRECAO_IMPORTS.md        # Guia de correção de imports
├── ANALISE_COMPATIBILIDADE.md # Análise de compatibilidade
├── PREPARACAO_ANKIWEB.md      # Preparação para AnkiWeb
├── MIGRACAO_MANIFEST.md       # Modernização para manifest.json
└── EXTENSAO_ANKIADDON.md      # Explicação .ankiaddon vs .zip
```

## Para Desenvolvedores

Se você está trabalhando no projeto Sheets2Anki, consulte:

1. **`CORRECAO_IMPORTS.md`** - Para entender como a estrutura de imports foi corrigida
2. **`ANALISE_COMPATIBILIDADE.md`** - Para entender as mudanças de compatibilidade
3. **`PREPARACAO_ANKIWEB.md`** - Para preparar o add-on para publicação
4. **`../tests/README.md`** - Para informações sobre como executar testes
5. **`../README.md`** - Para documentação geral do usuário

## Status do Projeto

### ✅ Refatoração Concluída
- Módulo de compatibilidade implementado
- Imports modernizados
- Manifest.json atualizado para Anki 25.x
- Config.json modernizado
- Testes de compatibilidade criados

### ✅ Preparação AnkiWeb
- Pacote otimizado criado
- Estrutura validada
- Pronto para upload

### 🎯 Próximos Passos
1. Testar no Anki 25.x real
2. Validar todas as funcionalidades
3. Publicar no AnkiWeb

## Contribuindo com a Documentação

Ao fazer mudanças significativas no projeto:
1. Documente as alterações importantes
2. Mantenha os guias atualizados
3. Adicione novos arquivos de documentação conforme necessário
4. Teste a documentação com novos desenvolvedores
