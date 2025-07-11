# Scripts de Build e Empacotamento

Este diretório contém scripts Python para construir e validar os pacotes do add-on Sheets2Anki.

## Scripts Disponíveis

### `build_packages.py`
**Script principal e mais recomendado para uso geral.**

Menu interativo unificado que permite:
- Construir pacote para AnkiWeb (`.ankiaddon`)
- Construir pacote standalone (`.ankiaddon` com manifest completo)
- Validar pacotes existentes
- Limpar arquivos temporários

```bash
python scripts/build_packages.py
```

### `create_standalone_package.py`
Constrói especificamente o pacote para upload no AnkiWeb.

- Remove campos opcionais do manifest (mantém apenas os obrigatórios)
- Limpa todos os arquivos de cache (`__pycache__`, `.pyc`, `.pyo`)
- Gera `build/sheets2anki.ankiaddon` pronto para upload
- Valida a estrutura do pacote

```bash
python scripts/create_standalone_package.py
```

### `create_standalone_package.py`
Constrói um pacote standalone para distribuição independente.

- Mantém o manifest completo com todos os campos
- Limpa arquivos de cache
- Gera `build/sheets2anki-standalone.ankiaddon`
- Valida a estrutura do pacote

```bash
python scripts/create_standalone_package.py
```

### `validate_ankiaddon.py`
Valida pacotes `.ankiaddon` existentes.

- Verifica estrutura do ZIP
- Valida manifest.json
- Verifica ausência de arquivos de cache
- Lista todos os arquivos incluídos

```bash
python scripts/validate_ankiaddon.py build/sheets2anki.ankiaddon
```

## Workflow Recomendado

1. **Para desenvolvimento e testes**: Use `build_packages.py` para acesso rápido a todas as funções
2. **Para upload no AnkiWeb**: Use `create_standalone_package.py` ou a opção correspondente no menu
3. **Para distribuição independente**: Use `create_standalone_package.py` ou a opção correspondente no menu
4. **Para validação**: Use `validate_ankiaddon.py` ou a opção correspondente no menu

## Estrutura do Pacote

Os scripts garantem que os pacotes `.ankiaddon` sigam as especificações do AnkiWeb:

- ✅ Arquivos na raiz do ZIP (sem pasta pai)
- ✅ `manifest.json` válido e presente
- ✅ Ausência de arquivos `__pycache__`, `.pyc`, `.pyo`
- ✅ Estrutura de diretórios preservada (`src/`, `libs/`, etc.)

## Requisitos

- Python 3.6+
- Módulos padrão: `json`, `zipfile`, `os`, `shutil`, `tempfile`

Todos os scripts são auto-suficientes e não requerem dependências externas.
