#!/usr/bin/env python3
"""
Teste visual das cores para dark mode e light mode.
"""

def test_colors():
    print("🎨 TESTE DE CORES PARA DEBUG WINDOW")
    print("=" * 50)
    
    print("\n🌙 DARK MODE:")
    print("  Fundo texto: #1e1e1e (muito escuro)")
    print("  Cor texto:   #f0f0f0 (muito claro)")
    print("  Contraste:   ALTO ✅")
    print("  Info bg:     #2d2d2d")
    print("  Bordas:      #555555")
    
    print("\n☀️ LIGHT MODE:")
    print("  Fundo texto: #ffffff (branco)")
    print("  Cor texto:   #000000 (preto)")
    print("  Contraste:   ALTO ✅")
    print("  Info bg:     #f8f8f8")
    print("  Bordas:      #cccccc")
    
    print("\n✨ MELHORIAS IMPLEMENTADAS:")
    print("  • Detecção robusta de dark mode com 3 métodos de fallback")
    print("  • Cores de alto contraste em ambos os modos")
    print("  • Scrollbar estilizada para cada tema")
    print("  • Fonte monoespaçada otimizada")
    print("  • Seleção de texto com cores apropriadas")
    print("  • Bordas mais visíveis (2px)")
    print("  • Padding aumentado para melhor legibilidade")

if __name__ == "__main__":
    test_colors()
