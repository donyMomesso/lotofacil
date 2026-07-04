"""
Gera painel_mobile.html: painel mobile-first para acessar o laboratório
pelo celular, usando dados/banco_projeto.json como banco de leitura.

Uso:
    python3 gerar_painel_mobile.py
"""
import json
import os
from datetime import datetime, timezone, timedelta

import gerar_banco_projeto
import lotofacil_lib as lib

BRASILIA = timezone(timedelta(hours=-3))
PAINEL_MOBILE_PATH = os.path.join(lib.BASE_DIR, "painel_mobile.html")
BANCO_PATH = os.path.join(lib.DADOS_DIR, "banco_projeto.json")

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>Lotofácil Lab — Mobile</title>
<style>
  :root {
    --bg: #faf7ff;
    --card: #ffffff;
    --text: #1f1235;
    --muted: #7c6a9b;
    --line: #eadffd;
    --purple: #7c3aed;
    --pink: #ec4899;
    --amber: #f59e0b;
    --green: #16a34a;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
  }
  header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: linear-gradient(135deg, #5b21b6, #7c3aed 60%, #c026d3);
    color: white;
    padding: 18px 16px 14px;
    box-shadow: 0 6px 20px rgba(43,10,77,.22);
  }
  h1 { margin: 0; font-size: 22px; line-height: 1.15; }
  .sub { margin-top: 5px; color: rgba(255,255,255,.76); font-size: 12.5px; line-height: 1.45; }
  .tabs {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 12px 14px 2px;
    scrollbar-width: none;
  }
  .tabs::-webkit-scrollbar { display: none; }
  .tabs a {
    flex: 0 0 auto;
    text-decoration: none;
    color: var(--text);
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 9px 12px;
    font-size: 13px;
    font-weight: 700;
  }
  .tabs a.primary { background: var(--purple); color: white; border-color: var(--purple); }
  main { padding: 12px 14px 34px; }
  .alert {
    background: linear-gradient(90deg, rgba(245,158,11,.18), rgba(245,158,11,.06));
    border: 1px solid rgba(245,158,11,.38);
    border-radius: 14px;
    padding: 13px 14px;
    font-size: 13.5px;
    line-height: 1.45;
    margin-bottom: 12px;
  }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 14px;
    box-shadow: 0 2px 10px rgba(43,10,77,.06);
  }
  .label { color: var(--muted); font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: .05em; }
  .value { font-size: 25px; font-weight: 900; margin-top: 6px; line-height: 1; }
  section { margin-top: 18px; scroll-margin-top: 95px; }
  h2 { font-size: 13px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin: 0 0 10px; }
  .result-row, .dezena-row, .link-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    border-bottom: 1px solid #f0e9fb;
    padding: 10px 0;
    font-size: 13.5px;
  }
  .result-row:last-child, .dezena-row:last-child, .link-row:last-child { border-bottom: none; }
  .nums { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12.5px; color: #4c1d95; line-height: 1.5; }
  .badge {
    display: inline-block;
    border-radius: 999px;
    padding: 3px 9px;
    background: #ede4ff;
    color: var(--purple);
    font-size: 12px;
    font-weight: 800;
    white-space: nowrap;
  }
  .badge.green { background: #dcfce7; color: var(--green); }
  .badge.amber { background: #fef3c7; color: #b45309; }
  .bar {
    height: 8px;
    background: #f0e9fb;
    border-radius: 999px;
    overflow: hidden;
    margin-top: 6px;
  }
  .bar span { display: block; height: 100%; background: linear-gradient(90deg, var(--purple), var(--pink)); }
  a { color: var(--purple); font-weight: 800; }
  @media (max-width: 380px) {
    .grid { grid-template-columns: 1fr; }
    h1 { font-size: 20px; }
  }
</style>
</head>
<body>
<header>
  <h1>Lotofácil Lab</h1>
  <div class="sub">Painel mobile · atualizado em __GERADO_EM__ · concurso __ULTIMO_CONCURSO__</div>
</header>

<nav class="tabs">
  <a class="primary" href="#resumo">Resumo</a>
  <a href="#resultados">Resultados</a>
  <a href="#frequencia">Frequência</a>
  <a href="#jogos">Jogos</a>
  <a href="#links">Arquivos</a>
  <a href="painel.html">Clássico</a>
  <a href="painel_jogos.html">Jogos</a>
</nav>

<main>
  <div class="alert"><b>Estudo estatístico.</b> Não é previsão, não é recomendação de aposta e não indica combinação “mais perto” de acertar.</div>

  <section id="resumo">
    <h2>Resumo</h2>
    <div class="grid">
      <div class="card"><div class="label">Concursos</div><div class="value">__TOTAL_CONCURSOS__</div></div>
      <div class="card"><div class="label">Próximo</div><div class="value">__PROXIMO__</div></div>
      <div class="card"><div class="label">Esperança</div><div class="value">__ESPERANCA__</div></div>
      <div class="card"><div class="label">Último</div><div class="value">__ULTIMO_CONCURSO__</div></div>
    </div>
  </section>

  <section id="resultados">
    <h2>Últimos resultados</h2>
    <div class="card">__ULTIMOS_RESULTADOS__</div>
  </section>

  <section id="frequencia">
    <h2>Frequência e atraso</h2>
    <div class="card">__FREQUENCIA_DEZENAS__</div>
  </section>

  <section id="jogos">
    <h2>Jogos de estudo do próximo concurso</h2>
    <div class="card">__JOGOS_PROXIMO__</div>
  </section>

  <section id="links">
    <h2>Banco e arquivos do projeto</h2>
    <div class="card">__LINKS__</div>
  </section>
</main>
</body>
</html>
"""


def _carregar_banco():
    if not os.path.exists(BANCO_PATH):
        gerar_banco_projeto.main()
    with open(BANCO_PATH, encoding="utf-8") as f:
        return json.load(f)


def _ultimos_resultados_html(banco):
    linhas = []
    for r in banco.get("ultimos_resultados", [])[:8]:
        linhas.append(
            f"<div class='result-row'><div><b>Concurso {r['concurso']}</b><br>"
            f"<span class='nums'>{r['dezenas_formatadas']}</span></div>"
            f"<span class='badge amber'>{r['data']}</span></div>"
        )
    return "".join(linhas) or "<div class='muted'>Sem resultados.</div>"


def _frequencia_html(banco):
    dezenas = banco.get("frequencia_dezenas", [])
    if not dezenas:
        return "<div class='muted'>Sem frequência calculada.</div>"

    max_freq = max(d["frequencia_absoluta"] for d in dezenas) or 1
    top = sorted(dezenas, key=lambda d: d["frequencia_absoluta"], reverse=True)[:10]
    linhas = []
    for d in top:
        largura = round(d["frequencia_absoluta"] / max_freq * 100, 1)
        linhas.append(
            f"<div class='dezena-row'><div><b>{d['dezena_formatada']}</b> · "
            f"{d['frequencia_absoluta']}x · atraso {d['atraso_atual']}<div class='bar'><span style='width:{largura}%'></span></div></div>"
            f"<span class='badge'>{d['frequencia_pct']}%</span></div>"
        )
    return "".join(linhas)


def _jogos_html(banco):
    jogos = banco.get("jogos_proximo_concurso", [])
    if not jogos:
        return "<div class='muted'>Ainda sem jogos gerados para o próximo concurso.</div>"

    linhas = []
    for j in jogos:
        linhas.append(
            f"<div class='result-row'><div><b>{j['metodo']}</b><br>"
            f"<span class='nums'>{j['dezenas']}</span></div>"
            f"<span class='badge green'>{j['soma']}</span></div>"
        )
    return "".join(linhas)


def _links_html(banco):
    links = banco.get("links_internos", [])
    extras = [{"titulo": "Painel mobile", "arquivo": "painel_mobile.html"}]
    linhas = []
    for item in extras + links:
        linhas.append(
            f"<div class='link-row'><span>{item['titulo']}</span><a href='{item['arquivo']}'>abrir</a></div>"
        )
    return "".join(linhas)


def main():
    banco = _carregar_banco()
    meta = banco.get("meta", {})
    ultimo = meta.get("ultimo_concurso") or {}

    html = TEMPLATE
    html = html.replace("__GERADO_EM__", meta.get("gerado_em", datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M")))
    html = html.replace("__TOTAL_CONCURSOS__", str(meta.get("total_concursos", 0)))
    html = html.replace("__PROXIMO__", str(meta.get("proximo_concurso", "-")))
    html = html.replace("__ESPERANCA__", str(meta.get("esperanca_teorica_acertos", lib.ESPERANCA_TEORICA)))
    html = html.replace("__ULTIMO_CONCURSO__", str(ultimo.get("concurso", "-")))
    html = html.replace("__ULTIMOS_RESULTADOS__", _ultimos_resultados_html(banco))
    html = html.replace("__FREQUENCIA_DEZENAS__", _frequencia_html(banco))
    html = html.replace("__JOGOS_PROXIMO__", _jogos_html(banco))
    html = html.replace("__LINKS__", _links_html(banco))

    with open(PAINEL_MOBILE_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Painel mobile gerado em: {PAINEL_MOBILE_PATH}")


if __name__ == "__main__":
    main()
