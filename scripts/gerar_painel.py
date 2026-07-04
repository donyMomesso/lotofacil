"""
Gera painel.html (Painel Classico): visao geral estatistica do laboratorio,
com o novo design roxo/rosa/ambar baseado no mockup do manus.ai.

E uma fotografia estatica, regenerada a cada ciclo diario -- nao busca
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
<title>Painel Clássico — Laboratório Lotofácil</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Inter',sans-serif; background:#FAF7FF; color:#1F1235; min-height:100vh; }
  table { width:100%; border-collapse:collapse; }
  .card { background:#fff; border:1px solid #E9DFFB; border-radius:16px; padding:18px; box-shadow:0 2px 10px rgba(43,10,77,.06); }
  .muted { color:#8B76B0; }
  .kicker { font-size:14px; color:#8B76B0; text-transform:uppercase; letter-spacing:.05em; font-weight:700; margin:0 0 12px; }
  th { color:#8B76B0; font-size:11.5px; text-transform:uppercase; text-align:left; padding:8px 10px; border-bottom:1px solid #E9DFFB; }
  td { padding:8px 10px; border-bottom:1px solid #F1ECFB; font-size:13px; }
  tr:last-child td { border-bottom:none; }
  .pill { display:inline-block; border-radius:999px; padding:3px 10px; font-weight:700; font-size:12.5px; }
  .pill.ok { background:#DCFCE7; color:#16A34A; }
  .pill.mid { background:#EDE4FF; color:#7C3AED; }
  canvas { max-height:300px; }
</style>
</head>
<body>

<div style="background:linear-gradient(135deg,#5B21B6,#7C3AED 55%,#C026D3); padding:26px 32px 22px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; box-shadow:0 6px 22px rgba(43,10,77,.25);">
  <div>
    <a href="index.html" style="font-size:11.5px; color:rgba(255,255,255,.65); text-decoration:none;">← Lotofácil Lab</a>
    <h1 style="font-family:'Sora',sans-serif; font-size:22px; font-weight:800; color:#fff; margin:4px 0 2px;">Painel Clássico</h1>
    <div style="font-size:12.5px; color:rgba(255,255,255,.75);">Painel gerado em __ATUALIZADO_EM__ (Brasília) · concurso mais recente: __ULTIMO_CONCURSO__</div>
  </div>
  <div style="background:rgba(255,255,255,.16); border:1px solid rgba(255,255,255,.3); border-radius:8px; padding:6px 14px; font-size:12px; color:#fff; font-weight:600;">⚠ Estudo estatístico — não é recomendação de aposta</div>
</div>

<div style="margin:22px 32px; padding:14px 18px; border-radius:12px; background:linear-gradient(90deg, rgba(245,158,11,.14), rgba(245,158,11,.05)); border:1px solid rgba(245,158,11,.35); font-size:13.5px; line-height:1.55;">
  <b style="color:#B45309;">Isto é um estudo de matemática e estatística.</b> Nenhum jogo aqui é recomendação de aposta. Todos os métodos são comparados contra o valor teórico esperado (__ESPERANCA__ acertos por jogo de 15 dezenas).
</div>

<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:14px; margin:0 32px 8px;">
  <div class="card">
    <div class="muted" style="font-size:11.5px; text-transform:uppercase; letter-spacing:.05em; font-weight:600;">Concursos no histórico</div>
    <div style="font-size:27px; font-weight:800; margin-top:6px; font-family:'Sora',sans-serif;">__TOTAL_CONCURSOS__</div>
  </div>
  <div class="card">
    <div class="muted" style="font-size:11.5px; text-transform:uppercase; letter-spacing:.05em; font-weight:600;">Próximo concurso</div>
    <div style="font-size:27px; font-weight:800; margin-top:6px; font-family:'Sora',sans-serif;">__PROXIMO_CONCURSO__</div>
  </div>
  <div class="card">
    <div class="muted" style="font-size:11.5px; text-transform:uppercase; letter-spacing:.05em; font-weight:600;">Esperança teórica</div>
    <div style="font-size:27px; font-weight:800; margin-top:6px; font-family:'Sora',sans-serif; color:#7C3AED;">__ESPERANCA__</div>
    <div class="muted" style="font-size:11.5px; margin-top:2px;">distribuição hipergeométrica</div>
  </div>
  <div class="card">
    <div class="muted" style="font-size:11.5px; text-transform:uppercase; letter-spacing:.05em; font-weight:600;">Jogos de estudo conferidos</div>
    <div style="font-size:27px; font-weight:800; margin-top:6px; font-family:'Sora',sans-serif;">__TOTAL_CONFERIDOS__</div>
  </div>
</div>

<section style="margin:26px 32px;">
  <h2 class="kicker">Frequência e atraso das dezenas</h2>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">
    <div class="card"><canvas id="freqChart"></canvas></div>
    <div class="card"><canvas id="atrasoChart"></canvas></div>
  </div>
</section>

<section style="margin:26px 32px;">
  <h2 class="kicker">Desempenho comparado dos métodos</h2>
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">
    <div class="card"><canvas id="metodosChart"></canvas></div>
    <div class="card" style="overflow:auto;">
      <table>
        <thead><tr><th>Método</th><th>Jogos</th><th>Média</th><th>Desvio</th><th>11+</th><th>13+</th></tr></thead>
        <tbody>__TABELA_METODOS__</tbody>
      </table>
    </div>
  </div>
</section>

<section style="margin:26px 32px;">
  <h2 class="kicker">Simulação retroativa (backtest em todo o histórico real)</h2>
  <div class="card"><canvas id="backtestChart"></canvas></div>
</section>

<section style="margin:26px 32px;">
  <h2 class="kicker">Jogos de estudo do próximo concurso</h2>
  <div class="card" style="overflow:auto;">
    <table>
      <thead><tr><th>Método</th><th>Dezenas</th><th>Soma</th><th>Pares/Ímpares</th></tr></thead>
      <tbody>__TABELA_JOGOS__</tbody>
    </table>
  </div>
</section>

<section style="margin:26px 32px;">
  <h2 class="kicker">Últimas conferências</h2>
  <div class="card" style="overflow:auto;">
    <table>
      <thead><tr><th>Concurso</th><th>Método</th><th>Acertos</th></tr></thead>
      <tbody>__TABELA_CONFERENCIAS__</tbody>
    </table>
  </div>
</section>

<section style="margin:26px 32px;">
  <h2 class="kicker">Apostas estendidas (16 a 20 dezenas): custo × cobertura</h2>
  <div style="padding:14px 18px; border-radius:12px; background:linear-gradient(90deg, rgba(245,158,11,.14), rgba(245,158,11,.05)); border:1px solid rgba(245,158,11,.35); font-size:13px; line-height:1.55; margin-bottom:14px;">
    Isto é combinatória pura, não depende de nenhum sorteio real e <b style="color:#B45309;">não é recomendação de aposta</b>. Apostar com mais dezenas aumenta a média esperada de acertos, mas o custo sobe pela mesma matemática.
  </div>
  <div class="card"><canvas id="estendidasChart" style="max-height:320px;"></canvas></div>
</section>

<section style="margin:26px 32px;">
  <h2 class="kicker">Sequência e salto das trincas de dezenas consecutivas</h2>
  <div style="padding:14px 18px; border-radius:12px; background:linear-gradient(90deg, rgba(124,58,237,.10), rgba(124,58,237,.03)); border:1px solid rgba(124,58,237,.25); font-size:13px; line-height:1.55; margin-bottom:14px;">
    Toda trinca de 3 dezenas consecutivas tem a mesma probabilidade teórica de sair junta (__SEQ_TEORICA__%) ou de nenhuma sair (__SALTO_TEORICA__%). A variação entre trincas abaixo é ruído amostral — nenhuma está "mais perto" ou "mais atrasada".
  </div>
  <div class="card" style="overflow:auto;">
    <table>
      <thead><tr><th>Trinca</th><th>Sequência</th><th>%</th><th>Teórico</th><th>Salto</th><th>%</th><th>Teórico</th></tr></thead>
      <tbody>__TABELA_SEQSALTO__</tbody>
    </table>
  </div>
</section>

<section style="margin:26px 32px;">
  <h2 class="kicker">Exemplos filtrados: combinações fixas testadas contra todo o histórico</h2>
  <div style="padding:14px 18px; border-radius:12px; background:linear-gradient(90deg, rgba(124,58,237,.10), rgba(124,58,237,.03)); border:1px solid rgba(124,58,237,.25); font-size:13px; line-height:1.55; margin-bottom:14px;">
    Cada linha é uma combinação fixa de 15 dezenas (exemplo do espaço filtrado: par/ímpar 8/7, soma 180-210, sem sequência de 6+, no máximo 1 linha vazia), conferida contra <b>todos</b> os concursos reais. Não é jogo para apostar — mostra que combinações "bem-comportadas" também convergem para a esperança teórica.
  </div>
  <div class="card" style="overflow:auto;">
    <table>
      <thead><tr><th>Exemplo</th><th>Dezenas</th><th>Concursos testados</th><th>Média</th><th>Dif. vs. esperança</th><th>Máx.</th><th>11+</th><th>13+</th></tr></thead>
      <tbody>__TABELA_EXEMPLOS__</tbody>
    </table>
  </div>
</section>

<footer style="padding:24px 32px 44px; color:#8B76B0; font-size:12px;">Gerado automaticamente por scripts/gerar_painel.py · ver README.md e diario_estatistico.md para o raciocínio completo por trás de cada atualização.</footer>

<script>
const dados = __DADOS_JSON__;
const muted = '#8B76B0';

new Chart(document.getElementById('freqChart'), {
  type:'bar',
  data:{ labels:dados.dezenas.map(d=>d.toString().padStart(2,'0')), datasets:[{ label:'Frequência (%)', data:dados.freq_pct, backgroundColor:'#7C3AED', borderRadius:4 }] },
  options:{ plugins:{ legend:{display:false}, title:{display:true, text:'Frequência relativa de cada dezena (%)', color:'#1F1235'} },
    scales:{ x:{ ticks:{color:muted} }, y:{ ticks:{color:muted} } } }
});

new Chart(document.getElementById('atrasoChart'), {
  type:'bar',
  data:{ labels:dados.dezenas.map(d=>d.toString().padStart(2,'0')), datasets:[{ label:'Atraso (concursos)', data:dados.atraso, backgroundColor:'#F59E0B', borderRadius:4 }] },
  options:{ plugins:{ legend:{display:false}, title:{display:true, text:'Concursos sem sair (atraso atual)', color:'#1F1235'} },
    scales:{ x:{ ticks:{color:muted} }, y:{ ticks:{color:muted} } } }
});

new Chart(document.getElementById('metodosChart'), {
  data:{ labels:dados.metodos.map(m=>m.metodo.replace(/^M[0-9]_/,'')), datasets:[
    { type:'bar', label:'Média de acertos', data:dados.metodos.map(m=>m.media_acertos), backgroundColor:'#EC4899', borderRadius:4 },
    { type:'line', label:'Esperança teórica', data:dados.metodos.map(()=>dados.esperanca), borderColor:'#16A34A', borderDash:[6,4], pointRadius:0 }
  ]},
  options:{ plugins:{ legend:{labels:{color:'#1F1235'}}, title:{display:true, text:'Média de acertos por método vs. valor esperado', color:'#1F1235'} },
    scales:{ x:{ ticks:{color:muted} }, y:{ ticks:{color:muted}, suggestedMax:15 } } }
});

if (dados.backtest_metodos && dados.backtest_metodos.length) {
  new Chart(document.getElementById('backtestChart'), {
    data:{ labels:dados.backtest_metodos.map(m=>m.metodo.replace(/^M[0-9]_/,'')), datasets:[
      { type:'bar', label:'Média de acertos (backtest)', data:dados.backtest_metodos.map(m=>m.media_acertos), backgroundColor:'#A855F7', borderRadius:4 },
      { type:'line', label:'Esperança teórica', data:dados.backtest_metodos.map(()=>dados.esperanca), borderColor:'#16A34A', borderDash:[6,4], pointRadius:0 }
    ]},
    options:{ plugins:{ legend:{labels:{color:'#1F1235'}}, title:{display:true, text:'Backtest em milhares de concursos reais (eixo ampliado)', color:'#1F1235'} },
      scales:{ x:{ ticks:{color:muted} }, y:{ ticks:{color:muted}, min:8.5, max:9.5 } } }
  });
}

if (dados.estendidas && dados.estendidas.length) {
  new Chart(document.getElementById('estendidasChart'), {
    data:{ labels:dados.estendidas.map(e=>e.dezenas_na_aposta+' dezenas'), datasets:[
      { type:'bar', label:'Custo (R$, escala log)', data:dados.estendidas.map(e=>e.custo_reais), backgroundColor:'#F59E0B', yAxisID:'yCusto' },
      { type:'line', label:'Média de acertos esperada', data:dados.estendidas.map(e=>e.media_acertos_esperada), borderColor:'#16A34A', backgroundColor:'#16A34A', yAxisID:'yMedia', tension:.3 }
    ]},
    options:{ plugins:{ legend:{labels:{color:'#1F1235'}}, title:{display:true, text:'Custo (R$) vs. média esperada de acertos, por tamanho da aposta', color:'#1F1235'} },
      scales:{ x:{ ticks:{color:muted} },
        yCusto:{ type:'logarithmic', position:'left', ticks:{color:muted}, title:{display:true,text:'Custo (R$)',color:muted} },
        yMedia:{ position:'right', min:8, max:13, ticks:{color:muted}, grid:{drawOnChartArea:false}, title:{display:true,text:'Média esperada',color:muted} } } }
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

    estendidas = []
    estendidas_path = os.path.join(lib.DADOS_DIR, "apostas_estendidas.csv")
    if os.path.exists(estendidas_path):
        with open(estendidas_path, encoding="utf-8") as f:
            estendidas = list(csv.DictReader(f))

    seqsalto = []
    seqsalto_path = os.path.join(lib.DADOS_DIR, "sequencias_saltos.csv")
    if os.path.exists(seqsalto_path):
        with open(seqsalto_path, encoding="utf-8") as f:
            seqsalto = list(csv.DictReader(f))
    seq_teo = seqsalto[0]["sequencia_teorica_pct"] if seqsalto else "-"
    salto_teo = seqsalto[0]["salto_teorico_pct"] if seqsalto else "-"

    exemplos = []
    exemplos_path = os.path.join(lib.DADOS_DIR, "exemplos_filtrados_backtest.csv")
    if os.path.exists(exemplos_path):
        with open(exemplos_path, encoding="utf-8") as f:
            exemplos = list(csv.DictReader(f))

    dados_json = {
        "dezenas": lib.TODAS_DEZENAS,
        "freq_pct": [round(100 * freq[d] / total, 2) if total else 0 for d in lib.TODAS_DEZENAS],
        "atraso": [atraso[d] for d in lib.TODAS_DEZENAS],
        "metodos": [{"metodo": l["metodo"], "media_acertos": l["media_acertos"]} for l in stats_metodos],
        "esperanca": lib.ESPERANCA_TEORICA,
        "backtest_metodos": [{"metodo": l["metodo"], "media_acertos": float(l["media_acertos"])} for l in stats_backtest],
        "estendidas": [
            {
                "dezenas_na_aposta": int(e["dezenas_na_aposta"]),
                "custo_reais": float(e["custo_reais"]),
                "media_acertos_esperada": float(e["media_acertos_esperada"]),
            }
            for e in estendidas
        ],
    }

    tabela_metodos = "".join(
        f"<tr><td>{l['metodo']}</td><td>{l['total_jogos_conferidos']}</td>"
        f"<td>{l['media_acertos']}</td><td>{l['desvio_padrao_acertos']}</td>"
        f"<td>{l['pct_11_ou_mais']}%</td><td>{l['pct_13_ou_mais']}%</td></tr>"
        for l in stats_metodos
    )

    tabela_jogos = "".join(
        f"<tr><td>{j['metodo']}</td><td style='font-family:monospace;'>{j['dezenas']}</td><td>{j['soma']}</td>"
        f"<td>{j['pares']}p / {j['impares']}i</td></tr>"
        for j in jogos_proximo
    ) or "<tr><td colspan=4>Ainda não gerado.</td></tr>"

    tabela_backtest_placeholder = ""  # backtest fica só no grafico, igual ao mockup

    tabela_conf = "".join(
        f"<tr><td>{c['concurso']}</td><td>{c['metodo']}</td>"
        f"<td><span class='pill {'ok' if c['acertos'] >= int(lib.ESPERANCA_TEORICA) else 'mid'}'>{c['acertos']}</span></td></tr>"
        for c in ultimas_conf
    ) or "<tr><td colspan=3>Ainda sem conferências.</td></tr>"

    tabela_seqsalto = "".join(
        f"<tr><td>{l['trinca']}</td><td>{l['sequencia_qtd']}</td><td>{l['sequencia_pct']}%</td>"
        f"<td>{seq_teo}%</td><td>{l['salto_qtd']}</td><td>{l['salto_pct']}%</td><td>{salto_teo}%</td></tr>"
        for l in seqsalto
    ) or "<tr><td colspan=7>Ainda não calculado (scripts/tabela_sequencias.py).</td></tr>"

    tabela_exemplos = "".join(
        f"<tr><td>{e['exemplo']}</td><td style='font-family:monospace;'>{e['dezenas']}</td>"
        f"<td>{e['total_concursos_testados']}</td><td>{e['media_acertos']}</td>"
        f"<td>{float(e['diferenca_vs_esperanca']):+.4f}</td><td>{e['max_acertos_observado']}</td>"
        f"<td>{e['pct_11_ou_mais']}%</td><td>{e['pct_13_ou_mais']}%</td></tr>"
        for e in exemplos
    ) or "<tr><td colspan=8>Ainda não calculado (scripts/estudo_desdobramento_filtros.py).</td></tr>"

    html = TEMPLATE
    html = html.replace("__ATUALIZADO_EM__", datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M"))
    html = html.replace("__ULTIMO_CONCURSO__", str(ultimo_concurso))
    html = html.replace("__TOTAL_CONCURSOS__", str(total))
    html = html.replace("__PROXIMO_CONCURSO__", str(proximo_concurso))
    html = html.replace("__ESPERANCA__", str(lib.ESPERANCA_TEORICA))
    html = html.replace("__TOTAL_CONFERIDOS__", str(total_conferidos))
    html = html.replace("__TABELA_METODOS__", tabela_metodos)
    html = html.replace("__TABELA_JOGOS__", tabela_jogos)
    html = html.replace("__TABELA_CONFERENCIAS__", tabela_conf)
    html = html.replace("__TABELA_SEQSALTO__", tabela_seqsalto)
    html = html.replace("__SEQ_TEORICA__", str(seq_teo))
    html = html.replace("__SALTO_TEORICA__", str(salto_teo))
    html = html.replace("__TABELA_EXEMPLOS__", tabela_exemplos)
    html = html.replace("__DADOS_JSON__", json.dumps(dados_json, ensure_ascii=False))

    with open(PAINEL_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"painel.html (Classico) gerado em: {PAINEL_PATH}")


if __name__ == "__main__":
    main()
