# Makefile para Sheets2Anki
# Uso: make build, make test, make clean

.PHONY: build test clean help

# Comando Python (detectar automaticamente)
PYTHON := $(shell command -v python3 2> /dev/null || echo python)

# Diretórios
BUILD_DIR := build
ANKIADDON_FILE := $(BUILD_DIR)/sheets2anki.ankiaddon

# Verificar se estamos no diretório correto e mudar se necessário
ifneq ($(wildcard ../manifest.json),)
    ROOT_DIR := ..
else
    ROOT_DIR := .
endif

help: ## Mostrar esta ajuda
	@echo "🚀 Sheets2Anki - Comandos Disponíveis:"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Criar build do add-on (.ankiaddon)
	@echo "📦 Criando build..."
	cd $(ROOT_DIR) && $(PYTHON) scripts/prepare_ankiweb.py
	@echo "✅ Build criado: $(ROOT_DIR)/$(ANKIADDON_FILE)"

test: ## Executar todos os testes
	@echo "🧪 Executando testes..."
	cd $(ROOT_DIR) && $(PYTHON) run_tests.py

build-quick: ## Criar build sem executar testes
	@echo "⚡ Build rápido (sem testes)..."
	cd $(ROOT_DIR) && $(PYTHON) scripts/prepare_ankiweb.py
	@echo "✅ Build criado: $(ROOT_DIR)/$(ANKIADDON_FILE)"

clean: ## Limpar arquivos de build
	@echo "🧹 Limpando build..."
	rm -rf $(ROOT_DIR)/$(BUILD_DIR)
	@echo "✅ Build limpo"

install-dev: ## Instalar dependências de desenvolvimento
	@echo "📥 Instalando dependências..."
	cd $(ROOT_DIR) && pip install -r requirements-dev.txt || echo "⚠️  requirements-dev.txt não encontrado"

check: ## Verificar estrutura do projeto
	@echo "🔍 Verificando estrutura..."
	@[ -f $(ROOT_DIR)/manifest.json ] && echo "✓ manifest.json" || echo "❌ manifest.json não encontrado"
	@[ -f $(ROOT_DIR)/config.json ] && echo "✓ config.json" || echo "❌ config.json não encontrado"
	@[ -f $(ROOT_DIR)/__init__.py ] && echo "✓ __init__.py" || echo "❌ __init__.py não encontrado"
	@[ -d $(ROOT_DIR)/src ] && echo "✓ src/" || echo "❌ src/ não encontrado"
	@[ -d $(ROOT_DIR)/libs ] && echo "✓ libs/" || echo "❌ libs/ não encontrado"

all: clean test build ## Limpar, testar e criar build completo

# Alvo padrão
.DEFAULT_GOAL := help
