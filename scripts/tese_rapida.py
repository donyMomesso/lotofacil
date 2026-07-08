#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Análise rápida apenas das conferências reais (sem simulação)
Para obter tese atualizada em segundos
"""
import csv
import json
import statistics
from collections import Counter

def carregar_conferencias():
    """Carrega todas as conferências"""
    conferencias = []
    with open("dados/conferencia.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dezenas_jogo = [int(x) for x in row["dezenas_jogo"].split("-")]
            conferencias.append({
                "concurso": int(row["concurso"]),
                "metodo": row["metodo"],
                "dezenas_jogo": dezenas_jogo,
                "acertos": int(row["acertos"]),
                "soma": sum(dezenas_jogo),
                "pares": sum(1 for d in dezenas_jogo if d % 2 == 0),
            })
    return conferencias

def gerar_tese(conferencias):
    """Analisa conferências reais e gera tese"""
    
    print("\n" + "="*70)
    print("  TESE ATUALIZADA - ANÁLISE DE CONFERÊNCIAS REAIS")
    print("="*70)
    
    print(f"\nTotal de conferências: {len(conferencias)}")
    
    # Vencedores (>=11)
    vencedores = [c for c in conferencias if c["acertos"] >= 11]
    print(f"Vencedores (>=11): {len(vencedores)}")
    
    if vencedores:
        print("\n  Vencedores encontrados:")
        for v in vencedores:
            print(f"    - Concurso {v['concurso']} {v['metodo']}: {v['acertos']} acertos, soma={v['soma']}, pares={v['pares']}")
    
    # Análise por método
    print(f"\n{'='*70}")
    print(f"DESEMPENHO POR MÉTODO")
    print(f"{'='*70}")
    
    por_metodo = {}
    for c in conferencias:
        if c["metodo"] not in por_metodo:
            por_metodo[c["metodo"]] = []
        por_metodo[c["metodo"]].append(c)
    
    for metodo in sorted(por_metodo.keys()):
        jogos = por_metodo[metodo]
        acertos_list = [j["acertos"] for j in jogos]
        media = statistics.mean(acertos_list)
        winners = len([a for a in acertos_list if a >= 11])
        taxa = (winners / len(jogos) * 100) if jogos else 0
        
        print(f"\n{metodo}:")
        print(f"  - Jogos: {len(jogos)}")
        print(f"  - Média de acertos: {media:.2f}")
        print(f"  - Vencedores: {winners} ({taxa:.1f}%)")
        print(f"  - Distribuição: {Counter(acertos_list)}")
    
    # Se tiver vencedores, analisa padrões
    if vencedores:
        print(f"\n{'='*70}")
        print(f"PADRÕES NOS VENCEDORES")
        print(f"{'='*70}")
        
        # Dezenas
        todas_dezenas = []
        for v in vencedores:
            todas_dezenas.extend(v["dezenas_jogo"])
        
        freq_dezenas = Counter(todas_dezenas)
        print(f"\nTop dezenas:")
        for dezena, freq in freq_dezenas.most_common(10):
            pct = (freq / len(vencedores)) * 100
            print(f"  {dezena:2d}: {freq}x ({pct:5.1f}%)")
        
        # Soma
        somas = [v["soma"] for v in vencedores]
        print(f"\nSoma:")
        print(f"  - Média: {statistics.mean(somas):.1f}")
        print(f"  - Moda: {Counter(somas).most_common(1)[0][0]}")
        print(f"  - Range: {min(somas)}-{max(somas)}")
        
        # Paridade
        pares = [v["pares"] for v in vencedores]
        print(f"\nParidade (pares):")
        print(f"  - Média: {statistics.mean(pares):.1f}")
        print(f"  - Moda: {Counter(pares).most_common(1)[0][0]}")
        print(f"  - Distribuição: {Counter(pares)}")
        
        # Tese
        tese = {
            "data_analise": "2026-07-08",
            "total_conferencias": len(conferencias),
            "total_vencedores": len(vencedores),
            "taxa_vencimento_pct": round((len(vencedores) / len(conferencias) * 100), 2),
            "vencedores_por_metodo": {m: len([c for c in por_metodo[m] if any(a >= 11 for a in [c["acertos"]])]) for m in por_metodo},
            "dezenas_top_5": [d[0] for d in freq_dezenas.most_common(5)],
            "soma_media": round(statistics.mean(somas), 1),
            "soma_moda": Counter(somas).most_common(1)[0][0],
            "soma_range": f"{min(somas)}-{max(somas)}",
            "pares_media": round(statistics.mean(pares), 1),
            "pares_moda": Counter(pares).most_common(1)[0][0],
        }
        
        return tese
    else:
        print("\n[N/A] Sem vencedores conferidos ainda")
        return None

if __name__ == "__main__":
    conferencias = carregar_conferencias()
    tese = gerar_tese(conferencias)
    
    if tese:
        with open("TESE_REALIDADE.json", "w", encoding="utf-8") as f:
            json.dump(tese, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Tese salva em TESE_REALIDADE.json")
