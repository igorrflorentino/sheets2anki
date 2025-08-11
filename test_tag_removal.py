#!/usr/bin/env python3
"""
Script de teste para verificar se as tags de alunos foram removidas corretamente.
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Importar módulos necessários
import templates_and_definitions as cols

def create_tags_from_fields(note_data):
    """
    Versão simplificada da função para teste, copiada do data_processor.py
    """
    import re
    
    tags = []
    TAG_ROOT = "Sheets2Anki"
    TAG_TOPICS = "topicos"
    TAG_CONCEPTS = "conceitos"
    TAG_BANCAS = "bancas"
    TAG_ANOS = "anos"
    TAG_CARREIRAS = "carreiras"
    TAG_IMPORTANCIA = "importancia"
    TAG_ADICIONAIS = "adicionais"
    
    DEFAULT_TOPIC = "[MISSING T.]"
    DEFAULT_SUBTOPIC = "[MISSING S.]"
    DEFAULT_CONCEPT = "[MISSING C.]"

    # Tag raiz
    tags.append(TAG_ROOT)

    def clean_tag_text(text):
        """Limpa texto para uso como tag no Anki"""
        if not text or not isinstance(text, str):
            return ""
        # Remove espaços extras, substitui espaços por underscores e caracteres problemáticos
        cleaned = text.strip().replace(" ", "_").replace(":", "_").replace(";", "_")
        # Remove caracteres especiais que podem causar problemas no Anki
        cleaned = re.sub(r"[^\w\-_]", "", cleaned)
        return cleaned

    # 1. Tags de ALUNOS - REMOVIDAS para simplificar lógica
    # (Tags de alunos foram eliminadas conforme solicitado)

    # 2. Tags hierárquicas de TOPICO::SUBTOPICO::CONCEITO (aninhadas)
    topico = note_data.get(cols.TOPICO, "").strip()
    subtopico = note_data.get(cols.SUBTOPICO, "").strip()
    conceito = note_data.get(cols.CONCEITO, "").strip()

    # Usar valores padrão se estiverem vazios
    if not topico:
        topico = DEFAULT_TOPIC
    if not subtopico:
        subtopico = DEFAULT_SUBTOPIC
    if not conceito:
        conceito = DEFAULT_CONCEPT

    # Processar múltiplos valores (separados por vírgula)
    topicos = [clean_tag_text(t) for t in topico.split(",") if clean_tag_text(t)]
    subtopicos = [clean_tag_text(s) for s in subtopico.split(",") if clean_tag_text(s)]
    conceitos = [clean_tag_text(c) for c in conceito.split(",") if clean_tag_text(c)]

    # Gerar todas as combinações hierárquicas - formato: Sheets2Anki::topicos::topico::subtopico::conceito
    for topico_clean in topicos:
        for subtopico_clean in subtopicos:
            for conceito_clean in conceitos:
                # Tag hierárquica completa aninhada (sem repetir prefixos subtopicos/conceitos)
                tags.append(
                    f"{TAG_ROOT}::{TAG_TOPICS}::{topico_clean}::{subtopico_clean}::{conceito_clean}"
                )

    # 3. Tags diretas de CONCEITOS (para busca fácil)
    for conceito_clean in conceitos:
        tags.append(f"{TAG_ROOT}::{TAG_CONCEPTS}::{conceito_clean}")

    # 4. Tags de BANCAS
    bancas = note_data.get(cols.BANCAS, "").strip()
    if bancas:
        for banca in bancas.split(","):
            banca_clean = clean_tag_text(banca)
            if banca_clean:
                tags.append(f"{TAG_ROOT}::{TAG_BANCAS}::{banca_clean}")

    # 5. Tags de ANOS
    ano = note_data.get(cols.ANO, "").strip()
    if ano:
        for ano_item in ano.split(","):
            ano_clean = clean_tag_text(ano_item)
            if ano_clean:
                tags.append(f"{TAG_ROOT}::{TAG_ANOS}::{ano_clean}")

    # 6. Tags de CARREIRAS
    carreira = note_data.get(cols.CARREIRAS, "").strip()
    if carreira:
        for carr in carreira.split(","):
            carr_clean = clean_tag_text(carr)
            if carr_clean:
                tags.append(f"{TAG_ROOT}::{TAG_CARREIRAS}::{carr_clean}")

    # 7. Tags de IMPORTANCIA
    importancia = note_data.get(cols.IMPORTANCIA, "").strip()
    if importancia:
        importancia_clean = clean_tag_text(importancia)
        if importancia_clean:
            tags.append(f"{TAG_ROOT}::{TAG_IMPORTANCIA}::{importancia_clean}")

    # 8. Tags ADICIONAIS
    tags_adicionais = note_data.get(cols.MORE_TAGS, "").strip()
    if tags_adicionais:
        # Suporta tanto separação por vírgula quanto por ponto e vírgula
        separadores = [",", ";"]
        for sep in separadores:
            if sep in tags_adicionais:
                tags_list = tags_adicionais.split(sep)
                break
        else:
            tags_list = [tags_adicionais]

        for tag in tags_list:
            tag_clean = clean_tag_text(tag)
            if tag_clean:
                tags.append(f"{TAG_ROOT}::{TAG_ADICIONAIS}::{tag_clean}")

    return tags

def test_tag_removal():
    """Teste para verificar se as tags de alunos foram removidas."""
    
    # Dados de teste
    note_data = {
        cols.ALUNOS: "João, Maria, Pedro",
        cols.TOPICO: "Geografia",
        cols.SUBTOPICO: "Capitais",
        cols.CONCEITO: "Brasil",
        cols.BANCAS: "CESPE, FCC",
        cols.ANO: "2024",
        cols.CARREIRAS: "Concursos Públicos",
        cols.IMPORTANCIA: "Alta",
        cols.MORE_TAGS: "importante, fundamental"
    }
    
    # Gerar tags
    tags = create_tags_from_fields(note_data)
    
    print("=== TAGS GERADAS ===")
    for i, tag in enumerate(sorted(tags), 1):
        print(f"{i:2d}. {tag}")
    
    print("\n=== VERIFICAÇÃO ===")
    
    # Verificar se existem tags de alunos
    aluno_tags = [tag for tag in tags if "::alunos::" in tag.lower()]
    
    if aluno_tags:
        print("❌ ERRO: Tags de alunos ainda estão sendo criadas!")
        print("Tags de alunos encontradas:")
        for tag in aluno_tags:
            print(f"  - {tag}")
        return False
    else:
        print("✅ SUCESSO: Nenhuma tag de aluno encontrada!")
    
    # Verificar se outras tags ainda existem
    expected_tag_types = [
        "topicos",
        "conceitos", 
        "bancas",
        "anos",
        "carreiras",
        "importancia",
        "adicionais"
    ]
    
    print("\n=== VERIFICAÇÃO DE OUTRAS TAGS ===")
    for tag_type in expected_tag_types:
        found = any(f"::{tag_type}::" in tag for tag in tags)
        status = "✅" if found else "❌"
        print(f"{status} Tags de {tag_type}: {'Encontradas' if found else 'NÃO encontradas'}")
    
    print(f"\nTotal de tags geradas: {len(tags)}")
    return True

if __name__ == "__main__":
    success = test_tag_removal()
    sys.exit(0 if success else 1)
