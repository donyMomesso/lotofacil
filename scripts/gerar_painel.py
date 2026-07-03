"""
Gera painel.html: um painel visual autônomo (abre em qualquer navegador,
sem precisar de servidor) com o estado atual do laboratório.

É uma fotografia estática, regenerada a cada ciclo diário — não busca
nada da internet sozinho.

Uso:
    python3 gerar_painel.py
"""
import csv
import json
import os
from datetime import datetime, timezone, timedelta

import lotofacil_lib as lib

PAINEL_PATH = os.path.join(lib.BASE_DIR, "painel.html")
BRASILIA = timezone(timedelta(hours=-3))

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Laboratório Estatístico Lotofácil — Painel</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
<style>
  :root {
    --bg: #0f1420; --card: #171e2e; --card2: #1e2740; --text: #e7ebf3; --muted: #9aa6bd;
    --accent: #5b8def; --good: #3fbf7f; --warn: #e0a838; --line: #2a3350;
  }
  * { box-sizing: border-box; }
  body { margin:0; font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
         background: var(--bg); color: var(--text); }
  header { padding: 24px 32px 8px; }
  h1 { margin: 0 0 4px; font-size: 22px; }
  .sub { color: var(--muted); font-size: 13px; }
  .disclaimer { margin: 16px 32px; padding: 14px 18px; border-radius: 10px;
                background: linear-gradient(90deg, rgba(224,168,56,.15), rgba(224,168,56,.05));
                border: 1px solid rgba(224,168,56,.35); font-size: 13.5px; line-height: 1.5; }
  .disclaimer b { color: var(--warn); }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 14px; margin: 8px 32px 0; }
  .stat { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px; }
  .stat .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }
  .stat .value { font-size: 26px; font-weight: 700; margin-top: 6px; }
  .stat .hint { color: var(--muted); font-size: 12px; margin-top: 4px; }
  section { margin: 26px 32px; }
  section h2 { font-size: 15px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em;
               margin: 0 0 12px; font-weight: 600; }
  .panels { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
  @media (max-width: 900px) { .panels { grid-template-columns: 1fr; } }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid var(--line); }
  th { color: var(--muted); font-weight: 600; font-size: 11.5px; text-transform: uppercase; }
  tr:last-child td { border-bottom: none; }
  .pill { display:inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11.5px; font-weight:600; }
  .pill.ok { background: rgba(63,191,127,.15); color: var(--good); }
  .pill.mid { background: rgba(91,141,239,.15); color: var(--accent); }
  footer { padding: 24px 32px 40px; color: var(--muted); font-size: 12px; }
  canvas { max-height: 320px; }
</style>
</head>
<body>
<header>
  <h1>Laboratório Estatístico Lotofácil</h1>
  <div class="sub">Painel gerado em __ATUALIZADO_EM__ (horário de Brasília) &middot; concurso mais recente: __ULTIMO_CONCURSO__</div>
</header>

<div class="disclaimer">
  <b>Isto é um estudo de matemática e estatística.</b> Nenhum jogo aqui é recomendação de aposta.
  A Lotofácil é um sorteio aleatório — nada neste painel indica que um método está "mais perto" de
  acertar 14 ou 15 dezenas. Todos os métodos são comparados contra o valor teórico esperado
  (__ESPERANCA__ acertos por jogo de 15 dezenas).
</div>

<div class="grid">
  <div class="stat"><div class="label">Concursos no histórico</div><div class="value">__TOTAL_CONCURSOS__</div></div>
  <div class="stat"><div class="label">Próximo concurso (jogos de estudo)</div><div class="value">__PROXIMO_CONCURSO__</div></div>
  <div class="stat"><div class="label">Esperança teórica de acertos</div><div class="value">__ESPERANCA__</div><div class="hint">distribuição hipergeométrica</div></div>
  <div class="stat"><div class="label">Jogos de estudo conferidos</div><div class="value">__TOTAL_CONFERIDOS__</div></div>
</div>

<section>
  <h2>Frequência e atraso das dezenas</h2>
  <div class="panels">
    <div class="card"><canvas id="freqChart"></canvas></div>
    <div class="card"><canvas id="atrasoChart"></canvas></div>
  </div>
</section>

<section>
  <h2>Desempenho comparado dos métodos</h2>
  <div class="panels">
    <div class="card"><canvas id="metodosChart"></canvas></div>
    <div class="card">
      <table>
        <thead><tr><th>Método</th><th>Jogos</th><th>Média</th><th>Desvio</th><th>11+</th><th>13+</th></tr></thead>
        <tbody>__TABELA_METODOS__</tbody>
      </table>
    </div>
  </div>
</section>

<section>
  <h2>Simulação retroativa (backtest em todo o histórico real)</h2>
  <div class="panels">
    <div class="card"><canvas id="backtestChart"></canvas></div>
    <div class="card">
      <table>
        <thead><tr><th>Método</th><th>Concursos</th><th>Média</th><th>Dif. vs. esperança</th><th>13+</th></tr></thead>
        <tbody>__TABELA_BACKTEST__</tbody>
      </table>
    </div>
  </div>
</section>

<section>
  <h2>Jogos de estudo do próximo concurso</h2>
  <div class="card">
    <table>
      <thead><tr><th>Método</th><th>Dezenas</th><th>Soma</th><th>Pares/Ímpares</th></tr></thead>
      <tbody>__TABELA_JOGOS__</tbody>
    </table>
  </div>
</section>

<section>
  <h2>Últimas conferências</h2>
  <div class="card">
    <table>
      <thead><tr><th>Concurso</th><th>Método</th><th>Acertos</th></tr></thead>
      <tbody>__TABELA_CONFERENCIAS__</tbody>
    </table>
  </div>
</section>

<footer>
  Gerado automaticamente por scripts/gerar_painel.py &middot; ver README.md e diario_estatistico.md para o
  raciocínio completo por trás de cada atualização.
</footer>

<script>
const dados = __DADOS_JSON__;

new Chart(document.getElementById('freqChart'), {
  type: 'bar',
  data: {
    labels: dados.dezenas.map(d => d.toString().padStart(2,'0')),
    datasets: [{ label: 'Frequência (%)', data: dados.freq_pct, backgroundColor: '#5b8def' }]
  },
  options: { plugins: { legend: { display:false }, title: { display:true, text:'Frequência relativa de cada dezena (%)', color:'#e7ebf3' } },
    scales: { x: { ticks: { color:'#9aa6bd' } }, y: { ticks: { color:'#9aa6bd' } } } }
});

new Chart(document.getElementById('atrasoChart'), {
  type: 'bar',
  data: {
    labels: dados.dezenas.map(d => d.toString().padStart(2,'0')),
    datasets: [{ label: 'Atraso (concursos)', data: dados.atraso, backgroundColor: '#e0a838' }]
  },
  options: { plugins: { legend: { display:false }, title: { display:true, text:'Concursos sem sair (atraso atual)', color:'#e7ebf3' } },
    scales: { x: { ticks: { color:'#9aa6bd' } }, y: { ticks: { color:'#9aa6bd' } } } }
});

new Chart(document.getElementById('metodosChart'), {
  type: 'bar',
  data: {
    labels: dados.metodos.map(m => m.metodo.replace(/^M[0-9]_/,'')),
    datasets: [
      { label: 'Média de acertos', data: dados.metodos.map(m => m.media_acertos), backgroundColor: '#5b8def' },
      { label: 'Esperança teórica', data: dados.metodos.map(() => dados.esperanca), type: 'line',
        borderColor: '#3fbf7f', borderDash: [6,4], pointRadius: 0 }
    ]
  },
  options: { plugins: { legend: { labels: { color:'#e7ebf3' } }, title: { display:true, text:'Média de acertos por método vs. valor esperado', color:'#e7ebf3' } },
    scales: { x: { ticks: { color:'#9aa6bd' } }, y: { ticks: { color:'#9aa6bd' }, suggestedMax: 15 } } }
});

if (dados.backtest_metodos && dados.backtest_metodos.length) {
  new Chart(document.getElementById('backtestChart'), {
    type: 'bar',
    data: {
      labels: dados.backtest_metodos.map(m => m.metodo.replace(/^M[0-9]_/,'')),
      datasets: [
        { label: 'Média de acertos (backtest)', data: dados.backtest_metodos.map(m => m.media_acertos), backgroundColor: '#a78bfa' },
        { label: 'Esperança teórica', data: dados.backtest_metodos.map(() => dados.esperanca), type: 'line',
          borderColor: '#3fbf7f', borderDash: [6,4], pointRadius: 0 }
      ]
    },
    options: { plugins: { legend: { labels: { color:'#e7ebf3' } },
      title: { display:true, text:'Backtest em milhares de concursos reais (eixo ampliado p/ mostrar a diferença)', color:'#e7ebf3' } },
      scales: { x: { ticks: { color:'#9aa6bd' } }, y: { ticks: { color:'#9aa6bd' }, min: 8.5, max: 9.5 } } }
  });
}
</script>
</body>
</html>
"""


def main():
    freq, atraso, total = lib.frequencia_e_atraso()
    resultados = lib.carregar_resultados()
    ultimo_concurso = resultados[-1]["concurso"] if resultados else "-"
    proximo_concurso = (resultados[-1]["concurso"] + 1) if resultados else 1

    stats_metodos = lib.calcular_estatisticas_metodos()
    total_conferidos = sum(l["total_jogos_conferidos"] for l in stats_metodos)

    jogos = lib.carregar_jogos()
    jogos_proximo = [j for j in jogos if j["concurso_alvo"] == proximo_concurso]

    conferencias = lib.carregar_conferencias()
    ultimas_conf = conferencias[-15:][::-1]

    stats_backtest = []
    sim_path = os.path.join(lib.DADOS_DIR, "estatisticas_simulacao.csv")
    if os.path.exists(sim_path):
        with open(sim_path, encoding="utf-8") as f:
            stats_backtest = list(csv.DictReader(f))

    dados_json = {
        "dezenas": lib.TODAS_DEZENAS,
        "freq_pct": [round(100 * freq[d] / total, 2) if total else 0 for d in lib.TODAS_DEZENAS],
        "atraso": [atraso[d] for d in lib.TODAS_DEZENAS],
        "metodos": [{"metodo": l["metodo"], "media_acertos": l["media_acertos"]} for l in stats_metodos],
        "esperanca": lib.ESPERANCA_TEORICA,
        "backtest_metodos": [{"metodo": l["metodo"], "media_acertos": float(l["media_acertos"])} for l in stats_backtest],
    }

    tabela_metodos = "".join(
        f"<tr><td>{l['metodo']}</td><td>{l['total_jogos_conferidos']}</td>"
        f"<td>{l['media_acertos']}</td><td>{l['desvio_padrao_acertos']}</td>"
        f"<td>{l['pct_11_ou_mais']}%</td><td>{l['pct_13_ou_mais']}%</td></tr>"
        for l in stats_metodos
    )

    tabela_jogos = "".join(
        f"<tr><td>{j['metodo']}</td><td>{j['dezenas']}</td><td>{j['soma']}</td>"
        f"<td>{j['pares']}p / {j['impares']}i</td></tr>"
        for j in jogos_proximo
    ) or "<tr><td colspan=4>Ainda não gerado.</td></tr>"

    tabela_backtest = "".join(
        f"<tr><td>{l['metodo']}</td><td>{l['total_concursos_simulados']}</td>"
        f"<td>{l['media_acertos']}</td><td>{float(l['diferenca_vs_esperanca']):+.4f}</td>"
        f"<td>{l['pct_13_ou_mais']}%</td></tr>"
        for l in stats_backtest
    ) or "<tr><td colspan=5>Simulação ainda não rodada (scripts/simular_backtest.py).</td></tr>"

    tabela_conf = "".join(
        f"<tr><td>{c['concurso']}</td><td>{c['metodo']}</td>"
        f"<td><span class='pill {'ok' if c['acertos'] >= int(lib.ESPERANCA_TEORICA) else 'mid'}'>{c['acertos']}</span></td></tr>"
        for c in ultimas_conf
    ) or "<tr><td colspan=3>Ainda sem conferências.</td></tr>"

    html = TEMPLATE
    html = html.replace("__ATUALIZADO_EM__", datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M"))
    html = html.replace("__ULTIMO_CONCURSO__", str(ultimo_concurso))
    html = html.replace("__TOTAL_CONCURSOS__", str(total))
    html = html.replace("__PROXIMO_CONCURSO__", str(proximo_concurso))
    html = html.replace("__ESPERANCA__", str(lib.ESPERANCA_TEORICA))
    html = html.replace("__TOTAL_CONFERIDOS__", str(total_conferidos))
    html = html.replace("__TABELA_METODOS__", tabela_metodos)
    html = html.replace("__TABELA_BACKTEST__", tabela_backtest)
    html = html.replace("__TABELA_JOGOS__", tabela_jogos)
    html = html.replace("__TABELA_CONFERENCIAS__", tabela_conf)
    html = html.replace("__DADOS_JSON__", json.dumps(dados_json, ensure_ascii=False))

    with open(PAINEL_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Painel gerado em: {PAINEL_PATH}")


if __name__ == "__main__":
    main()
