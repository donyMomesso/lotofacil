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
from datetime import datetime
from collections import Counter

# Adiciona path para importar lotofacil_lib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import lotofacil_lib as lib

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
                    self.log(f"✓ {os.path.basename(arq)}: {linhas} linhas")
                except Exception as e:
                    self.erro(f"✗ {os.path.basename(arq)}: {str(e)}")
            else:
                self.aviso(f"⊘ {os.path.basename(arq)}: não encontrado")
    
    # ========== TESTES DE DADOS ==========
    def testar_carregamento_dados(self):
        """Testa carregamento de todos os dados."""
        self.secao("TESTE 2: CARREGAMENTO DE DADOS")
        
        try:
            resultados = lib.carregar_resultados()
            self.log(f"✓ Resultados carregados: {len(resultados)} concursos")
            self.dados_teste['resultados'] = resultados
            
            if len(resultados) == 0:
                self.aviso("⊘ Nenhum resultado registrado no sistema")
            
        except Exception as e:
            self.erro(f"✗ Erro ao carregar resultados: {str(e)}")
            
        try:
            jogos = lib.carregar_jogos()
            self.log(f"✓ Jogos carregados: {len(jogos)} jogos")
            self.dados_teste['jogos'] = jogos
        except Exception as e:
            self.erro(f"✗ Erro ao carregar jogos: {str(e)}")
            
        try:
            conferencias = lib.carregar_conferencias()
            self.log(f"✓ Conferências carregadas: {len(conferencias)} registros")
            self.dados_teste['conferencias'] = conferencias
        except Exception as e:
            self.erro(f"✗ Erro ao carregar conferências: {str(e)}")
    
    # ========== TESTES DE MÉTODOS ==========
    def testar_metodos_geracao(self):
        """Testa todos os 8 métodos de geração."""
        self.secao("TESTE 3: MÉTODOS DE GERAÇÃO (M1-M8)")
        
        resultados = self.dados_teste.get('resultados', [])
        
        if not resultados:
            self.aviso("⊘ Sem dados históricos para testar métodos com contexto")
            self.log("Testando métodos com dados vazios...")
        
        try:
            metodos_gerados = lib.gerar_todos_metodos(seed=42)
            
            for nome, dezenas in metodos_gerados.items():
                if self._validar_dezenas(dezenas):
                    soma = sum(dezenas)
                    pares = sum(1 for d in dezenas if d % 2 == 0)
                    self.log(f"✓ {nome}: {sorted(dezenas)}")
                    self.log(f"  └─ Soma: {soma}, Pares: {pares}, Ímpares: {15-pares}")
                else:
                    self.erro(f"✗ {nome}: dezenas inválidas")
                    
            self.dados_teste['metodos_gerados'] = metodos_gerados
            
        except Exception as e:
            self.erro(f"✗ Erro ao gerar métodos: {str(e)}")
    
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
            
            self.log(f"✓ Frequência calculada para {len(freq)} dezenas")
            self.log(f"✓ Atraso calculado para {len(atraso)} dezenas")
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
            self.erro(f"✗ Erro ao calcular frequência/atraso: {str(e)}")
    
    # ========== TESTES DE CONFERÊNCIA ==========
    def testar_conferencia(self):
        """Testa funcionalidades de conferência."""
        self.secao("TESTE 5: SISTEMA DE CONFERÊNCIA")
        
        conferencias = self.dados_teste.get('conferencias', [])
        
        if conferencias:
            total = len(conferencias)
            self.log(f"✓ Total de conferências: {total}")
            
            # Análise por método
            por_metodo = {}
            for conf in conferencias:
                metodo = conf.get('metodo', 'desconhecido')
                if metodo not in por_metodo:
                    por_metodo[metodo] = []
                por_metodo[metodo].append(conf.get('acertos', 0))
            
            self.log(f"✓ Métodos conferidos: {len(por_metodo)}")
            
            for metodo, acertos_lista in sorted(por_metodo.items()):
                media = statistics.mean(acertos_lista)
                desvio = statistics.pstdev(acertos_lista) if len(acertos_lista) > 1 else 0.0
                min_ac = min(acertos_lista)
                max_ac = max(acertos_lista)
                
                self.log(f"  {metodo}:")
                self.log(f"    └─ {len(acertos_lista)} jogos | Média: {media:.2f} | σ: {desvio:.2f} | Min: {min_ac} | Max: {max_ac}")
            
            # Distribuição geral
            todas_acertos = [conf.get('acertos', 0) for conf in conferencias]
            dist = Counter(todas_acertos)
            
            self.log(f"\n  Distribuição geral de acertos:")
            for acertos in sorted(dist.keys()):
                qtd = dist[acertos]
                pct = 100 * qtd / total
                self.log(f"    {acertos} acertos: {qtd} ({pct:.1f}%)")
        else:
            self.aviso("⊘ Nenhuma conferência registrada")
    
    # ========== TESTES DE ESTATÍSTICAS ==========
    def testar_estatisticas(self):
        """Testa cálculo de estatísticas dos métodos."""
        self.secao("TESTE 6: ESTATÍSTICAS DE DESEMPENHO")
        
        try:
            stats = lib.calcular_estatisticas_metodos()
            
            if stats:
                self.log(f"✓ Estatísticas calculadas para {len(stats)} métodos")
                
                for item in stats:
                    metodo = item.get('metodo', '?')
                    n = item.get('total_jogos_conferidos', 0)
                    media = item.get('media_acertos', 0)
                    desvio = item.get('desvio_padrao_acertos', 0)
                    
                    if n > 0:
                        self.log(f"  {metodo}:")
                        self.log(f"    └─ {n} jogos | Média: {media:.3f} | σ: {desvio:.3f}")
                
                self.dados_teste['stats_metodos'] = stats
            else:
                self.aviso("⊘ Sem estatísticas disponíveis (nenhuma conferência realizada)")
                
        except Exception as e:
            self.erro(f"✗ Erro ao calcular estatísticas: {str(e)}")
    
    # ========== TESTES DE SIMULAÇÃO ==========
    def testar_simulacao_backtest(self):
        """Testa simulação de backtest."""
        self.secao("TESTE 7: SIMULAÇÃO DE BACKTEST")
        
        resultados = self.dados_teste.get('resultados', [])
        
        if len(resultados) < 10:
            self.aviso(f"⊘ Apenas {len(resultados)} concursos disponíveis (mínimo recomendado: 10)")
            return
        
        try:
            # Simula 5 jogos por método nos últimos 20 concursos
            num_concursos_backtest = min(20, len(resultados))
            concursos_backtest = resultados[-num_concursos_backtest:]
            
            resultados_simulacao = {metodo: [] for metodo in lib.METODOS}
            
            for concurso_idx, concurso in enumerate(concursos_backtest):
                # Gera métodos com dados até o concurso anterior
                ate_concurso = resultados[len(resultados) - num_concursos_backtest + concurso_idx - 1]['concurso'] if concurso_idx > 0 else None
                
                try:
                    metodos = lib.gerar_todos_metodos(seed=concurso['concurso'], ate_concurso=ate_concurso)
                    
                    for metodo, dezenas in metodos.items():
                        acertos = len(dezenas & concurso['dezenas'])
                        resultados_simulacao[metodo].append(acertos)
                except:
                    pass
            
            self.log(f"✓ Simulação de backtest em {len(concursos_backtest)} concursos")
            
            for metodo, acertos_lista in sorted(resultados_simulacao.items()):
                if acertos_lista:
                    media = statistics.mean(acertos_lista)
                    desvio = statistics.pstdev(acertos_lista) if len(acertos_lista) > 1 else 0.0
                    min_ac = min(acertos_lista)
                    max_ac = max(acertos_lista)
                    
                    self.log(f"  {metodo}:")
                    self.log(f"    └─ Média: {media:.2f} | σ: {desvio:.2f} | Min: {min_ac} | Max: {max_ac}")
            
            self.dados_teste['simulacao'] = resultados_simulacao
            
        except Exception as e:
            self.erro(f"✗ Erro na simulação: {str(e)}")
    
    # ========== TESTE DE SERIES TEMPORAIS ==========
    def testar_series_temporais(self):
        """Testa análise de series temporais."""
        self.secao("TESTE 8: ANÁLISE DE SÉRIES TEMPORAIS")
        
        try:
            series = lib.calcular_series_metodos(janela=50)
            
            self.log(f"✓ Séries temporais calculadas (janela: {series['janela']} concursos)")
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
                    self.log(f"    └─ {n} concursos | Média: {media:.3f} | σ: {desvio:.3f} | RMS (vs esperança): {rms:.3f}")
                
                if series['metodo_mais_estavel']:
                    self.log(f"\n  ✓ Método mais estável (últimos {series['janela']} concursos): {series['metodo_mais_estavel']}")
            
            self.dados_teste['series'] = series
            
        except Exception as e:
            self.erro(f"✗ Erro ao calcular séries: {str(e)}")
    
    # ========== TESTE DE EXPORTAÇÃO ==========
    def testar_exportacao(self):
        """Testa funções de exportação."""
        self.secao("TESTE 9: FUNÇÕES DE EXPORTAÇÃO")
        
        try:
            # Teste de exportação JSON de estatísticas
            arquivo_json = lib.exportar_estatisticas_para_json()
            if os.path.exists(arquivo_json):
                tamanho = os.path.getsize(arquivo_json)
                self.log(f"✓ Estatísticas exportadas para JSON: {tamanho} bytes")
            else:
                self.aviso(f"⊘ Arquivo JSON não foi criado")
                
        except Exception as e:
            self.erro(f"✗ Erro na exportação JSON: {str(e)}")
        
        try:
            # Teste de salvamento de frequência
            lib.salvar_frequencia_dezenas()
            if os.path.exists(lib.FREQUENCIA_CSV):
                tamanho = os.path.getsize(lib.FREQUENCIA_CSV)
                self.log(f"✓ Frequência salva em CSV: {tamanho} bytes")
            else:
                self.aviso(f"⊘ Arquivo de frequência não foi criado")
                
        except Exception as e:
            self.erro(f"✗ Erro ao salvar frequência: {str(e)}")
        
        try:
            # Teste de salvamento de estatísticas
            lib.salvar_estatisticas_metodos()
            if os.path.exists(lib.ESTATISTICAS_CSV):
                tamanho = os.path.getsize(lib.ESTATISTICAS_CSV)
                self.log(f"✓ Estatísticas salvas em CSV: {tamanho} bytes")
            else:
                self.aviso(f"⊘ Arquivo de estatísticas não foi criado")
                
        except Exception as e:
            self.erro(f"✗ Erro ao salvar estatísticas: {str(e)}")
    
    # ========== RELATÓRIO FINAL ==========
    def gerar_relatorio_diagnostico(self):
        """Gera relatório final de diagnóstico."""
        self.secao("RELATÓRIO FINAL DE DIAGNÓSTICO")
        
        total_testes = 9
        erros_count = len(self.erros)
        avisos_count = len(self.avisos)
        
        self.log(f"Total de testes executados: {total_testes}")
        self.log(f"Erros encontrados: {erros_count}")
        self.log(f"Avisos: {avisos_count}")
        
        if erros_count == 0:
            self.log(f"\n✓ DIAGNÓSTICO: SISTEMA OK (Apenas {avisos_count} aviso(s) informativo(s))")
        elif erros_count <= 2:
            self.log(f"\n⚠ DIAGNÓSTICO: SISTEMA COM PROBLEMAS MENORES ({erros_count} erro(s))")
        else:
            self.log(f"\n✗ DIAGNÓSTICO: SISTEMA COM PROBLEMAS GRAVES ({erros_count} erro(s))")
        
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
                self.log(f"  └─ {metodo}: {count} jogos")
        
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
            self.log(f"✓ Volume adequado de conferências para análise")
        
        stats = self.dados_teste.get('stats_metodos', [])
        if stats:
            metodos_com_dados = [s for s in stats if s.get('total_jogos_conferidos', 0) > 0]
            if len(metodos_com_dados) == len(lib.METODOS):
                self.log(f"✓ Todos os 8 métodos têm dados de conferência")
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
            conteudo += f"✓ **SISTEMA OK** ({avisos_count} aviso(s))\n\n"
        elif erros_count <= 2:
            conteudo += f"⚠ **PROBLEMAS MENORES** ({erros_count} erro(s))\n\n"
        else:
            conteudo += f"✗ **PROBLEMAS GRAVES** ({erros_count} erro(s))\n\n"
        
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
        
        print(f"\n✓ Relatório salvo em: {caminho}\n")
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
