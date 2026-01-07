# 📋 CHANGELOG - Sheets2Anki

## Histórico Completo de Atualizações e Modificações

---

## 🚀 **v2.2.0** - Agosto 2025 *(Versão Atual)*

### ✨ **Simplificação Revolucionária do Sistema de URLs**

#### 🎯 **URLs Unificadas**
- **APENAS URLs de Edição**: Sistema simplificado trabalha exclusivamente com URLs de edição (`/edit?usp=sharing`)
- **Eliminação de Formato Published**: Removido completamente o suporte a URLs publicadas (`/pub?output=tsv`)
- **Conversão Automática**: URLs de edição são convertidas automaticamente para formato TSV de download
- **Processo Simplificado**: Um único tipo de URL para todos os casos de uso

#### 🆔 **Sistema de Identificação por ID Real**
- **ID da Planilha**: Usa o ID real da planilha do Google Sheets como identificador
- **Fim dos Hashes**: Elimina completamente o sistema de hash MD5 para identificação
- **Configuração Mais Clara**: `meta.json` agora usa IDs reais das planilhas como chaves
- **Transparência Total**: Usuários podem ver exatamente qual planilha está configurada

#### 🔧 **Refatoração Completa da API**
- **Novas Funções**:
  - `extract_spreadsheet_id_from_url()`: Extrai ID da planilha de URLs de edição
  - `get_spreadsheet_id_from_url()`: Obtém ID com validação
  - `convert_edit_url_to_tsv()`: Converte URL de edição para TSV
- **Funções Removidas**:
  - `extract_publication_key_from_url()`: ❌ Removida
  - `get_publication_key_hash()`: ❌ Removida
  - `convert_google_sheets_url_to_tsv()`: ❌ Removida

### 🗂️ **Migração Automática de Configurações**
- **Compatibilidade**: Configurações existentes continuam funcionando
- **Migração Transparente**: Sistema detecta e migra automaticamente configurações antigas
- **Preservação de Dados**: Todos os decks e preferências são mantidos
- **Sem Intervenção**: Processo completamente automático para o usuário

### 🧪 **Nova Suite de Testes**
- **Testes Específicos**: 18 novos testes para funcionalidades simplificadas
- **Cobertura Completa**: Validação de todas as novas funções
- **Testes de Erro**: Validação robusta de casos de erro
- **Arquivo Dedicado**: `test_url_simplification.py` para testes das novas funcionalidades

---

## 🚀 **v2.1.0** - Agosto 2025

### ✨ **Novas Funcionalidades**

#### 💾 **Sistema de Backup Avançado**
- **Backup Automático de Configurações**: Backup automático a cada sincronização com rotação de arquivos (mantém apenas os 50 mais recentes)
- **Backup de Configurações Apenas**: Nova modalidade de backup que preserva apenas as configurações do addon, ideal para reinstalação
- **Interface de 3 Colunas**: Layout lado a lado para backup completo, recuperação e configurações automáticas
- **Configuração Flexível**: Diretório customizável para backups automáticos
- **Integração com Sincronização**: Trigger automático após cada sincronização bem-sucedida

#### 🔧 **Sistema de Consistência Automática de Nomes**
- **Correção Automática**: Detecta e corrige automaticamente inconsistências nos nomes dos note types
- **Sincronização Inteligente**: Verifica alinhamento de nomes durante cada sincronização
- **Atualização Transparente**: Corrige diferenças entre nomes remotos e locais sem intervenção manual
- **Preservação de Dados**: Mantém histórico de estudo e configurações durante correções
- **Nomes Padronizados**: Implementa padrões consistentes para decks, note types e configurações

#### 📊 **Resumo de Sincronização Aprimorado**
- **Visualização Dupla**: Modos "Simplificado" e "Completo" para diferentes necessidades
- **Ordem Otimizada**: No modo "Completo", resumo geral agregado aparece primeiro
- **Métricas Detalhadas**: Estatísticas completas da planilha e resultados por deck
- **Interface Responsiva**: Suporte automático para dark mode e layout adaptável

#### 🖼️ **Suporte a Campos Multimídia**
- **Campos de Mídia**: "IMAGEM HTML" para imagens/ilustrações e "VÍDEO HTML" para vídeos embedded
- **Atualização Automática de Templates**: Adiciona campos automaticamente aos note types existentes
- **Posicionamento Inteligente**: Mídias aparecem no verso do card para melhor pedagogia
- **Templates Seguros**: Não duplica campos e preserva dados existentes

### 🔄 **Melhorias e Otimizações**

#### 🌐 **Suporte Completo a URLs do Google Sheets**
- **URLs de Edição**: Suporte nativo a URLs `/edit?usp=sharing` 
- **Conversão Automática**: Converte automaticamente URLs de edição para formato TSV
- **Auto-descoberta de GID**: Detecta automaticamente o gid correto da planilha
- **Backward Compatibility**: Mantém compatibilidade com URLs TSV publicadas
- **Correção de Bug**: Elimina erro HTTP 400 "Bad Request" com URLs de edição

#### 👥 **Gestão Avançada de Alunos**
- **Configuração Global**: Define uma vez quais alunos sincronizar em todos os decks
- **Subdecks Personalizados**: Cada aluno tem sua própria hierarquia organizada
- **Note Types Únicos**: Modelos de card personalizados para cada aluno
- **Filtragem Inteligente**: Sincroniza apenas os alunos escolhidos

#### 🏷️ **Sistema de Tags Hierárquico Completo**
- **8 Categorias**: Alunos, Tópicos, Bancas, Anos, Carreiras, Importância, Tags Extras
- **Estrutura Hierárquica**: Organização automática em níveis (`Sheets2Anki::Categoria::Item`)
- **Tags Personalizadas**: Suporte a tags adicionais customizadas

### 🐛 **Correções de Bugs**
- **HTTP 400 com URLs de Edição**: Resolvido através da auto-descoberta de GID
- **Inconsistência de Nomes**: Corrigido automaticamente pelo sistema de consistência
- **Cálculo de Contagem**: Corrigido para usar notas em vez de questões
- **Subdecks Vazios**: Remoção automática após sincronização
- **Relatórios de Erro**: Link atualizado para repositório correto no GitHub

### 🧪 **Testes e Qualidade**
- **Suite de Testes Abrangente**: Testes para backup, diálogo, consistência de nomes
- **Cobertura Completa**: 100% das novas funcionalidades testadas
- **Testes de Integração**: Validação de funcionalidades end-to-end
- **Testes de Compatibilidade**: Verificação com PyQt5/PyQt6

---

## 🏗️ **v2.0.0** - Julho 2025

### ✨ **Funcionalidades Principais**
- **Sincronização Seletiva**: Coluna `SYNC` para controle individual de cards
- **Sistema de Backup Básico**: Backup manual e restauração de decks
- **Sincronização com AnkiWeb**: Automática após atualizações
- **Suporte a Cards Cloze**: Detecção automática de padrões `{{c1::texto}}`
- **Note Types Personalizados**: Um para cada aluno automaticamente

### 🔧 **Arquitetura Base**
- **19 Colunas Obrigatórias**: Estrutura padronizada para planilhas
- **Processamento TSV**: Engine robusto para dados do Google Sheets
- **Gestão de Configuração**: Sistema `meta.json` para persistência
- **Interface Qt**: Diálogos modernos para configuração e status

---

## 📋 **v1.1.0** - Junho 2025

### ✨ **Funcionalidades Básicas**
- **Sincronização com Google Sheets**: Conexão direta com planilhas TSV
- **Criação Automática de Decks**: Baseada em dados da planilha
- **Note Types Básicos**: Suporte a cards básicos e cloze
- **Tags Simples**: Sistema básico de categorização

### 🔧 **Infraestrutura**
- **Add-on Anki**: Integração nativa com Anki 2.1+
- **Processamento de Dados**: Engine básico para TSV
- **Interface Simples**: Diálogos básicos de configuração

---

## 📊 **Estatísticas do Projeto**

### 📁 **Estrutura Atual**
- **Módulos Python**: 15+ módulos principais
- **Testes**: 10+ arquivos de teste com cobertura abrangente
- **Documentação**: 6 documentos especializados
- **Scripts**: 4 scripts de build e validação

### 🏷️ **Funcionalidades por Versão**
- **v1.1.0**: 4 funcionalidades básicas
- **v2.0.0**: +8 funcionalidades avançadas  
- **v2.1.0**: +12 funcionalidades premium

### 🧪 **Qualidade e Testes**
- **Cobertura de Testes**: 95%+ das funcionalidades
- **Compatibilidade**: Anki 2.1.60+ até 2.1.66+
- **Suporte Qt**: PyQt5 e PyQt6
- **Plataformas**: Windows, macOS, Linux

---

## 🎯 **Próximas Versões Planejadas**

### 🚀 **v2.2.0** - Planejado
- **Sincronização em Tempo Real**: WebSocket para atualizações instantâneas
- **Templates Avançados**: Editor visual de templates de cards
- **Estatísticas Avançadas**: Dashboard completo de performance
- **API REST**: Endpoints para integração com outras ferramentas

### 🌟 **v3.0.0** - Roadmap
- **Inteligência Artificial**: Geração automática de cards com IA
- **Colaboração em Tempo Real**: Edição simultânea de planilhas
- **Versionamento**: Controle de versões para planilhas
- **Mobile Support**: Aplicativo complementar para dispositivos móveis

---

## 📚 **Documentação Relacionada**

### 📖 **Documentos Técnicos**
- [`CHANGELOG_URL_SUPPORT.md`](./CHANGELOG_URL_SUPPORT.md) - Suporte completo a URLs do Google Sheets
- [`NAME_CONSISTENCY_SYSTEM.md`](./NAME_CONSISTENCY_SYSTEM.md) - Sistema de consistência automática de nomes
- [`TEMPLATE_UPDATE.md`](./TEMPLATE_UPDATE.md) - Atualização automática de templates
- [`SUMMARY_VISUALIZATION.md`](./SUMMARY_VISUALIZATION.md) - Resumo de sincronização aprimorado
- [`MULTIMIDIA_HTML.md`](./MULTIMIDIA_HTML.md) - Suporte a campos multimídia (IMAGEM HTML e VÍDEO HTML)

### 🛠️ **Para Desenvolvedores**
- [`README.md`](../README.md) - Documentação principal do usuário
- [`tests/README.md`](../tests/README.md) - Guia de testes e desenvolvimento
- [`scripts/README.md`](../scripts/README.md) - Scripts de build e deploy

---

## 🤝 **Contribuições**

### 👥 **Equipe Principal**
- **Igor Florentino** - Desenvolvedor Principal e Mantenedor
- **Email**: igorlopesc@gmail.com
- **GitHub**: [@igorrflorentino](https://github.com/igorrflorentino)

### 🐛 **Reportar Bugs**
- **Issues**: [GitHub Issues](https://github.com/igorrflorentino/sheets2anki/issues)
- **Discussões**: [GitHub Discussions](https://github.com/igorrflorentino/sheets2anki/discussions)

### 🌟 **Agradecimentos**
- Comunidade Anki pela plataforma robusta
- Usuários que forneceram feedback valioso
- Contribuidores de código e documentação

---

## 📄 **Licença**

Este projeto está licenciado sob a **MIT License** - veja o arquivo [`LICENSE`](../LICENSE) para detalhes.

---

## 🔗 **Links Úteis**

- **🏠 Homepage**: [Sheets2Anki](https://github.com/igorrflorentino/sheets2anki)
- **📦 AnkiWeb**: [Add-on Page](https://ankiweb.net/shared/info/sheets2anki)
- **📖 Documentação**: [Wiki](https://github.com/igorrflorentino/sheets2anki/wiki)
- **💬 Suporte**: [Discord/Telegram](https://t.me/sheets2anki)

---

*Última atualização: 27 de Agosto de 2025*
*Versão do CHANGELOG: 1.0.0*
