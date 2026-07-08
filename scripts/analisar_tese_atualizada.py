#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para analisar melhorias na tese comparando dados antigos vs novos
"""
import csv
import json
import statistics
from collections import Counter
import sys

def carregar_conferencias():
    """Carrega todas as conferências do CSV"""
    conferencias = []
    with open("dados/conferencia.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            conferencias.append({
                "concurso": int(row["concurso"]),
                "metodo": row["metodo"],
                "dezenas_jogo": set(int(x) for x in row["dezenas_jogo"].split("-")),
                "dezenas_sorteadas": set(int(x) for x in row["dezenas_sorteadas"].split("-")),
                "acertos": int(row["acertos"]),
                "soma_jogo": sum(int(x) for x in row["dezenas_jogo"].split("-")),
                "pares_jogo": sum(1 for x in row["dezenas_jogo"].split("-") if int(x) % 2 == 0),
            })
    return conferencias

def analisar_vencedores(conferencias, threshold=11):
    """Extrai vencedores (>=11 acertos) e calcula padrões"""
    vencedores = [c for c in conferencias if c["acertos"] >= threshold]
    
    print(f"\n{'='*70}")
    print(f"ANÁLISE DE VENCEDORES (>={threshold} acertos)")
    print(f"{'='*70}")
    print(f"\nTotal de conferências: {len(conferencias)}")
    print(f"Vencedores encontrados: {len(vencedores)}")
    print(f"Taxa de vencimento: {(len(vencedores)/len(conferencias)*100):.2f}%")
    
    if not vencedores:
        print("[N/A] Sem vencedores para análise")
        return None
    
    # Análise por método
    vencedores_por_metodo = {}
    for v in vencedores:
        if v["metodo"] not in vencedores_por_metodo:
            vencedores_por_metodo[v["metodo"]] = []
        vencedores_por_metodo[v["metodo"]].append(v)
    
    print(f"\n{'='*70}")
    print(f"VENCEDORES POR MÉTODO")
    print(f"{'='*70}")
    for metodo in sorted(vencedores_por_metodo.keys()):
        winners = vencedores_por_metodo[metodo]
        print(f"\n{metodo}: {len(winners)} vencedor(es)")
        if winners:
            acertos_list = [w["acertos"] for w in winners]
            print(f"  - Média de acertos: {statistics.mean(acertos_list):.2f}")
            print(f"  - Distribuição: {Counter(acertos_list)}")
    
    # Análise de dezenas críticas
    print(f"\n{'='*70}")
    print(f"DEZENAS CRÍTICAS (frequência em vencedores)")
    print(f"{'='*70}")
    
    todas_dezenas_vencedores = []
    for v in vencedores:
        todas_dezenas_vencedores.extend(v["dezenas_jogo"])
    
    freq_dezenas = Counter(todas_dezenas_vencedores)
    top_10 = freq_dezenas.most_common(10)
    
    print(f"\nTop 10 dezenas em vencedores:")
    for dezena, freq in top_10:
        pct = (freq / len(vencedores)) * 100
        print(f"  {dezena:2d}: {freq:3d}x ({pct:5.1f}% dos vencedores)")
    
    # Análise de soma
    print(f"\n{'='*70}")
    print(f"PADRÃO DE SOMA")
    print(f"{'='*70}")
    somas = [v["soma_jogo"] for v in vencedores]
    print(f"\nMédia: {statistics.mean(somas):.1f}")
    print(f"Desvio padrão: {statistics.stdev(somas):.1f}")
    print(f"Moda: {Counter(somas).most_common(1)[0][0]}")
    print(f"Range: {min(somas)} a {max(somas)}")
    print(f"Distribuição: {Counter(somas)}")
    
    # Análise de paridade
    print(f"\n{'='*70}")
    print(f"PADRÃO DE PARIDADE")
    print(f"{'='*70}")
    pares = [v["pares_jogo"] for v in vencedores]
    print(f"\nMédia de pares: {statistics.mean(pares):.1f}")
    print(f"Moda: {Counter(pares).most_common(1)[0][0]}")
    print(f"Distribuição: {Counter(pares)}")
    
    return {
        "total_vencedores": len(vencedores),
        "taxa_vencimento": len(vencedores) / len(conferencias),
        "dezenas_top_5": [d[0] for d in top_10[:5]],
        "soma_media": statistics.mean(somas),
        "soma_moda": Counter(somas).most_common(1)[0][0],
        "pares_media": statistics.mean(pares),
        "pares_moda": Counter(pares).most_common(1)[0][0],
        "vencedores_por_metodo": {m: len(winners) for m, winners in vencedores_por_metodo.items()},
    }

def comparar_teses(tese_anterior, tese_nova):
    """Compara a tese anterior com a nova"""
    print(f"\n{'='*70}")
    print(f"COMPARAÇÃO: TESE ANTERIOR vs TESE NOVA")
    print(f"{'='*70}")
    
    print(f"\nVENCEDORES:")
    print(f"  Anterior: {tese_anterior.get('total_vencedores', 'N/A')}")
    print(f"  Nova:     {tese_nova['total_vencedores']}")
    print(f"  Melhoria: {'+' if tese_nova['total_vencedores'] > tese_anterior.get('total_vencedores', 0) else ''}{tese_nova['total_vencedores'] - tese_anterior.get('total_vencedores', 0)}")
    
    print(f"\nTAXA DE VENCIMENTO:")
    print(f"  Anterior: {tese_anterior.get('taxa_vencimento', 0)*100:.3f}%")
    print(f"  Nova:     {tese_nova['taxa_vencimento']*100:.3f}%")
    print(f"  Melhoria: {(tese_nova['taxa_vencimento'] - tese_anterior.get('taxa_vencimento', 0))*100:+.3f}%")
    
    print(f"\nDEZENAS TOP 5:")
    print(f"  Anterior: {tese_anterior.get('dezenas_top_5', 'N/A')}")
    print(f"  Nova:     {tese_nova['dezenas_top_5']}")
    
    if tese_anterior.get('dezenas_top_5'):
        mesmas = set(tese_anterior['dezenas_top_5']) & set(tese_nova['dezenas_top_5'])
        print(f"  Coincidência: {len(mesmas)}/5 dezenas mantidas")
    
    print(f"\nSOMA MÉDIA:")
    print(f"  Anterior: {tese_anterior.get('soma_media', 'N/A'):.1f}")
    print(f"  Nova:     {tese_nova['soma_media']:.1f}")
    
    print(f"\nPARES MÉDIA:")
    print(f"  Anterior: {tese_anterior.get('pares_media', 'N/A'):.1f}")
    print(f"  Nova:     {tese_nova['pares_media']:.1f}")

if __name__ == "__main__":
    # Tese anterior (do teste diagnóstico anterior)
    tese_anterior = {
        "total_vencedores": 767,
        "taxa_vencimento": 0.00959,
        "dezenas_top_5": [22, 2, 18, 10, 14],
        "soma_media": 198.8,
        "soma_moda": 200,
        "pares_media": 7.6,
        "pares_moda": 8,
    }
    
    # Análise nova
    conferencias = carregar_conferencias()
    tese_nova = analisar_vencedores(conferencias, threshold=11)
    
    if tese_nova:
        comparar_teses(tese_anterior, tese_nova)
        
        # Salvar tese nova
        with open("TESE_ATUALIZADA.json", "w", encoding="utf-8") as f:
            json.dump(tese_nova, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Tese atualizada salva em TESE_ATUALIZADA.json")
