#!/usr/bin/env python3
"""
TESTE DIAGNÓSTICO COMPLETO - Sistema Lotofácil
Testa todas as funções, métodos, simulações e gera diagnóstico abrangente.
"""

import sys
import os
import json
import csv
import statistics
import random
from datetime import datetime
from collections import Counter

# Adiciona path para importar lotofacil_lib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lotofacil_lib as lib

# Configuração de encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class TestadorDiagnostico:
    def __init__(self):
        self.relatorio = []
        self.erros = []
        self.avisos = []
        self.dados_teste = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def log(self, mensagem, nivel="INFO"):
        """Log formatado de mensagens."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.relatorio.append(f"[{timestamp}] [{nivel}] {mensagem}")
        print(f"[{timestamp}] [{nivel}] {mensagem}")
        
    def erro(self, mensagem):
        """Registra erro."""
        self.log(mensagem, "ERRO")
        self.erros.append(mensagem)
        
    def aviso(self, mensagem):
        """Registra aviso."""
        self.log(mensagem, "AVISO")
        self.avisos.append(mensagem)
        
    def secao(self, titulo):
        """Marca uma seção do relatório."""
        self.log(f"\n{'='*60}")
        self.log(f"  {titulo}")
        self.log(f"{'='*60}\n")
        
    # ========== TESTES DE INTEGRIDADE ==========
    def testar_integridade_arquivos(self):
        """Testa se os arquivos de dados existem e são legíveis."""
        self.secao("TESTE 1: INTEGRIDADE DE ARQUIVOS")
        
        arquivos = [
            lib.RESULTADOS_CSV,
            lib.JOGOS_CSV,
            lib.CONFERENCIA_CSV,
            lib.FREQUENCIA_CSV,
        ]
        
        for arq in arquivos:
            if os.path.exists(arq):
                try:
                    with open(arq, 'r', encoding='utf-8') as f:
                        linhas = len(f.readlines())
                    self.log(f"[OK] {os.path.basename(arq)}: {linhas} linhas")
                except Exception as e:
                    self.erro(f"[ERRO] {os.path.basename(arq)}: {str(e)}")
            else:
                self.aviso(f"[N/A] {os.path.basename(arq)}: não encontrado")
    
    # ========== TESTES DE DADOS ==========
    def testar_carregamento_dados(self):
        """Testa carregamento de todos os dados."""
        self.secao("TESTE 2: CARREGAMENTO DE DADOS")
        
        try:
            resultados = lib.carregar_resultados()
            self.log(f"[OK] Resultados carregados: {len(resultados)} concursos")
            self.dados_teste['resultados'] = resultados
            
            if len(resultados) == 0:
                self.aviso("[N/A] Nenhum resultado registrado no sistema")
            
        except Exception as e:
            self.erro(f"[ERRO] Erro ao carregar resultados: {str(e)}")
            
        try:
            jogos = lib.carregar_jogos()
            self.log(f"[OK] Jogos carregados: {len(jogos)} jogos")
            self.dados_teste['jogos'] = jogos
        except Exception as e:
            self.erro(f"[ERRO] Erro ao carregar jogos: {str(e)}")
            
        try:
            conferencias = lib.carregar_conferencias()
            self.log(f"[OK] Conferências carregadas: {len(conferencias)} registros")
            self.dados_teste['conferencias'] = conferencias
        except Exception as e:
            self.erro(f"[ERRO] Erro ao carregar conferências: {str(e)}")
    
    # ========== TESTES DE MÉTODOS ==========
    def testar_metodos_geracao(self):
        """Testa todos os 8 métodos de geração."""
        self.secao("TESTE 3: MÉTODOS DE GERAÇÃO (M1-M8)")
        
        resultados = self.dados_teste.get('resultados', [])
        
        if not resultados:
            self.aviso("[N/A] Sem dados históricos para testar métodos com contexto")
            self.log("Testando métodos com dados vazios...")
        
        try:
            metodos_gerados = lib.gerar_todos_metodos(seed=42)
            
            for nome, dezenas in metodos_gerados.items():
                if self._validar_dezenas(dezenas):
                    soma = sum(dezenas)
                    pares = sum(1 for d in dezenas if d % 2 == 0)
                    self.log(f"[OK] {nome}: {sorted(dezenas)}")
                    self.log(f"    - Soma: {soma}, Pares: {pares}, Ímpares: {15-pares}")
                else:
                    self.erro(f"[ERRO] {nome}: dezenas inválidas")
                    
            self.dados_teste['metodos_gerados'] = metodos_gerados
            
        except Exception as e:
            self.erro(f"[ERRO] Erro ao gerar métodos: {str(e)}")
    
    def _validar_dezenas(self, dezenas):
        """Valida se um conjunto de dezenas é válido."""
        return (
            isinstance(dezenas, set) and 
            len(dezenas) == 15 and 
            all(1 <= d <= 25 for d in dezenas)
        )
    
    # ========== TESTES DE FREQUÊNCIA/ATRASO ==========
    def testar_frequencia_atraso(self):
        """Testa cálculo de frequência e atraso."""
        self.secao("TESTE 4: ANÁLISE DE FREQUÊNCIA E ATRASO")
        
        try:
            freq, atraso, total = lib.frequencia_e_atraso()
            
            self.log(f"[OK] Frequência calculada para {len(freq)} dezenas")
            self.log(f"[OK] Atraso calculado para {len(atraso)} dezenas")
            self.log(f"  Total de concursos analisados: {total}")
            
            if total > 0:
                freq_media = statistics.mean(freq.values())
                atraso_media = statistics.mean(atraso.values())
                
                self.log(f"  Frequência média por dezena: {freq_media:.2f}")
                self.log(f"  Atraso médio por dezena: {atraso_media:.2f}")
                
                dezena_mais_freq = max(freq, key=freq.get)
                dezena_mais_atrasada = max(atraso, key=atraso.get)
                
                self.log(f"  Dezena mais frequente: {dezena_mais_freq} ({freq[dezena_mais_freq]} vezes)")
                self.log(f"  Dezena mais atrasada: {dezena_mais_atrasada} (atraso: {atraso[dezena_mais_atrasada]})")
                
                self.dados_teste['freq'] = freq
                self.dados_teste['atraso'] = atraso
                self.dados_teste['total_concursos'] = total
            
        except Exception as e:
            self.erro(f"[ERRO] Erro ao calcular frequência/atraso: {str(e)}")
    
    # ========== TESTES DE CONFERÊNCIA ==========
    def testar_conferencia(self):
        """Testa funcionalidades de conferência."""
        self.secao("TESTE 5: SISTEMA DE CONFERÊNCIA")
        
        conferencias = self.dados_teste.get('conferencias', [])
        
        if conferencias:
            total = len(conferencias)
            self.log(f"[OK] Total de conferências: {total}")
            
            # Análise por método
            por_metodo = {}
            for conf in conferencias:
                metodo = conf.get('metodo', 'desconhecido')
                if metodo not in por_metodo:
                    por_metodo[metodo] = []
                por_metodo[metodo].append(conf.get('acertos', 0))
            
            self.log(f"[OK] Métodos conferidos: {len(por_metodo)}")
            
            for metodo, acertos_lista in sorted(por_metodo.items()):
                media = statistics.mean(acertos_lista)
                desvio = statistics.pstdev(acertos_lista) if len(acertos_lista) > 1 else 0.0
                min_ac = min(acertos_lista)
                max_ac = max(acertos_lista)
                
                self.log(f"  {metodo}:")
                self.log(f"      - {len(acertos_lista)} jogos | Média: {media:.2f} | σ: {desvio:.2f} | Min: {min_ac} | Max: {max_ac}")
            
            # Distribuição geral
            todas_acertos = [conf.get('acertos', 0) for conf in conferencias]
            dist = Counter(todas_acertos)
            
            self.log(f"\n  Distribuição geral de acertos:")
            for acertos in sorted(dist.keys()):
                qtd = dist[acertos]
                pct = 100 * qtd / total
                self.log(f"    {acertos} acertos: {qtd} ({pct:.1f}%)")
        else:
            self.aviso("[N/A] Nenhuma conferência registrada")
    
    # ========== TESTES DE ESTATÍSTICAS ==========
    def testar_estatisticas(self):
        """Testa cálculo de estatísticas dos métodos."""
        self.secao("TESTE 6: ESTATÍSTICAS DE DESEMPENHO")
        
        try:
            stats = lib.calcular_estatisticas_metodos()
            
            if stats:
                self.log(f"[OK] Estatísticas calculadas para {len(stats)} métodos")
                
                for item in stats:
                    metodo = item.get('metodo', '?')
                    n = item.get('total_jogos_conferidos', 0)
                    media = item.get('media_acertos', 0)
                    desvio = item.get('desvio_padrao_acertos', 0)
                    
                    if n > 0:
                        self.log(f"  {metodo}:")
                        self.log(f"      - {n} jogos | Média: {media:.3f} | σ: {desvio:.3f}")
                
                self.dados_teste['stats_metodos'] = stats
            else:
                self.aviso("[N/A] Sem estatísticas disponíveis (nenhuma conferência realizada)")
                
        except Exception as e:
            self.erro(f"[ERRO] Erro ao calcular estatísticas: {str(e)}")
    
    # ========== TESTES DE SIMULAÇÃO ==========
    def testar_simulacao_backtest(self):
        """Testa simulação de 5 mil testes por sorteio gerado."""
        self.secao("TESTE 7: SIMULACAO DE 5.000 TESTES POR SORTEIO")
        
        resultados = self.dados_teste.get('resultados', [])
        
        if len(resultados) < 10:
            self.aviso(f"[N/A] Apenas {len(resultados)} concursos disponíveis (mínimo recomendado: 10)")
            return
        
        try:
            # Usa últimos 2 concursos para testar com 5k testes cada
            num_concursos_backtest = min(2, len(resultados))
            concursos_backtest = resultados[-num_concursos_backtest:]
            num_testes_por_sorteio = 5000
            
            resultados_simulacao = {metodo: [] for metodo in lib.METODOS}
            sorteios_vencedores = {metodo: [] for metodo in lib.METODOS}  # Acertos > 11
            
            for concurso_idx, concurso in enumerate(concursos_backtest):
                ate_concurso = resultados[len(resultados) - num_concursos_backtest + concurso_idx - 1]['concurso'] if concurso_idx > 0 else None
                
                self.log(f"  Testando concurso {concurso['concurso']} com {num_testes_por_sorteio} testes...")
                
                try:
                    metodos = lib.gerar_todos_metodos(seed=concurso['concurso'], ate_concurso=ate_concurso)
                    
                    for metodo, dezenas_base in metodos.items():
                        acertos_metodo = []
                        vencedores_count = 0
                        
                        # Executa 20k variações do método
                        for teste_idx in range(num_testes_por_sorteio):
                            # Gera variação do método com seed diferente
                            rng = random.Random(f"{concurso['concurso']}_{metodo}_{teste_idx}")
                            
                            # Regenera com novo RNG para gerar variações
                            if metodo == "M1_aleatorio_puro":
                                dezenas = lib.metodo_aleatorio_puro(rng)
                            elif metodo == "M2_mais_frequentes":
                                dezenas = lib.metodo_mais_frequentes(rng, self.dados_teste.get('freq', {}))
                            elif metodo == "M3_mais_atrasadas":
                                dezenas = lib.metodo_mais_atrasadas(rng, self.dados_teste.get('atraso', {}))
                            elif metodo == "M4_par_impar_balanceado":
                                dezenas = lib.metodo_par_impar_balanceado(rng)
                            elif metodo == "M5_soma_faixa_comum":
                                dezenas = lib.metodo_soma_faixa_comum(rng)
                            elif metodo == "M6_filtros_combinados":
                                resultados_sets = lib._resultados_como_sets(ate_concurso)
                                dezenas = lib.metodo_filtros_combinados(rng, resultados_sets)
                            elif metodo == "M7_cobertura_pares":
                                resultados_sets = lib._resultados_como_sets(ate_concurso)
                                dezenas = lib.metodo_cobertura_pares(rng, resultados_sets)
                            else:  # M8
                                resultados_sets = lib._resultados_como_sets(ate_concurso)
                                dezenas = lib.metodo_repeticao_controlada(rng, resultados_sets)
                            
                            acertos = len(dezenas & concurso['dezenas'])
                            acertos_metodo.append(acertos)
                            
                            # Registra sorteios com > 11 acertos
                            if acertos > 11:
                                vencedores_count += 1
                                sorteios_vencedores[metodo].append({
                                    'concurso': concurso['concurso'],
                                    'acertos': acertos,
                                    'dezenas': sorted(dezenas),
                                    'soma': sum(dezenas),
                                    'pares': sum(1 for d in dezenas if d % 2 == 0)
                                })
                        
                        resultados_simulacao[metodo].extend(acertos_metodo)
                        taxa_vencedores = (vencedores_count / num_testes_por_sorteio) * 100
                        self.log(f"    {metodo}: {vencedores_count} vencedores ({taxa_vencedores:.2f}%)")
                except Exception as e:
                    self.aviso(f"    [N/A] Erro ao testar {metodo}: {str(e)}")
            
            self.log(f"\n  [OK] Simulação completa: {len(concursos_backtest)} concursos × {num_testes_por_sorteio} testes")
            self.log(f"  Total de testes executados: {len(concursos_backtest) * num_testes_por_sorteio:,}")
            
            # Resumo geral
            for metodo, acertos_lista in sorted(resultados_simulacao.items()):
                if acertos_lista:
                    media = statistics.mean(acertos_lista)
                    desvio = statistics.pstdev(acertos_lista) if len(acertos_lista) > 1 else 0.0
                    min_ac = min(acertos_lista)
                    max_ac = max(acertos_lista)
                    percentual_11_ou_mais = (sum(1 for a in acertos_lista if a >= 11) / len(acertos_lista)) * 100
                    
                    self.log(f"\n  {metodo}:")
                    self.log(f"      - Média: {media:.3f} | σ: {desvio:.3f} | Min: {min_ac} | Max: {max_ac}")
                    self.log(f"      - Acertos ≥ 11: {percentual_11_ou_mais:.2f}%")
            
            self.dados_teste['simulacao'] = resultados_simulacao
            self.dados_teste['sorteios_vencedores'] = sorteios_vencedores
            
        except Exception as e:
            self.erro(f"[ERRO] Erro na simulação: {str(e)}")
    
    # ========== TESTE DE SERIES TEMPORAIS ==========
    def testar_series_temporais(self):
        """Testa análise de series temporais."""
        self.secao("TESTE 8: ANÁLISE DE SÉRIES TEMPORAIS")
        
        try:
            series = lib.calcular_series_metodos(janela=50)
            
            self.log(f"[OK] Séries temporais calculadas (janela: {series['janela']} concursos)")
            self.log(f"  Concursos analisados: {len(series['concursos'])}")
            self.log(f"  Esperança teórica: {series['esperanca_teorica']}")
            
            if series['series']:
                self.log(f"\n  Desempenho por método (últimos {series['janela']} concursos):")
                
                for item in series['series']:
                    metodo = item.get('metodo', '?')
                    media = item.get('media_periodo', 0)
                    desvio = item.get('desvio_padrao_periodo', 0)
                    rms = item.get('desvio_vs_esperanca_rms', 0)
                    n = item.get('total_concursos_periodo', 0)
                    
                    self.log(f"  {metodo}:")
                    self.log(f"      - {n} concursos | Média: {media:.3f} | σ: {desvio:.3f} | RMS (vs esperança): {rms:.3f}")
                
                if series['metodo_mais_estavel']:
                    self.log(f"\n  [OK] Método mais estável (últimos {series['janela']} concursos): {series['metodo_mais_estavel']}")
            
            self.dados_teste['series'] = series
            
        except Exception as e:
            self.erro(f"[ERRO] Erro ao calcular séries: {str(e)}")
    
    # ========== ANÁLISE DE TESE ==========
    def analisar_tese_sorteios_vencedores(self):
        """Analisa padrões nos sorteios com acertos > 11."""
        self.secao("TESTE 9: TESE - ANÁLISE DE SORTEIOS VENCEDORES (>11 acertos)")
        
        sorteios_vencedores = self.dados_teste.get('sorteios_vencedores', {})
        
        if not sorteios_vencedores or all(len(v) == 0 for v in sorteios_vencedores.values()):
            self.aviso("[N/A] Nenhum sorteio com acertos > 11 encontrado")
            return
        
        total_vencedores = sum(len(v) for v in sorteios_vencedores.values())
        self.log(f"Total de sorteios vencedores (>11 acertos): {total_vencedores}")
        
        # Análise por método
        for metodo, vencedores in sorted(sorteios_vencedores.items()):
            if vencedores:
                self.log(f"\n  {metodo}: {len(vencedores)} sorteios vencedores")
                
                acertos_list = [v['acertos'] for v in vencedores]
                somas_list = [v['soma'] for v in vencedores]
                pares_list = [v['pares'] for v in vencedores]
                
                # Estatísticas dos vencedores
                media_acertos = statistics.mean(acertos_list)
                media_soma = statistics.mean(somas_list)
                media_pares = statistics.mean(pares_list)
                
                self.log(f"      - Média de acertos: {media_acertos:.2f}")
                self.log(f"      - Soma média: {media_soma:.1f} (range: {min(somas_list)}-{max(somas_list)})")
                self.log(f"      - Pares médios: {media_pares:.1f}")
                
                # Distribuição de acertos
                dist_acertos = Counter(acertos_list)
                self.log(f"      - Distribuição: {dict(sorted(dist_acertos.items()))}")
        
        # Tese consolidada
        self.log(f"\n{'='*60}")
        self.log(f"  TESE: CARACTERÍSTICAS DOS SORTEIOS VENCEDORES")
        self.log(f"{'='*60}")
        
        # Coleta todas as dezenas que aparecem nos vencedores
        todas_dezenas_vencedoras = {}
        for metodo, vencedores in sorteios_vencedores.items():
            if vencedores:
                for v in vencedores:
                    for dezena in v['dezenas']:
                        todas_dezenas_vencedoras[dezena] = todas_dezenas_vencedoras.get(dezena, 0) + 1
        
        if todas_dezenas_vencedoras:
            dezenas_top = sorted(todas_dezenas_vencedoras.items(), key=lambda x: x[1], reverse=True)[:10]
            self.log(f"\n  Dezenas mais frequentes nos vencedores:")
            for dezena, freq in dezenas_top:
                self.log(f"    {dezena}: {freq} vezes")
        
        # Somas mais comuns nos vencedores
        todas_somas = []
        for metodo, vencedores in sorteios_vencedores.items():
            todas_somas.extend([v['soma'] for v in vencedores])
        
        if todas_somas:
            soma_media = statistics.mean(todas_somas)
            soma_desvio = statistics.pstdev(todas_somas) if len(todas_somas) > 1 else 0.0
            soma_moda_counter = Counter(todas_somas)
            soma_moda = soma_moda_counter.most_common(1)[0][0]
            
            self.log(f"\n  Análise de somas:")
            self.log(f"      - Média: {soma_media:.1f}")
            self.log(f"      - Desvio padrão: {soma_desvio:.1f}")
            self.log(f"      - Moda (mais frequente): {soma_moda}")
            self.log(f"      - Range: {min(todas_somas)} a {max(todas_somas)}")
        
        # Paridade
        todos_pares = []
        for metodo, vencedores in sorteios_vencedores.items():
            todos_pares.extend([v['pares'] for v in vencedores])
        
        if todos_pares:
            pares_media = statistics.mean(todos_pares)
            pares_moda_counter = Counter(todos_pares)
            pares_moda = pares_moda_counter.most_common(1)[0][0]
            
            self.log(f"\n  Análise de paridade:")
            self.log(f"      - Média de pares: {pares_media:.1f}")
            self.log(f"      - Pares mais frequentes: {pares_moda}")
        
        # Conclusão geral
        self.log(f"\n  CONCLUSÃO:")
        self.log(f"      - Taxa de vencimento (>11): {(total_vencedores / sum(len(v) for v in self.dados_teste.get('simulacao', {}).values()) * 100) if self.dados_teste.get('simulacao') else 0:.3f}%")
        self.log(f"      - Padrão principal: Soma ~{int(soma_media)} com ~{int(pares_media)} pares")
        self.log(f"      - Dezenas críticas: {', '.join(str(d[0]) for d in dezenas_top[:5])}")
    
    # ========== TESTE DE EXPORTAÇÃO ==========
    def testar_exportacao(self):
        """Testa funções de exportação."""
        self.secao("TESTE 9: FUNÇÕES DE EXPORTAÇÃO")
        
        try:
            # Teste de exportação JSON de estatísticas
            arquivo_json = lib.exportar_estatisticas_para_json()
            if os.path.exists(arquivo_json):
                tamanho = os.path.getsize(arquivo_json)
                self.log(f"[OK] Estatísticas exportadas para JSON: {tamanho} bytes")
            else:
                self.aviso(f"[N/A] Arquivo JSON não foi criado")
                
        except Exception as e:
            self.erro(f"[ERRO] Erro na exportação JSON: {str(e)}")
        
        try:
            # Teste de salvamento de frequência
            lib.salvar_frequencia_dezenas()
            if os.path.exists(lib.FREQUENCIA_CSV):
                tamanho = os.path.getsize(lib.FREQUENCIA_CSV)
                self.log(f"[OK] Frequência salva em CSV: {tamanho} bytes")
            else:
                self.aviso(f"[N/A] Arquivo de frequência não foi criado")
                
        except Exception as e:
            self.erro(f"[ERRO] Erro ao salvar frequência: {str(e)}")
        
        try:
            # Teste de salvamento de estatísticas
            lib.salvar_estatisticas_metodos()
            if os.path.exists(lib.ESTATISTICAS_CSV):
                tamanho = os.path.getsize(lib.ESTATISTICAS_CSV)
                self.log(f"[OK] Estatísticas salvas em CSV: {tamanho} bytes")
            else:
                self.aviso(f"[N/A] Arquivo de estatísticas não foi criado")
                
        except Exception as e:
            self.erro(f"[ERRO] Erro ao salvar estatísticas: {str(e)}")
    
    # ========== RELATÓRIO FINAL ==========
    def gerar_relatorio_diagnostico(self):
        """Gera relatório final de diagnóstico."""
        self.secao("RELATÓRIO FINAL DE DIAGNÓSTICO")
        
        total_testes = 10
        erros_count = len(self.erros)
        avisos_count = len(self.avisos)
        
        self.log(f"Total de testes executados: {total_testes}")
        self.log(f"Erros encontrados: {erros_count}")
        self.log(f"Avisos: {avisos_count}")
        
        if erros_count == 0:
            self.log(f"\n[OK] DIAGNÓSTICO: SISTEMA OK (Apenas {avisos_count} aviso(s) informativo(s))")
        elif erros_count <= 2:
            self.log(f"\n⚠ DIAGNÓSTICO: SISTEMA COM PROBLEMAS MENORES ({erros_count} erro(s))")
        else:
            self.log(f"\n[ERRO] DIAGNÓSTICO: SISTEMA COM PROBLEMAS GRAVES ({erros_count} erro(s))")
        
        # Resumo de dados
        self.log(f"\n{'='*60}")
        self.log(f"  RESUMO DE DADOS")
        self.log(f"{'='*60}")
        
        resultados = self.dados_teste.get('resultados', [])
        if resultados:
            self.log(f"Concursos registrados: {len(resultados)}")
            self.log(f"Primeiro: {resultados[0]['concurso']} | Último: {resultados[-1]['concurso']}")
        
        jogos = self.dados_teste.get('jogos', [])
        if jogos:
            self.log(f"Jogos de estudo gerados: {len(jogos)}")
            
            # Contagem por método
            metodos_count = Counter(j.get('metodo', '?') for j in jogos)
            for metodo, count in sorted(metodos_count.items()):
                self.log(f"    - {metodo}: {count} jogos")
        
        conferencias = self.dados_teste.get('conferencias', [])
        if conferencias:
            self.log(f"Conferências realizadas: {len(conferencias)}")
        
        # Recomendações
        self.log(f"\n{'='*60}")
        self.log(f"  RECOMENDAÇÕES")
        self.log(f"{'='*60}")
        
        if len(resultados) < 100:
            self.log(f"⚠ Baixo volume de histórico ({len(resultados)} concursos)")
            self.log(f"  Recomendação: Acumule mais dados para análises estatísticas robustas")
        
        if len(conferencias) == 0:
            self.log(f"ℹ Nenhuma conferência registrada")
            self.log(f"  Recomendação: Execute conferências para validar os métodos")
        elif len(conferencias) < 100:
            self.log(f"⚠ Baixo volume de conferências ({len(conferencias)})")
            self.log(f"  Recomendação: Continue registrando e conferindo jogos")
        else:
            self.log(f"[OK] Volume adequado de conferências para análise")
        
        stats = self.dados_teste.get('stats_metodos', [])
        if stats:
            metodos_com_dados = [s for s in stats if s.get('total_jogos_conferidos', 0) > 0]
            if len(metodos_com_dados) == len(lib.METODOS):
                self.log(f"[OK] Todos os 8 métodos têm dados de conferência")
            else:
                self.log(f"⚠ Apenas {len(metodos_com_dados)}/{len(lib.METODOS)} métodos têm conferências")
        
        self.log(f"\n{'='*60}")
        self.log(f"Diagnóstico concluído em {self.timestamp}")
        self.log(f"{'='*60}\n")
    
    def executar_testes_completos(self):
        """Executa todos os testes."""
        print(f"\n{'='*60}")
        print(f"  TESTE DIAGNÓSTICO COMPLETO - SISTEMA LOTOFÁCIL")
        print(f"  {self.timestamp}")
        print(f"{'='*60}\n")
        
        self.testar_integridade_arquivos()
        self.testar_carregamento_dados()
        self.testar_metodos_geracao()
        self.testar_frequencia_atraso()
        self.testar_conferencia()
        self.testar_estatisticas()
        self.testar_simulacao_backtest()
        self.analisar_tese_sorteios_vencedores()
        self.testar_series_temporais()
        self.testar_exportacao()
        self.gerar_relatorio_diagnostico()
        
        return self
    
    def salvar_relatorio(self, caminho=None):
        """Salva o relatório em arquivo markdown."""
        if caminho is None:
            caminho = os.path.join(lib.BASE_DIR, f"diagnostico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        conteudo = "# DIAGNÓSTICO COMPLETO - SISTEMA LOTOFÁCIL\n\n"
        conteudo += f"**Data/Hora:** {self.timestamp}\n\n"
        conteudo += "## Resultado Geral\n\n"
        
        erros_count = len(self.erros)
        avisos_count = len(self.avisos)
        
        if erros_count == 0:
            conteudo += f"[OK] **SISTEMA OK** ({avisos_count} aviso(s))\n\n"
        elif erros_count <= 2:
            conteudo += f"⚠ **PROBLEMAS MENORES** ({erros_count} erro(s))\n\n"
        else:
            conteudo += f"[ERRO] **PROBLEMAS GRAVES** ({erros_count} erro(s))\n\n"
        
        conteudo += "## Relatório Detalhado\n\n"
        conteudo += "```\n"
        conteudo += "\n".join(self.relatorio)
        conteudo += "\n```\n\n"
        
        if self.erros:
            conteudo += "## Erros Detectados\n\n"
            for erro in self.erros:
                conteudo += f"- {erro}\n"
            conteudo += "\n"
        
        if self.avisos:
            conteudo += "## Avisos\n\n"
            for aviso in self.avisos:
                conteudo += f"- {aviso}\n"
            conteudo += "\n"
        
        conteudo += "## Dados Resumidos\n\n"
        
        resultados = self.dados_teste.get('resultados', [])
        if resultados:
            conteudo += f"- **Concursos registrados:** {len(resultados)}\n"
        
        jogos = self.dados_teste.get('jogos', [])
        if jogos:
            conteudo += f"- **Jogos de estudo:** {len(jogos)}\n"
        
        conferencias = self.dados_teste.get('conferencias', [])
        if conferencias:
            conteudo += f"- **Conferências realizadas:** {len(conferencias)}\n"
        
        conteudo += "\n"
        
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        
        print(f"\n[OK] Relatório salvo em: {caminho}\n")
        return caminho


if __name__ == "__main__":
    testador = TestadorDiagnostico()
    testador.executar_testes_completos()
    arquivo_relatorio = testador.salvar_relatorio()
    
    # Imprime resumo final
    print(f"\n{'='*60}")
    print(f"TESTE CONCLUÍDO")
    print(f"Erros: {len(testador.erros)} | Avisos: {len(testador.avisos)}")
    print(f"Relatório: {arquivo_relatorio}")
    print(f"{'='*60}\n")
