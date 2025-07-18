# Sistema de Backup - Sheets2Anki

Este documento descreve o sistema de backup implementado para o Sheets2Anki, que permite exportar e importar configurações de decks remotos entre diferentes máquinas.

## 🎯 Funcionalidades

### 1. Backup Completo
- Backup de todas as configurações de decks remotos
- Backup das preferências do usuário
- Backup das configurações gerais do sistema
- Formato ZIP compactado para facilitar transferência

### 2. Restauração de Backup
- Restauração completa ou seletiva
- Backup de segurança automático antes da restauração
- Verificação de compatibilidade de versões

### 3. Exportação/Importação Seletiva
- Exportação de decks específicos
- Importação com opções de mesclagem
- Formato JSON para facilitar edição manual

### 4. Interface Gráfica
- Diálogo integrado ao menu do Anki
- Interface intuitiva com abas organizadas
- Progresso visual durante operações

### 5. Linha de Comando
- Script CLI para automação
- Suporte a operações em lote
- Integração com scripts de sistema

## 📋 Como Usar

### Interface Gráfica

1. **Acessar o Backup**
   - No Anki, vá em: `Ferramentas → Decks Remotos → Backup de Decks Remotos`
   - Ou use o atalho: `Ctrl+Shift+B`

2. **Criar Backup**
   - Aba "Criar Backup"
   - Escolha as opções desejadas
   - Selecione local para salvar
   - Clique em "Criar Backup"

3. **Restaurar Backup**
   - Aba "Restaurar Backup"
   - Selecione o arquivo de backup
   - Configure opções de restauração
   - Clique em "Restaurar Backup"

4. **Exportar/Importar Específico**
   - Aba "Exportar/Importar"
   - Selecione decks específicos para exportar
   - Ou importe configurações de outro arquivo

### Linha de Comando

```bash
# Criar backup completo
python backup_cli.py create meu_backup.zip

# Restaurar backup
python backup_cli.py restore meu_backup.zip --overwrite

# Exportar decks específicos
python backup_cli.py export meus_decks.json --decks "url1,url2"

# Importar configurações
python backup_cli.py import meus_decks.json --merge-mode overwrite

# Ver informações do backup
python backup_cli.py info meu_backup.zip

# Listar decks atuais
python backup_cli.py list
```

## 🗂️ Estrutura dos Arquivos

### Backup Completo (.zip)
```
backup.zip
├── backup_metadata.json      # Metadados do backup
├── configs/
│   ├── meta.json            # Configurações principais
│   └── config.json          # Configurações do sistema
├── decks/
│   ├── deck1_hash.json      # Configurações do deck 1
│   ├── deck2_hash.json      # Configurações do deck 2
│   └── ...
├── user_preferences.json    # Preferências do usuário
└── media/                   # Arquivos de mídia (futuro)
```

### Exportação Seletiva (.json)
```json
{
  "version": "1.0",
  "export_date": "2025-07-18T10:30:00",
  "export_type": "decks_config",
  "deck_count": 2,
  "decks": {
    "https://exemplo.com/deck1": {
      "name": "Meu Deck 1",
      "is_sync": true,
      "last_sync": "2025-07-18T10:00:00",
      // ... outras configurações
    },
    "https://exemplo.com/deck2": {
      "name": "Meu Deck 2",
      "is_sync": false,
      // ... outras configurações
    }
  },
  "user_preferences": {
    "deck_naming_mode": "automatic",
    "backup_before_sync": true,
    // ... outras preferências
  }
}
```

## 🔧 Configuração e Opções

### Opções de Backup
- **Configurações gerais**: Inclui config.json e meta.json
- **Configurações de decks**: Inclui todos os decks remotos
- **Preferências do usuário**: Inclui todas as preferências
- **Arquivos de mídia**: Reservado para futuro uso

### Opções de Restauração
- **Restauração seletiva**: Escolha quais componentes restaurar
- **Sobrescrever existentes**: Decide se sobrescreve configurações atuais
- **Backup de segurança**: Criado automaticamente antes da restauração

### Opções de Importação
- **Sobrescrever**: Substitui decks existentes
- **Pular**: Ignora decks que já existem
- **Perguntar**: Pergunta para cada conflito

## 🚀 Cenários de Uso

### 1. Migração entre Máquinas
```bash
# Na máquina antiga
python backup_cli.py create transferencia.zip

# Na máquina nova
python backup_cli.py restore transferencia.zip --overwrite
```

### 2. Backup Periódico
```bash
# Script automático
DATE=$(date +%Y%m%d_%H%M%S)
python backup_cli.py create "backup_$DATE.zip"
```

### 3. Compartilhamento de Configurações
```bash
# Exportar apenas alguns decks
python backup_cli.py export compartilhar.json --decks "url1,url2"

# Importar sem sobrescrever
python backup_cli.py import compartilhar.json --merge-mode skip
```

### 4. Backup de Segurança
- Backup automático antes de cada sincronização
- Backup manual antes de grandes mudanças
- Múltiplas versões de backup

## 🔒 Segurança

### Backup de Segurança
- Criado automaticamente antes de restaurar
- Salvo em `~/.sheets2anki_safety_backups/`
- Permite reverter alterações se necessário

### Validação de Dados
- Verificação de integridade dos arquivos
- Validação de compatibilidade de versões
- Verificação de estrutura de dados

### Privacidade
- Não inclui dados pessoais além das configurações
- URLs dos decks são preservadas exatamente como configuradas
- Nenhum dado é enviado para servidores externos

## 🛠️ Troubleshooting

### Problemas Comuns

1. **Backup muito grande**
   - Desmarque "Incluir arquivos de mídia"
   - Use exportação seletiva para decks específicos

2. **Erro de permissão**
   - Verifique permissões do diretório de destino
   - Use diretório diferente se necessário

3. **Backup corrompido**
   - Verifique integridade do arquivo ZIP
   - Use `python backup_cli.py info arquivo.zip` para diagnóstico

4. **Versão incompatível**
   - Backup pode ter sido criado em versão diferente
   - Tente restauração seletiva se houver problemas

### Logs e Debugging
- Mensagens de erro são exibidas no console
- Use o comando `info` para verificar detalhes do backup
- Verifique os arquivos de backup de segurança em caso de problemas

## 📚 Referência da API

### BackupManager
```python
from src.backup_manager import BackupManager

# Criar instância
backup_manager = BackupManager()

# Criar backup
success = backup_manager.create_backup("backup.zip", include_media=False)

# Restaurar backup
restore_options = {
    'configs': True,
    'decks': True,
    'preferences': True,
    'media': False,
    'overwrite': False
}
success = backup_manager.restore_backup("backup.zip", restore_options)

# Exportar configurações
success = backup_manager.export_decks_config("export.json", ["url1", "url2"])

# Importar configurações
success = backup_manager.import_decks_config("import.json", "skip")

# Obter informações
info = backup_manager.list_backup_info("backup.zip")
```

## 🎉 Conclusão

O sistema de backup do Sheets2Anki oferece uma solução completa para:
- ✅ Migração entre máquinas
- ✅ Backup de segurança
- ✅ Compartilhamento de configurações
- ✅ Automação via linha de comando
- ✅ Interface gráfica amigável

Para mais informações ou problemas, consulte a documentação do projeto ou abra uma issue no repositório.
