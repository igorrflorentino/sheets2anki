#!/usr/bin/env python3
"""
Teste simples para verificar se o diálogo de backup funciona
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Simular imports do Anki
sys.path.insert(0, str(project_root / "stubs"))

try:
    from src.backup_dialog import BackupDialog
    print("✅ BackupDialog importado com sucesso!")
    
    # Tentar criar uma instância (sem mostrar)
    dialog = BackupDialog(None)
    print("✅ BackupDialog criado com sucesso!")
    
    print("🎉 Teste de compatibilidade passou!")
    
except Exception as e:
    print(f"❌ Erro ao importar ou criar BackupDialog: {e}")
    import traceback
    traceback.print_exc()
