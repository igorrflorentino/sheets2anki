#!/usr/bin/env python3
"""
Script de linha de comando para backup de decks remotos do Sheets2Anki

Este script permite criar e restaurar backups sem precisar do Anki GUI.
Útil para automação e migração entre máquinas.

Uso:
    python backup_cli.py create [caminho_backup] [--include-media]
    python backup_cli.py restore [caminho_backup] [--overwrite]
    python backup_cli.py export [caminho_export] [--decks deck1,deck2,...]
    python backup_cli.py import [caminho_import] [--merge-mode overwrite|skip]
    python backup_cli.py info [caminho_backup]
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.backup_manager import BackupManager
from src.config_manager import get_meta


def create_backup(args):
    """Cria um backup completo"""
    backup_manager = BackupManager()
    
    # Determinar caminho do backup
    if args.output:
        backup_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"sheets2anki_backup_{timestamp}.zip"
    
    # Criar backup
    print(f"🚀 Criando backup: {backup_path}")
    success = backup_manager.create_backup(backup_path, args.include_media)
    
    if success:
        print(f"✅ Backup criado com sucesso: {backup_path}")
        return 0
    else:
        print("❌ Erro ao criar backup")
        return 1


def restore_backup(args):
    """Restaura um backup"""
    backup_manager = BackupManager()
    
    if not os.path.exists(args.backup_file):
        print(f"❌ Arquivo de backup não encontrado: {args.backup_file}")
        return 1
    
    # Opções de restauração
    restore_options = {
        'configs': True,
        'decks': True,
        'preferences': True,
        'media': True,
        'overwrite': args.overwrite
    }
    
    print(f"🚀 Restaurando backup: {args.backup_file}")
    success = backup_manager.restore_backup(args.backup_file, restore_options)
    
    if success:
        print("✅ Backup restaurado com sucesso")
        return 0
    else:
        print("❌ Erro ao restaurar backup")
        return 1


def export_decks(args):
    """Exporta configurações específicas de decks"""
    backup_manager = BackupManager()
    
    # Determinar caminho de exportação
    if args.output:
        export_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = f"sheets2anki_export_{timestamp}.json"
    
    # Processar lista de decks
    deck_urls = None
    if args.decks:
        deck_urls = [url.strip() for url in args.decks.split(',')]
    
    print(f"🚀 Exportando configurações: {export_path}")
    success = backup_manager.export_decks_config(export_path, deck_urls)
    
    if success:
        print(f"✅ Configurações exportadas com sucesso: {export_path}")
        return 0
    else:
        print("❌ Erro ao exportar configurações")
        return 1


def import_decks(args):
    """Importa configurações de decks"""
    backup_manager = BackupManager()
    
    if not os.path.exists(args.import_file):
        print(f"❌ Arquivo de importação não encontrado: {args.import_file}")
        return 1
    
    merge_mode = args.merge_mode or 'skip'
    
    print(f"🚀 Importando configurações: {args.import_file}")
    success = backup_manager.import_decks_config(args.import_file, merge_mode)
    
    if success:
        print("✅ Configurações importadas com sucesso")
        return 0
    else:
        print("❌ Erro ao importar configurações")
        return 1


def show_backup_info(args):
    """Mostra informações sobre um backup"""
    backup_manager = BackupManager()
    
    if not os.path.exists(args.backup_file):
        print(f"❌ Arquivo de backup não encontrado: {args.backup_file}")
        return 1
    
    info = backup_manager.list_backup_info(args.backup_file)
    
    if info:
        print(f"📋 Informações do backup: {args.backup_file}")
        print(f"   📅 Data de criação: {info.get('creation_date', 'Desconhecido')}")
        print(f"   📦 Versão: {info.get('backup_version', 'Desconhecido')}")
        print(f"   📊 Total de decks: {info.get('total_decks', 0)}")
        print(f"   📋 Conteúdo: {', '.join(info.get('contents', []))}")
        print(f"   🎯 Versão Anki: {info.get('anki_version', 'Desconhecido')}")
        print(f"   🎯 Versão Sheets2Anki: {info.get('sheets2anki_version', 'Desconhecido')}")
        return 0
    else:
        print("❌ Não foi possível ler informações do backup")
        return 1


def list_current_decks():
    """Lista os decks atualmente configurados"""
    try:
        meta_data = get_meta()
        decks = meta_data.get('decks', {})
        
        print(f"📊 Decks remotos configurados: {len(decks)}")
        
        if decks:
            for i, (url, config) in enumerate(decks.items(), 1):
                name = config.get('name', 'Sem nome')
                print(f"   {i}. {name}")
                print(f"      URL: {url}")
                print(f"      Sync: {'Sim' if config.get('is_sync', False) else 'Não'}")
                print()
        else:
            print("   Nenhum deck remoto configurado")
        
        return 0
        
    except Exception as e:
        print(f"❌ Erro ao listar decks: {e}")
        return 1


def main():
    """Função principal do CLI"""
    parser = argparse.ArgumentParser(
        description="Ferramenta de backup para Sheets2Anki",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  %(prog)s create backup.zip
  %(prog)s restore backup.zip --overwrite
  %(prog)s export export.json --decks "url1,url2"
  %(prog)s import export.json --merge-mode overwrite
  %(prog)s info backup.zip
  %(prog)s list
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Criar backup')
    create_parser.add_argument('output', nargs='?', help='Caminho do arquivo de backup')
    create_parser.add_argument('--include-media', action='store_true', 
                              help='Incluir arquivos de mídia')
    
    # Comando restore
    restore_parser = subparsers.add_parser('restore', help='Restaurar backup')
    restore_parser.add_argument('backup_file', help='Arquivo de backup')
    restore_parser.add_argument('--overwrite', action='store_true',
                               help='Sobrescrever configurações existentes')
    
    # Comando export
    export_parser = subparsers.add_parser('export', help='Exportar configurações')
    export_parser.add_argument('output', nargs='?', help='Arquivo de exportação')
    export_parser.add_argument('--decks', help='URLs dos decks separadas por vírgula')
    
    # Comando import
    import_parser = subparsers.add_parser('import', help='Importar configurações')
    import_parser.add_argument('import_file', help='Arquivo de importação')
    import_parser.add_argument('--merge-mode', choices=['overwrite', 'skip'],
                              help='Modo de mesclagem para conflitos')
    
    # Comando info
    info_parser = subparsers.add_parser('info', help='Mostrar informações do backup')
    info_parser.add_argument('backup_file', help='Arquivo de backup')
    
    # Comando list
    list_parser = subparsers.add_parser('list', help='Listar decks atuais')
    
    # Parse dos argumentos
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Executar comando
    try:
        if args.command == 'create':
            return create_backup(args)
        elif args.command == 'restore':
            return restore_backup(args)
        elif args.command == 'export':
            return export_decks(args)
        elif args.command == 'import':
            return import_decks(args)
        elif args.command == 'info':
            return show_backup_info(args)
        elif args.command == 'list':
            return list_current_decks()
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        print("\n❌ Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
