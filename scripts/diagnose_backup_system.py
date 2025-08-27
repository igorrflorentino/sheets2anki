#!/usr/bin/env python3
"""
Diagnóstico completo do sistema de backup do Sheets2Anki.
"""

import sys
import os
import json
from pathlib import Path

def diagnose_backup_system():
    """Diagnóstica problemas no sistema de backup."""
    
    print("🔍 DIAGNÓSTICO: Sistema de Backup Sheets2Anki")
    print("=" * 55)
    
    project_root = Path("/Users/igorflorentino/• Principais do Home/Git/Coding/anki/sheets2anki")
    
    # Verificar arquivos relacionados a backup
    backup_files = [
        "src/backup_system.py",
        "src/backup_dialog.py", 
        "src/backup_manager.py",
        "config.json",
        "meta.json"
    ]
    
    print("📁 VERIFICAÇÃO DE ARQUIVOS:")
    existing_files = []
    missing_files = []
    
    for file_path in backup_files:
        full_path = project_root / file_path
        if full_path.exists():
            existing_files.append(file_path)
            print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} (FALTANDO)")
    
    # Analisar problemas detectados
    print(f"\n🔍 PROBLEMAS DETECTADOS:")
    
    problems = []
    
    # Problema 1: Import conflicts
    if "src/backup_manager.py" in missing_files:
        problems.append({
            'id': 'IMPORT_ERROR',
            'severity': '🔴 CRÍTICO',
            'issue': 'backup_dialog.py importa backup_manager que não existe',
            'impact': 'Diálogo de backup não funciona',
            'solution': 'Corrigir import para usar BackupManager de backup_system.py'
        })
    
    # Problema 2: Backup automático não implementado
    problems.append({
        'id': 'AUTO_BACKUP_MISSING',
        'severity': '🟡 MÉDIO',
        'issue': 'backup_before_sync=true no config mas não implementado',
        'impact': 'Backup automático antes da sync não funciona',
        'solution': 'Implementar chamada de backup automático em sync.py'
    })
    
    # Problema 3: Duplicação de código
    problems.append({
        'id': 'CODE_DUPLICATION',
        'severity': '🟡 MÉDIO', 
        'issue': 'BackupManager duplicado em backup_system.py',
        'impact': 'Código duplicado e confuso',
        'solution': 'Consolidar em uma classe única'
    })
    
    # Problema 4: Interface desconectada
    problems.append({
        'id': 'DIALOG_DISCONNECT',
        'severity': '🔴 CRÍTICO',
        'issue': 'backup_dialog.py não consegue instanciar BackupManager',
        'impact': 'Interface de backup não funciona',
        'solution': 'Corrigir referências e imports'
    })
    
    # Problema 5: Falta de integração com sync
    problems.append({
        'id': 'SYNC_INTEGRATION',
        'severity': '🟡 MÉDIO',
        'issue': 'Backup automático não é chamado durante sincronização',
        'impact': 'Configuração backup_before_sync ignorada',
        'solution': 'Adicionar lógica de backup em sync.py'
    })
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{i}. {problem['severity']} {problem['id']}")
        print(f"   📋 Problema: {problem['issue']}")
        print(f"   💥 Impacto: {problem['impact']}")
        print(f"   🔧 Solução: {problem['solution']}")
    
    print(f"\n" + "=" * 55)
    print("📊 ANÁLISE DETALHADA:")
    
    # Verificar configuração atual
    try:
        with open(project_root / "meta.json", 'r', encoding='utf-8') as f:
            meta = json.load(f)
        
        config = meta.get("config", {})
        backup_before_sync = config.get("backup_before_sync", False)
        
        print(f"   ⚙️  backup_before_sync: {backup_before_sync}")
        if backup_before_sync:
            print(f"   ⚠️  Configuração ativa mas funcionalidade não implementada!")
    except Exception as e:
        print(f"   ❌ Erro ao ler meta.json: {e}")
    
    # Analisar estrutura do backup_system.py
    try:
        backup_system_path = project_root / "src/backup_system.py"
        with open(backup_system_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se há duplicação de classes
        if content.count("class BackupManager") > 1:
            print(f"   🔴 DUPLICAÇÃO: Múltiplas classes BackupManager encontradas")
        
        # Verificar se show_backup_dialog existe
        if "def show_backup_dialog" in content:
            print(f"   ✅ show_backup_dialog definida em backup_system.py")
        
    except Exception as e:
        print(f"   ❌ Erro ao analisar backup_system.py: {e}")
    
    print(f"\n" + "=" * 55)
    print("🎯 SOLUÇÕES RECOMENDADAS:")
    
    solutions = [
        "1. 🔧 Corrigir import em backup_dialog.py:",
        "   - Trocar 'from .backup_manager import BackupManager'", 
        "   - Por 'from .backup_system import BackupManager'",
        "",
        "2. 🔄 Implementar backup automático em sync.py:",
        "   - Verificar config backup_before_sync",
        "   - Chamar BackupManager.create_backup() antes da sync",
        "   - Definir local padrão para backups automáticos",
        "",
        "3. 🧹 Limpar duplicação de código:",
        "   - Remover classe BackupManager duplicada",
        "   - Manter apenas uma implementação",
        "",
        "4. 🧪 Testar funcionalidade completa:",
        "   - Backup manual via interface",
        "   - Backup automático durante sync",
        "   - Restauração de backups",
        "",
        "5. 📁 Definir estrutura de backup:",
        "   - Diretório padrão para backups",
        "   - Naming convention para arquivos",
        "   - Limpeza automática de backups antigos"
    ]
    
    for solution in solutions:
        print(f"   {solution}")
    
    print(f"\n" + "=" * 55)
    print("🎯 PRIORIDADE DE CORREÇÃO:")
    print("   🔴 CRÍTICO: Corrigir imports (backup não funciona)")
    print("   🟡 MÉDIO: Implementar backup automático")
    print("   🟢 BAIXO: Limpeza e otimização do código")
    
    return len([p for p in problems if 'CRÍTICO' in p['severity']])

def main():
    """Função principal."""
    try:
        critical_issues = diagnose_backup_system()
        if critical_issues > 0:
            print(f"\n🚨 {critical_issues} PROBLEMAS CRÍTICOS ENCONTRADOS!")
            print("⚠️  Sistema de backup não está funcionando corretamente")
            return 1
        else:
            print(f"\n✅ NENHUM PROBLEMA CRÍTICO DETECTADO")
            return 0
    except Exception as e:
        print(f"\n💥 ERRO DURANTE DIAGNÓSTICO: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
