# Migração para manifest.json - Anki 25.x

## 🔄 Mudança Importante: meta.json → manifest.json

### Por que a mudança?

A partir do **Anki 2.1.45+** (e especialmente no Anki 25.x), o Anki adotou o `manifest.json` como o arquivo padrão para metadados de add-ons, substituindo o `meta.json` antigo.

### Principais Diferenças

#### `meta.json` (Antigo)
- Usado até Anki 2.1.44
- Formato mais simples
- Incluía configurações inline

#### `manifest.json` (Novo - Anki 25.x)
- Padrão moderno desde Anki 2.1.45+
- Formato mais estruturado
- Configurações separadas (config.json)
- Melhor suporte a versionamento

### Migração Implementada

#### ✅ Arquivo Criado
```json
{
    "package": "sheets2anki",
    "name": "Sheets2Anki",
    "version": "2.0.0",
    "author": "Igor Florentino",
    "description": "Sincronize decks do Anki com planilhas do Google Sheets em formato TSV. Ideal para estudos de concursos com estrutura de questões em português.",
    "homepage": "https://github.com/igorflorentino/sheets2anki",
    "min_point_version": 231000,
    "max_point_version": 260000,
    "conflicts": [],
    "mod": 1673299200,
    "disabled": false
}
```

#### ✅ Campos Principais
- `package`: Identificador único do add-on
- `name`: Nome amigável
- `version`: Versão semântica
- `min_point_version`: Anki 23.10+ (231000)
- `max_point_version`: Até Anki 26.0 (260000)
- `mod`: Timestamp de modificação
- `disabled`: Estado do add-on

#### ✅ Scripts Atualizados
- `prepare_ankiweb.py`: Agora valida `manifest.json`
- `test_compatibility.py`: Verifica `manifest.json`
- Documentação atualizada

### Benefícios da Migração

1. **Compatibilidade Total**: Funciona perfeitamente com Anki 25.x
2. **Padrão Moderno**: Segue as melhores práticas atuais
3. **AnkiWeb Ready**: Totalmente compatível com AnkiWeb
4. **Versionamento Claro**: Melhor controle de versões

### Impacto nos Usuários

- **Usuários Finais**: Nenhum impacto, instalação normal
- **Desenvolvedores**: Precisam usar `manifest.json` para novos add-ons
- **AnkiWeb**: Reconhece automaticamente o formato moderno

### Verificação

Execute o teste de compatibilidade:
```bash
python tests/test_compatibility.py
```

Deve mostrar:
```
✓ manifest.json existe
✓ Nome: Sheets2Anki
✓ Versão: 2.0.0
✓ Versão mínima: 231000
✓ Versão máxima: 260000
✅ Configurado para versões modernas do Anki
```

### Status

✅ **Migração Concluída**
- `meta.json` removido
- `manifest.json` criado e validado
- Pacote AnkiWeb atualizado
- Pronto para Anki 25.x

Esta mudança garante que o add-on esteja totalmente alinhado com os padrões modernos do Anki e seja aceito no AnkiWeb sem problemas.
