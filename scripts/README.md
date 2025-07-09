# 🚀 Scripts de Build - Sheets2Anki

Esta pasta contém todos os scripts necessários para fazer o build do add-on Sheets2Anki.

## 📋 Scripts Disponíveis

### 1. **Script Shell (Linux/macOS)** - `build.sh`
```bash
# Build completo (com testes)
./scripts/build.sh

# Build rápido (sem testes)
./scripts/build.sh --skip-tests
```

### 2. **Script Batch (Windows)** - `build.bat`
```cmd
REM Build completo (com testes)
scripts\build.bat

REM Build rápido (sem testes)
scripts\build.bat --skip-tests
```

### 3. **Makefile (Universal)** - `Makefile`
```bash
# Ver comandos disponíveis
make -f scripts/Makefile help

# Build completo
make -f scripts/Makefile build

# Build rápido
make -f scripts/Makefile build-quick

# Executar testes
make -f scripts/Makefile test

# Limpar build
make -f scripts/Makefile clean
```

### 4. **Python Direto** - `prepare_ankiweb.py`
```bash
# Executar diretamente
python scripts/prepare_ankiweb.py
```

## 🎯 Resultados

Todos os scripts criam:
- **`build/sheets2anki.ankiaddon`** - Arquivo principal para upload no AnkiWeb
- **`build/sheets2anki-backup.zip`** - Backup em formato ZIP

## 📦 Estrutura do Build

```
build/
├── sheets2anki.ankiaddon    # 🚀 Upload no AnkiWeb
├── sheets2anki-backup.zip   # 📦 Backup
└── sheets2anki/             # 📁 Conteúdo extraído
    ├── __init__.py
    ├── manifest.json
    ├── config.json
    ├── src/
    └── libs/
```

## ✅ Validações Automáticas

Os scripts verificam:
- ✓ Arquivos obrigatórios presentes
- ✓ `manifest.json` válido
- ✓ Estrutura de diretórios correta
- ✓ Remoção de arquivos desnecessários
- ✓ Limpeza automática de `meta.json` (se existir)

## 🚀 Publicação no AnkiWeb

1. Execute qualquer script de build
2. Acesse: https://ankiweb.net/shared/addons/
3. Faça upload de `build/sheets2anki.ankiaddon`
4. Preencha as informações do add-on

## 💡 Dicas

- Use `--skip-tests` para builds rápidos durante desenvolvimento
- Execute os scripts a partir do diretório raiz do projeto
- Todos os scripts são coloridos para melhor visualização
- Em caso de erro, o script para e mostra a causa
