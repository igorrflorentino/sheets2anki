#!/usr/bin/env python3
"""
Teste específico para verificar QFrame.HLine
"""
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "stubs"))

try:
    from stubs.aqt.qt import QFrame
    print(f"QFrame importado: {QFrame}")
    print(f"QFrame.HLine = {QFrame.HLine}")
    print(f"QFrame.VLine = {QFrame.VLine}")
    print(f"QFrame.Sunken = {QFrame.Sunken}")
    print("✅ Teste passou!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
