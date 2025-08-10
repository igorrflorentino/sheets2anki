#!/usr/bin/env python3
"""
Teste da nova lógica de criação de tags.
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Simular dados de uma nota para teste
def test_create_tags():
    # Importar as definições
    from templates_and_definitions import (
        ID, PERGUNTA, MATCH, ALUNOS, TOPICO, SUBTOPICO, CONCEITO, 
        BANCAS, ANO, CARREIRA, IMPORTANCIA, MORE_TAGS
    )
    
    # Dados de teste
    note_data = {
        ID: "001",
        PERGUNTA: "Teste pergunta",
        MATCH: "Teste resposta", 
        ALUNOS: "João, Maria, Pedro",
        TOPICO: "Geografia, História",
        SUBTOPICO: "Capitais, Descobrimentos",
        CONCEITO: "Capital Federal, Navegação",
        BANCAS: "FCC, CESPE, VUNESP",
        ANO: "2023, 2022",
        CARREIRA: "Concurso Público, Ensino Médio",
        IMPORTANCIA: "Alta",
        MORE_TAGS: "brasil;geografia;historia"
    }
    
    # Simular função create_tags_from_fields
    def clean_tag_text(text):
        """Limpa texto para uso como tag no Anki"""
        if not text or not isinstance(text, str):
            return ""
        import re
        cleaned = text.strip().replace(' ', '_').replace(':', '_').replace(';', '_')
        cleaned = re.sub(r'[^\w\-_]', '', cleaned)
        return cleaned
    
    tags = []
    TAG_ROOT = "Sheets2Anki"
    TAG_ALUNOS = "alunos"
    TAG_TOPICS = "topicos"
    TAG_SUBTOPICS = "subtopicos"
    TAG_CONCEPTS = "conceitos"
    TAG_BANCAS = "bancas"
    TAG_ANOS = "anos"
    TAG_CARREIRAS = "carreiras"
    TAG_IMPORTANCIA = "importancia"
    TAG_ADICIONAIS = "adicionais"
    
    # Tag raiz
    tags.append(TAG_ROOT)
    
    # 1. Tags de ALUNOS
    alunos = note_data.get(ALUNOS, '').strip()
    if alunos:
        for aluno in alunos.split(','):
            aluno_clean = clean_tag_text(aluno)
            if aluno_clean:
                tags.append(f"{TAG_ROOT}::{TAG_ALUNOS}::{aluno_clean}")
    
    # 2. Tags hierárquicas de TOPICO::SUBTOPICO::CONCEITO
    topico = note_data.get(TOPICO, '').strip()
    subtopico = note_data.get(SUBTOPICO, '').strip() 
    conceito = note_data.get(CONCEITO, '').strip()
    
    topicos = [clean_tag_text(t) for t in topico.split(',') if clean_tag_text(t)]
    subtopicos = [clean_tag_text(s) for s in subtopico.split(',') if clean_tag_text(s)]
    conceitos = [clean_tag_text(c) for c in conceito.split(',') if clean_tag_text(c)]
    
    for topico_clean in topicos:
        for subtopico_clean in subtopicos:
            for conceito_clean in conceitos:
                tags.append(f"{TAG_ROOT}::{TAG_TOPICS}::{topico_clean}::{TAG_SUBTOPICS}::{subtopico_clean}::{TAG_CONCEPTS}::{conceito_clean}")
    
    # 3. Tags diretas de CONCEITOS
    for conceito_clean in conceitos:
        tags.append(f"{TAG_ROOT}::{TAG_CONCEPTS}::{conceito_clean}")
    
    # 4. Tags de BANCAS
    bancas = note_data.get(BANCAS, '').strip()
    if bancas:
        for banca in bancas.split(','):
            banca_clean = clean_tag_text(banca)
            if banca_clean:
                tags.append(f"{TAG_ROOT}::{TAG_BANCAS}::{banca_clean}")
    
    # 5. Tags de ANOS
    ano = note_data.get(ANO, '').strip()
    if ano:
        for ano_item in ano.split(','):
            ano_clean = clean_tag_text(ano_item)
            if ano_clean:
                tags.append(f"{TAG_ROOT}::{TAG_ANOS}::{ano_clean}")
    
    # 6. Tags de CARREIRAS
    carreira = note_data.get(CARREIRA, '').strip()
    if carreira:
        for carr in carreira.split(','):
            carr_clean = clean_tag_text(carr)
            if carr_clean:
                tags.append(f"{TAG_ROOT}::{TAG_CARREIRAS}::{carr_clean}")
    
    # 7. Tags de IMPORTANCIA
    importancia = note_data.get(IMPORTANCIA, '').strip()
    if importancia:
        importancia_clean = clean_tag_text(importancia)
        if importancia_clean:
            tags.append(f"{TAG_ROOT}::{TAG_IMPORTANCIA}::{importancia_clean}")
    
    # 8. Tags ADICIONAIS
    tags_adicionais = note_data.get(MORE_TAGS, '').strip()
    if tags_adicionais:
        separadores = [',', ';']
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
    
    print("🏷️ Tags geradas:")
    print("================")
    for i, tag in enumerate(tags, 1):
        print(f"{i:2d}. {tag}")
    
    print(f"\n📊 Total de {len(tags)} tags criadas")

if __name__ == "__main__":
    test_create_tags()
