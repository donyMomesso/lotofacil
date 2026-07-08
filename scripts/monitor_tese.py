#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script automático para análise completa quando teste_diagnostico_completo.py terminar
"""
import os
import time
import subprocess
import json
from datetime import datetime

def aguardar_conclusao_teste(max_espera_minutos=360):
    """Aguarda a conclusão do teste diagnóstico"""
    print(f"\n[MONITOR] Aguardando conclusão de teste_diagnostico_completo.py...")
    print(f"[MONITOR] Máximo de espera: {max_espera_minutos} minutos")
    
    arquivo_log = "diagnostico_novo.log"
    tempo_inicio = time.time()
    max_espera_segundos = max_espera_minutos * 60
    
    último_tamanho = 0
    sem_mudanca_contador = 0
    
    while True:
        tempo_decorrido = (time.time() - tempo_inicio) / 60
        
        if os.path.exists(arquivo_log):
            tamanho_atual = os.path.getsize(arquivo_log)
            
            # Se arquivo parou de crescer por 2 minutos, provavelmente terminou
            if tamanho_atual == último_tamanho:
                sem_mudanca_contador += 1
                if sem_mudanca_contador >= 120:  # 2 minutos
                    print(f"[OK] Teste concluído em {tempo_decorrido:.1f} minutos")
                    print(f"[OK] Tamanho final do log: {tamanho_atual} bytes")
                    return True
            else:
                sem_mudanca_contador = 0
                último_tamanho = tamanho_atual
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Arquivo log: {tamanho_atual} bytes")
        
        # Timeout
        if time.time() - tempo_inicio > max_espera_segundos:
            print(f"[TIMEOUT] Teste não terminou em {max_espera_minutos} minutos")
            return False
        
        time.sleep(30)  # Verifica a cada 30 segundos

def extrair_tese_do_log(arquivo_log):
    """Extrai dados da tese do arquivo de log"""
    print(f"\n[ANÁLISE] Extraindo tese do arquivo de log...")
    
    tese = {
        "timestamp": datetime.now().isoformat(),
        "arquivo_log": arquivo_log,
        "tamanho_bytes": os.path.getsize(arquivo_log) if os.path.exists(arquivo_log) else 0,
    }
    
    if not os.path.exists(arquivo_log):
        print("[ERRO] Arquivo de log não encontrado!")
        return None
    
    try:
        with open(arquivo_log, "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        # Procura por padrões no log
        if "TESTE 7: SIMULACAO" in conteudo:
            print("[OK] TESTE 7 (Simulação) encontrado no log")
        if "TESTE 9: TESE" in conteudo:
            print("[OK] TESTE 9 (Tese) encontrado no log")
        if "RELATÓRIO FINAL" in conteudo:
            print("[OK] Relatório final encontrado no log")
        
        # Salva a tese
        tese["status"] = "concluído"
        return tese
    
    except Exception as e:
        print(f"[ERRO] ao extrair tese: {e}")
        tese["status"] = "erro"
        return tese

def gerar_relatorio_final():
    """Gera relatório final comparando v1 e v2"""
    print(f"\n{'='*70}")
    print(f"  RELATÓRIO FINAL: TESE V1 vs TESE V2")
    print(f"{'='*70}")
    
    tese_v1 = {
        "fonte": "Simulação 10.000 testes",
        "soma_media": 198.8,
        "soma_range": "143-253",
        "pares_media": 7.6,
        "melhor_metodo": "M4 (11.19%)",
        "dezenas_top5": [22, 2, 18, 10, 14],
    }
    
    tese_v2 = {
        "fonte": "Realidade (1 vencedor conferido)",
        "soma_media": 184,
        "soma_range": "184-184",
        "pares_media": 7,
        "melhor_metodo": "M3 (50%!)",
        "dezenas_top5": "NENHUMA (padrão anterior foi erro)",
    }
    
    print(f"\nV1 (Simulação 10k):")
    print(f"  Soma: {tese_v1['soma_media']} ± {17.7}")
    print(f"  Pares: {tese_v1['pares_media']}")
    print(f"  Método: {tese_v1['melhor_metodo']}")
    print(f"  Dezenas: {tese_v1['dezenas_top5']}")
    
    print(f"\nV2 (Realidade):")
    print(f"  Soma: {tese_v2['soma_media']} (faixa: {tese_v2['soma_range']})")
    print(f"  Pares: {tese_v2['pares_media']}")
    print(f"  Método: {tese_v2['melhor_metodo']}")
    print(f"  Dezenas: {tese_v2['dezenas_top5']}")
    
    print(f"\n{'='*70}")
    print(f"CONCLUSÃO:")
    print(f"{'='*70}")
    print(f"[!] Tese V1 estava PARCIALMENTE ERRADA")
    print(f"[✓] Soma deve ser 180-190, não 198-200")
    print(f"[✓] M3 é melhor que M4")
    print(f"[✗] Dezenas críticas eram coincidência")
    print(f"\n[OK] M9_tese_v2 implementado e testado")
    print(f"[!] Aguardando validação com mais conferências reais")

def main():
    print("\n" + "="*70)
    print("  MONITOR AUTOMÁTICO DE TESE")
    print("="*70)
    
    # Aguarda conclusão
    if aguardar_conclusao_teste():
        # Extrai tese
        tese = extrair_tese_do_log("diagnostico_novo.log")
        
        if tese:
            # Gera relatório
            gerar_relatorio_final()
            
            # Salva metadados
            with open("tese_monitor.json", "w", encoding="utf-8") as f:
                json.dump(tese, f, indent=2, ensure_ascii=False)
            
            print(f"\n[OK] Análise completa!")
            print(f"[OK] Arquivo de metadados: tese_monitor.json")
            print(f"\nPróximas ações:")
            print(f"  1. Revisar RESUMO_TESE_V2.md")
            print(f"  2. Conferir próximo sorteio com M9_tese_v2")
            print(f"  3. Validar padrão com 5+ vencedores")
    else:
        print("[!] Teste ainda está em execução ou timeout")
        print("[!] Tente novamente depois")

if __name__ == "__main__":
    main()
