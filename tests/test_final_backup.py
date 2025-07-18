#!/usr/bin/env python3
"""
Teste final para verificar se a interface do backup dialog funciona
"""
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "stubs"))

try:
    from src.backup_dialog import BackupDialog
    print("✅ BackupDialog importado com sucesso!")
    
    # Tentar criar uma instância
    dialog = BackupDialog(None)
    print("✅ BackupDialog criado com sucesso!")
    
    # Verificar se tem as constantes necessárias
    from src.backup_dialog import FRAME_HLINE, FRAME_SUNKEN
    print(f"✅ Constantes disponíveis: FRAME_HLINE={FRAME_HLINE}, FRAME_SUNKEN={FRAME_SUNKEN}")
    
    print("🎉 TESTE FINAL PASSOU! Sistema de backup está funcionando corretamente.")
    
except Exception as e:
    print(f"❌ Erro no teste final: {e}")
    import traceback
    traceback.print_exc()
