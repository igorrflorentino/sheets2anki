#!/usr/bin/env python3
"""
Teste específico para verificar QFrame.Shape e QFrame.Shadow
"""
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "stubs"))

try:
    from src.backup_dialog import BackupDialog, FRAME_HLINE, FRAME_SUNKEN
    print("✅ BackupDialog importado com sucesso!")
    print(f"✅ FRAME_HLINE = {FRAME_HLINE}")
    print(f"✅ FRAME_SUNKEN = {FRAME_SUNKEN}")
    
    # Tentar criar uma instância
    dialog = BackupDialog(None)
    print("✅ BackupDialog criado com sucesso!")
    
    # Testar constantes do QFrame
    from stubs.aqt.qt import QFrame
    print(f"✅ QFrame.HLine = {QFrame.HLine}")
    print(f"✅ QFrame.Shape.HLine = {QFrame.Shape.HLine}")
    print(f"✅ QFrame.Shadow.Sunken = {QFrame.Shadow.Sunken}")
    
    print("🎉 TESTE DE COMPATIBILIDADE PASSOU!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
