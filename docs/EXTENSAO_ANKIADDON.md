# Extensão .ankiaddon vs .zip - Anki Add-ons

## 🎯 Por que .ankiaddon é a Extensão Correta

### Diferenças Principais

#### `.ankiaddon` (Correto)
- **Padrão oficial** do Anki para add-ons
- **Reconhecido automaticamente** pelo Anki
- **Instalação direta** - duplo clique instala
- **AnkiWeb padrão** - aceito nativamente
- **Associação de arquivo** - abre no Anki

#### `.zip` (Backup/Desenvolvimento)
- Formato genérico de compressão
- Precisa ser extraído manualmente
- Usado para backup e desenvolvimento
- Não é reconhecido como add-on do Anki

### Como Funciona

#### Instalação via .ankiaddon
1. Usuário baixa `sheets2anki.ankiaddon`
2. Duplo clique no arquivo
3. Anki abre automaticamente
4. Add-on é instalado diretamente

#### Instalação via .zip (manual)
1. Usuário baixa arquivo .zip
2. Extrai manualmente
3. Copia para pasta de add-ons
4. Reinicia o Anki

### AnkiWeb e .ankiaddon

O **AnkiWeb** espera arquivos `.ankiaddon` porque:
- Melhor experiência do usuário
- Instalação automática
- Validação de formato
- Segurança aprimorada

### Nossa Implementação

#### ✅ Arquivo Principal
```
build/sheets2anki.ankiaddon  # Para AnkiWeb e usuários finais
```

#### ✅ Arquivo de Backup
```
build/sheets2anki-backup.zip  # Para desenvolvimento e backup
```

### Vantagens da Nossa Abordagem

1. **Arquivo .ankiaddon** - Pronto para AnkiWeb
2. **Arquivo .zip backup** - Para desenvolvimento
3. **Mesma estrutura interna** - Ambos contêm os mesmos arquivos
4. **Flexibilidade** - Suporta ambos os cenários

### Verificação

Para confirmar que funciona:

```bash
# Verificar estrutura interna do .ankiaddon
unzip -l build/sheets2anki.ankiaddon

# Deve mostrar:
# __init__.py
# manifest.json  
# config.json
# src/
# libs/
```

### Migração de Projetos Antigos

Se você tem um projeto usando `.zip`:
1. Renomeie de `.zip` para `.ankiaddon`
2. Mantenha a mesma estrutura interna
3. Teste no Anki

### Status Atual

✅ **Implementação Correta**
- Arquivo `.ankiaddon` criado
- Estrutura interna validada
- Pronto para AnkiWeb
- Backup `.zip` disponível

Esta mudança garante que o add-on seja instalado da forma mais fácil e segura possível pelos usuários do Anki.
