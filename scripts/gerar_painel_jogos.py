"""
Gera painel_jogos.html: painel visual completo de jogos gerados e conferências.
Exibe:
  - Jogos gerados por método para o próximo concurso (com dezenas destacadas)
  - Tabela de conferências (acertos por método)
  - Gráfico de distribuição de acertos (backtest) — SVG puro, sem biblioteca
  - Mapa de calor das dezenas (frequência e atraso)
  - Histórico dos últimos concursos

É um arquivo HTML autônomo (sem servidor), regenerado a cada ciclo diário.
Uso:
    python3 gerar_painel_jogos.py
"""
import csv
import json
import os
import math
from datetime import datetime, timezone, timedelta
import lotofacil_lib as lib

PAINEL_PATH = os.path.join(lib.BASE_DIR, "painel_jogos.html")
BRASILIA = timezone(timedelta(hours=-3))

CORES = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#a78bfa"]
METODO_LABELS = {
    "M1_aleatorio_puro": "M1 Aleatório",
    "M2_mais_frequentes": "M2 Mais Freq.",
    "M3_mais_atrasadas": "M3 Mais Atras.",
    "M4_par_impar_balanceado": "M4 Par/Ímpar",
    "M5_soma_faixa_comum": "M5 Soma Faixa",
}
METODO_CLASS = {
    "M1_aleatorio_puro": "m1",
    "M2_mais_frequentes": "m2",
    "M3_mais_atrasadas": "m3",
    "M4_par_impar_balanceado": "m4",
    "M5_soma_faixa_comum": "m5",
}


def carregar_ultimos_resultados(n=15):
    resultados = lib.carregar_resultados()
    return resultados[-n:]


def svg_bar_chart(datasets, labels, width=560, height=260, title=""):
    """Gera um gráfico de barras agrupadas em SVG puro."""
    pad_left, pad_right, pad_top, pad_bottom = 50, 20, 30, 40
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    n_groups = len(labels)
    n_series = len(datasets)
    bar_w = max(4, (chart_w / n_groups - 4) / n_series)
    group_w = bar_w * n_series + 4

    # Calcular max
    all_vals = [v for ds in datasets for v in ds["data"]]
    max_val = max(all_vals) if all_vals else 1
    y_ticks = 5
    tick_step = max_val / y_ticks

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="overflow:visible">']

    # Grid lines
    for i in range(y_ticks + 1):
        y = pad_top + chart_h - (i / y_ticks) * chart_h
        val = int(i * tick_step)
        svg.append(f'<line x1="{pad_left}" y1="{y:.1f}" x2="{pad_left+chart_w}" y2="{y:.1f}" stroke="#30363d" stroke-width="1"/>')
        svg.append(f'<text x="{pad_left-6}" y="{y+4:.1f}" text-anchor="end" fill="#8b949e" font-size="10">{val}</text>')

    # Bars
    for gi, label in enumerate(labels):
        gx = pad_left + gi * (chart_w / n_groups)
        for si, ds in enumerate(datasets):
            val = ds["data"][gi] if gi < len(ds["data"]) else 0
            bar_h = (val / max_val) * chart_h if max_val > 0 else 0
            bx = gx + si * bar_w + 2
            by = pad_top + chart_h - bar_h
            color = ds.get("color", CORES[si % len(CORES)])
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bar_h:.1f}" fill="{color}99" stroke="{color}" stroke-width="1" rx="2"/>')

        # X label
        lx = gx + group_w / 2
        svg.append(f'<text x="{lx:.1f}" y="{pad_top+chart_h+16}" text-anchor="middle" fill="#8b949e" font-size="10">{label}</text>')

    # Axes
    svg.append(f'<line x1="{pad_left}" y1="{pad_top}" x2="{pad_left}" y2="{pad_top+chart_h}" stroke="#30363d" stroke-width="1.5"/>')
    svg.append(f'<line x1="{pad_left}" y1="{pad_top+chart_h}" x2="{pad_left+chart_w}" y2="{pad_top+chart_h}" stroke="#30363d" stroke-width="1.5"/>')

    # Legend
    legend_y = height - 8
    lx = pad_left
    for si, ds in enumerate(datasets):
        color = ds.get("color", CORES[si % len(CORES)])
        svg.append(f'<rect x="{lx}" y="{legend_y-8}" width="10" height="10" fill="{color}99" stroke="{color}" rx="2"/>')
        svg.append(f'<text x="{lx+13}" y="{legend_y}" fill="#8b949e" font-size="10">{ds["label"]}</text>')
        lx += len(ds["label"]) * 6.5 + 20

    svg.append('</svg>')
    return "\n".join(svg)


def svg_media_chart(backtest, width=560, height=260):
    """Gera gráfico de barras horizontais com médias vs esperança."""
    pad_left, pad_right, pad_top, pad_bottom = 130, 20, 20, 20
    chart_w = width - pad_left - pad_right
    chart_h = height - pad_top - pad_bottom
    n = len(backtest)
    bar_h = chart_h / n - 8

    min_val, max_val = 8.85, 9.15
    esperanca = lib.ESPERANCA_TEORICA

    def xpos(val):
        return pad_left + (val - min_val) / (max_val - min_val) * chart_w

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']

    # Grid lines
    for tick in [8.9, 8.95, 9.0, 9.05, 9.1]:
        x = xpos(tick)
        color = "#58a6ff" if tick == 9.0 else "#30363d"
        svg.append(f'<line x1="{x:.1f}" y1="{pad_top}" x2="{x:.1f}" y2="{pad_top+chart_h}" stroke="{color}" stroke-width="1" stroke-dasharray="{"0" if tick==9.0 else "4,3"}"/>')
        svg.append(f'<text x="{x:.1f}" y="{pad_top+chart_h+14}" text-anchor="middle" fill="#8b949e" font-size="9">{tick}</text>')

    # Bars
    for i, b in enumerate(backtest):
        by = pad_top + i * (chart_h / n) + 4
        label = METODO_LABELS.get(b["metodo"], b["metodo"])
        color = CORES[i % len(CORES)]
        media = b["media"]
        bx = xpos(min(media, esperanca))
        bw = abs(xpos(media) - xpos(esperanca))
        bw = max(bw, 2)

        # Label
        svg.append(f'<text x="{pad_left-6}" y="{by+bar_h/2+4:.1f}" text-anchor="end" fill="{color}" font-size="11" font-weight="600">{label}</text>')
        # Bar background
        svg.append(f'<rect x="{pad_left}" y="{by:.1f}" width="{chart_w}" height="{bar_h:.1f}" fill="#ffffff08" rx="4"/>')
        # Bar value
        svg.append(f'<rect x="{bx:.1f}" y="{by+2:.1f}" width="{bw:.1f}" height="{bar_h-4:.1f}" fill="{color}99" stroke="{color}" stroke-width="1" rx="3"/>')
        # Value text
        vx = xpos(media) + (5 if media >= esperanca else -5)
        anchor = "start" if media >= esperanca else "end"
        svg.append(f'<text x="{vx:.1f}" y="{by+bar_h/2+4:.1f}" text-anchor="{anchor}" fill="{color}" font-size="11" font-weight="700">{media:.4f}</text>')

    # Esperança line
    ex = xpos(esperanca)
    svg.append(f'<line x1="{ex:.1f}" y1="{pad_top}" x2="{ex:.1f}" y2="{pad_top+chart_h}" stroke="#58a6ff" stroke-width="2"/>')
    svg.append(f'<text x="{ex+4:.1f}" y="{pad_top+12}" fill="#58a6ff" font-size="10">E=9.0</text>')

    svg.append('</svg>')
    return "\n".join(svg)


def render_heatmap(freq_list):
    """Gera o mapa de calor das dezenas como HTML."""
    pcts = [f["pct"] for f in freq_list]
    min_pct, max_pct = min(pcts), max(pcts)

    cells = []
    for f in freq_list:
        t = (f["pct"] - min_pct) / (max_pct - min_pct) if max_pct > min_pct else 0.5
        # Escala azul-frio → verde → amarelo
        r = int(t * 200)
        g = int(100 + t * 100)
        b = int(255 - t * 200)
        bg = f"rgba({r},{g},{b},0.2)"
        border = f"rgba({r},{g},{b},0.5)"
        atraso = f["atraso"]
        atraso_color = "#3fb950" if atraso == 0 else ("#d29922" if atraso <= 2 else "#f85149")
        cells.append(f'''<div class="hm-cell" style="background:{bg};border-color:{border}">
          <div class="hm-num">{f["d"]}</div>
          <div class="hm-pct">{f["pct"]}%</div>
          <div class="hm-atraso" style="color:{atraso_color}">atr:{atraso}</div>
        </div>''')
    return "\n".join(cells)


def render_atraso_bars(freq_list):
    sorted_list = sorted(freq_list, key=lambda x: x["atraso"], reverse=True)
    max_atraso = max(f["atraso"] for f in sorted_list) or 1
    bars = []
    for f in sorted_list:
        pct = f["atraso"] / max_atraso * 100
        color = "#3fb950" if f["atraso"] == 0 else ("#d29922" if f["atraso"] <= 2 else "#f85149")
        bars.append(f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:7px;">
          <span style="width:28px;text-align:center;font-weight:700;color:{color};font-size:13px">{f["d"]}</span>
          <div style="flex:1;height:7px;background:#30363d;border-radius:4px;overflow:hidden">
            <div style="width:{pct:.1f}%;height:100%;background:{color};border-radius:4px"></div>
          </div>
          <span style="width:65px;font-size:12px;color:#8b949e">{f["atraso"]} conc.</span>
        </div>''')
    return "\n".join(bars)


def render_jogos_html(jogos):
    concursos = {}
    for j in jogos:
        c = j["concurso_alvo"]
        if c not in concursos:
            concursos[c] = {"data": j["data_geracao"], "jogos": []}
        concursos[c]["jogos"].append(j)

    if not concursos:
        return '<div class="empty"><div class="icon">🎯</div><p>Nenhum jogo gerado ainda.</p></div>'

    html = []
    for c in sorted(concursos.keys(), reverse=True):
        info = concursos[c]
        html.append(f'''<div style="margin-bottom:28px;">
          <div class="concurso-header">
            <span class="concurso-num">Concurso #{c}</span>
            <span class="concurso-data">Gerado em {info["data"]}</span>
          </div>''')
        for j in info["jogos"]:
            label = METODO_LABELS.get(j["metodo"], j["metodo"])
            cls = METODO_CLASS.get(j["metodo"], "m1")
            dezenas = [int(d) for d in j["dezenas"].split("-")]
            bolas = "".join(f'<div class="bola bola-normal">{d:02d}</div>' for d in dezenas)
            html.append(f'''<div class="jogo-card">
              <div class="jogo-header">
                <span class="metodo-badge {cls}">{label}</span>
                <div class="jogo-meta">
                  <span>Soma: <b>{j["soma"]}</b></span>
                  <span>Pares: <b>{j["pares"]}</b></span>
                  <span>Ímpares: <b>{j["impares"]}</b></span>
                </div>
              </div>
              <div class="dezenas-grid">{bolas}</div>
            </div>''')
        html.append('</div>')
    return "\n".join(html)


def render_conferencia_html(conferencias):
    if not conferencias:
        return '''<div class="empty">
          <div class="icon">⏳</div>
          <p>Nenhuma conferência registrada ainda.</p>
          <p style="margin-top:8px;font-size:12px;color:#8b949e">As conferências aparecem aqui após o sorteio do concurso alvo.<br>O ciclo diário roda às 10h e captura o resultado da noite anterior.</p>
        </div>'''

    por_concurso = {}
    for c in conferencias:
        num = int(c["concurso"])
        if num not in por_concurso:
            por_concurso[num] = {"data": c["data_sorteio"], "sorteadas": [], "jogos": []}
        if not por_concurso[num]["sorteadas"] and c.get("dezenas_sorteadas"):
            por_concurso[num]["sorteadas"] = [int(d) for d in c["dezenas_sorteadas"].split("-")]
        dezenas_jogo = [int(d) for d in c["dezenas_jogo"].split("-")]
        por_concurso[num]["jogos"].append({
            "metodo": c["metodo"],
            "dezenas": dezenas_jogo,
            "acertos": int(c["acertos"]),
        })

    html = []
    for c in sorted(por_concurso.keys(), reverse=True):
        info = por_concurso[c]
        sorteadas = set(info["sorteadas"])
        bolas_sorteadas = "".join(f'<div class="bola bola-sorteada">{d:02d}</div>' for d in sorted(sorteadas))
        html.append(f'''<div style="margin-bottom:28px;">
          <div class="concurso-header">
            <span class="concurso-num">Concurso #{c}</span>
            <span class="concurso-data">Sorteado em {info["data"]}</span>
          </div>
          <div class="card" style="margin-bottom:14px;">
            <div class="card-title">Dezenas Sorteadas</div>
            <div class="dezenas-grid">{bolas_sorteadas}</div>
          </div>''')
        for j in info["jogos"]:
            label = METODO_LABELS.get(j["metodo"], j["metodo"])
            cls = METODO_CLASS.get(j["metodo"], "m1")
            ac = j["acertos"]
            ac_cls = "ac-low" if ac < 9 else ("ac-mid" if ac < 11 else ("ac-good" if ac < 13 else "ac-great"))
            bolas = "".join(
                f'<div class="bola {"bola-acerto" if d in sorteadas else "bola-erro"}">{d:02d}</div>'
                for d in j["dezenas"]
            )
            html.append(f'''<div class="jogo-card">
              <div class="jogo-header">
                <span class="metodo-badge {cls}">{label}</span>
                <span class="acertos-badge {ac_cls}">{ac} acertos</span>
              </div>
              <div class="dezenas-grid">{bolas}</div>
            </div>''')
        html.append('</div>')
    return "\n".join(html)


def render_backtest_stats(backtest):
    boxes = []
    for i, b in enumerate(backtest):
        label = METODO_LABELS.get(b["metodo"], b["metodo"])
        color = CORES[i % len(CORES)]
        dif = b["dif"]
        dif_str = f"+{dif:.4f}" if dif >= 0 else f"{dif:.4f}"
        dif_color = "#3fb950" if abs(dif) < 0.05 else "#d29922"
        boxes.append(f'''<div class="stat-box" style="border-top:3px solid {color}">
          <div class="label">{label.upper()}</div>
          <div class="value" style="color:{color};font-size:20px">{b["media"]:.4f}</div>
          <div class="hint" style="color:{dif_color}">Dif: {dif_str} vs esperança</div>
        </div>''')
    return "\n".join(boxes)


def render_backtest_table(backtest):
    rows = []
    for i, b in enumerate(backtest):
        label = METODO_LABELS.get(b["metodo"], b["metodo"])
        cls = METODO_CLASS.get(b["metodo"], "m1")
        dif = b["dif"]
        dif_str = f"+{dif:.4f}" if dif >= 0 else f"{dif:.4f}"
        dif_color = "#3fb950" if abs(dif) < 0.05 else "#d29922"
        rows.append(f'''<tr>
          <td><span class="metodo-badge {cls}">{label}</span></td>
          <td>{b["n"]:,}</td>
          <td><b>{b["media"]:.4f}</b></td>
          <td>{b["desvio"]:.4f}</td>
          <td style="color:{dif_color};font-weight:600">{dif_str}</td>
          <td>{b["pct_11"]}%</td>
          <td>{b["pct_13"]}%</td>
          <td>{b["pct_14"]}%</td>
          <td>{b["pct_15"]}%</td>
        </tr>''')
    return "\n".join(rows)


def render_historico_table(ultimos):
    rows = []
    for r in reversed(ultimos):
        dezenas = sorted(list(r["dezenas"]))
        pares = sum(1 for d in dezenas if d % 2 == 0)
        soma = sum(dezenas)
        dez_html = "".join(
            f'<span style="display:inline-block;background:rgba(88,166,255,.1);border:1px solid rgba(88,166,255,.2);border-radius:4px;padding:1px 5px;margin:1px;font-size:12px;font-weight:600;color:#58a6ff">{d:02d}</span>'
            for d in dezenas
        )
        rows.append(f'''<tr>
          <td><b style="color:#58a6ff">#{r["concurso"]}</b></td>
          <td style="color:#8b949e">{r["data"]}</td>
          <td>{dez_html}</td>
          <td>{soma}</td>
          <td>{pares}</td>
        </tr>''')
    return "\n".join(rows)


def build_html(jogos, conferencias, backtest, freq_list, ultimos_resultados, ultima_atualizacao):
    # Gráfico de distribuição de acertos (backtest)
    dist_datasets = []
    for i, b in enumerate(backtest):
        dist_datasets.append({
            "label": METODO_LABELS.get(b["metodo"], b["metodo"]),
            "data": [b["dist"].get(str(k), 0) for k in range(6, 14)],
            "color": CORES[i % len(CORES)],
        })
    svg_dist = svg_bar_chart(dist_datasets, [str(k) for k in range(6, 14)], width=540, height=250)
    svg_media = svg_media_chart(backtest, width=540, height=250)

    # Heatmap e barras de atraso
    heatmap_html = render_heatmap(freq_list)
    atraso_html = render_atraso_bars(freq_list)

    # Estatísticas das dezenas
    mais_freq = max(freq_list, key=lambda x: x["pct"])
    maior_atraso = max(freq_list, key=lambda x: x["atraso"])

    # Conteúdo das abas
    jogos_html = render_jogos_html(jogos)
    conf_html = render_conferencia_html(conferencias)
    bt_stats = render_backtest_stats(backtest)
    bt_table = render_backtest_table(backtest)
    hist_table = render_historico_table(ultimos_resultados)
    n_backtest = backtest[0]["n"] if backtest else 0

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lotofácil Lab — Jogos & Conferências</title>
<style>
  :root {{
    --bg: #0d1117; --card: #161b22; --card2: #1c2230; --border: #30363d;
    --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff; --green: #3fb950;
    --yellow: #d29922; --red: #f85149; --purple: #a78bfa; --orange: #f0883e;
    --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: var(--font); font-size: 14px; line-height: 1.5; }}

  .header {{ background: linear-gradient(135deg, #161b22 0%, #1c2230 100%); border-bottom: 1px solid var(--border); padding: 20px 28px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }}
  .header-left h1 {{ font-size: 20px; font-weight: 700; }}
  .header-left h1 span {{ color: var(--accent); }}
  .header-left .sub {{ color: var(--muted); font-size: 12px; margin-top: 3px; }}
  .badge {{ background: rgba(240,136,62,.15); color: var(--orange); border: 1px solid rgba(240,136,62,.3); border-radius: 6px; padding: 4px 10px; font-size: 11px; font-weight: 600; }}

  .tabs {{ display: flex; border-bottom: 1px solid var(--border); padding: 0 28px; background: var(--card); overflow-x: auto; }}
  .tab {{ padding: 12px 18px; font-size: 13px; font-weight: 500; color: var(--muted); cursor: pointer; border-bottom: 2px solid transparent; white-space: nowrap; transition: color .2s, border-color .2s; user-select: none; }}
  .tab:hover {{ color: var(--text); }}
  .tab.active {{ color: var(--accent); border-bottom-color: var(--accent); }}

  .page {{ display: none; padding: 24px 28px; max-width: 1200px; margin: 0 auto; }}
  .page.active {{ display: block; }}

  .card {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 18px; }}
  .card-title {{ font-size: 12px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin-bottom: 14px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  @media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

  .stat-row {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }}
  .stat-box {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 14px 18px; flex: 1; min-width: 130px; }}
  .stat-box .label {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }}
  .stat-box .value {{ font-size: 24px; font-weight: 700; margin-top: 4px; }}
  .stat-box .hint {{ font-size: 11px; color: var(--muted); margin-top: 2px; }}

  .jogo-card {{ background: var(--card2); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-bottom: 12px; }}
  .jogo-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }}
  .metodo-badge {{ font-size: 12px; font-weight: 600; padding: 3px 10px; border-radius: 20px; }}
  .m1 {{ background: rgba(88,166,255,.15); color: #58a6ff; border: 1px solid rgba(88,166,255,.3); }}
  .m2 {{ background: rgba(63,185,80,.15); color: #3fb950; border: 1px solid rgba(63,185,80,.3); }}
  .m3 {{ background: rgba(210,153,34,.15); color: #d29922; border: 1px solid rgba(210,153,34,.3); }}
  .m4 {{ background: rgba(248,81,73,.15); color: #f85149; border: 1px solid rgba(248,81,73,.3); }}
  .m5 {{ background: rgba(167,139,250,.15); color: #a78bfa; border: 1px solid rgba(167,139,250,.3); }}
  .jogo-meta {{ font-size: 11px; color: var(--muted); display: flex; gap: 14px; }}
  .dezenas-grid {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .bola {{ width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 700; border: 2px solid; }}
  .bola-normal {{ background: rgba(255,255,255,.06); border-color: var(--border); color: var(--text); }}
  .bola-acerto {{ background: rgba(63,185,80,.2); border-color: #3fb950; color: #3fb950; }}
  .bola-erro {{ background: rgba(248,81,73,.08); border-color: rgba(248,81,73,.2); color: #8b949e; }}
  .bola-sorteada {{ background: rgba(88,166,255,.2); border-color: #58a6ff; color: #58a6ff; }}

  .acertos-badge {{ font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 20px; }}
  .ac-low {{ background: rgba(248,81,73,.15); color: #f85149; border: 1px solid rgba(248,81,73,.3); }}
  .ac-mid {{ background: rgba(210,153,34,.15); color: #d29922; border: 1px solid rgba(210,153,34,.3); }}
  .ac-good {{ background: rgba(63,185,80,.15); color: #3fb950; border: 1px solid rgba(63,185,80,.3); }}
  .ac-great {{ background: rgba(88,166,255,.15); color: #58a6ff; border: 1px solid rgba(88,166,255,.3); }}

  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--border); color: var(--muted); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid rgba(48,54,61,.5); }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: rgba(255,255,255,.02); }}

  .heatmap {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }}
  .hm-cell {{ border-radius: 8px; padding: 10px 6px; text-align: center; border: 1px solid; }}
  .hm-num {{ font-size: 15px; font-weight: 700; }}
  .hm-pct {{ font-size: 10px; color: var(--muted); margin-top: 2px; }}
  .hm-atraso {{ font-size: 10px; margin-top: 2px; }}

  .concurso-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }}
  .concurso-num {{ font-size: 22px; font-weight: 700; color: var(--accent); }}
  .concurso-data {{ font-size: 13px; color: var(--muted); }}

  .disclaimer {{ background: rgba(210,153,34,.08); border: 1px solid rgba(210,153,34,.25); border-radius: 8px; padding: 12px 16px; font-size: 12px; color: var(--muted); margin-bottom: 20px; line-height: 1.6; }}
  .disclaimer b {{ color: var(--yellow); }}

  .empty {{ text-align: center; padding: 48px 24px; color: var(--muted); }}
  .empty .icon {{ font-size: 40px; margin-bottom: 12px; }}
  .empty p {{ font-size: 13px; }}

  .svg-wrap {{ overflow-x: auto; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <h1>Lotofácil <span>Lab</span> — Jogos & Conferências</h1>
    <div class="sub">Laboratório Estatístico Educativo · Atualizado em {ultima_atualizacao}</div>
  </div>
  <div class="badge">⚠ Apenas estudo estatístico — não é recomendação de aposta</div>
</div>

<div class="tabs">
  <div class="tab active" onclick="showTab('jogos')">🎯 Jogos Gerados</div>
  <div class="tab" onclick="showTab('conferencia')">✅ Conferências</div>
  <div class="tab" onclick="showTab('backtest')">📊 Backtest</div>
  <div class="tab" onclick="showTab('dezenas')">🔥 Dezenas</div>
  <div class="tab" onclick="showTab('historico')">📋 Histórico</div>
</div>

<!-- PAGE: JOGOS -->
<div class="page active" id="page-jogos">
  <div class="disclaimer">
    <b>Lembrete educativo:</b> Os jogos abaixo são gerados por 5 métodos estatísticos diferentes para fins de estudo comparativo.
    Nenhum método é "melhor" ou "mais perto de acertar" — todos convergem para a média teórica de <b>9 acertos</b> no longo prazo.
  </div>
  {jogos_html}
</div>

<!-- PAGE: CONFERENCIAS -->
<div class="page" id="page-conferencia">
  {conf_html}
</div>

<!-- PAGE: BACKTEST -->
<div class="page" id="page-backtest">
  <div class="disclaimer">
    <b>Backtest em {n_backtest:,} concursos reais:</b> Simulação retroativa de todos os métodos no histórico completo.
    A diferença entre as médias e a esperança teórica (9.0) é estatisticamente insignificante — confirmando que nenhum método tem vantagem preditiva.
  </div>
  <div class="stat-row">
    {bt_stats}
  </div>
  <div class="grid-2" style="margin-top:4px;">
    <div class="card">
      <div class="card-title">Distribuição de Acertos por Método (faixa 6–13)</div>
      <div class="svg-wrap">{svg_dist}</div>
    </div>
    <div class="card">
      <div class="card-title">Média de Acertos vs. Esperança Teórica (9.0)</div>
      <div class="svg-wrap">{svg_media}</div>
    </div>
  </div>
  <div class="card" style="margin-top:16px;">
    <div class="card-title">Tabela Comparativa dos Métodos</div>
    <table>
      <thead><tr>
        <th>Método</th><th>Concursos</th><th>Média</th><th>Desvio</th>
        <th>Dif. Esperança</th><th>% 11+</th><th>% 13+</th><th>% 14+</th><th>% 15</th>
      </tr></thead>
      <tbody>{bt_table}</tbody>
    </table>
  </div>
</div>

<!-- PAGE: DEZENAS -->
<div class="page" id="page-dezenas">
  <div class="stat-row">
    <div class="stat-box"><div class="label">Total Concursos</div><div class="value" style="color:var(--accent)">3.725</div><div class="hint">histórico completo</div></div>
    <div class="stat-box"><div class="label">Freq. Teórica</div><div class="value" style="color:var(--green)">60%</div><div class="hint">15/25 dezenas por sorteio</div></div>
    <div class="stat-box"><div class="label">Mais Frequente</div><div class="value" style="color:var(--yellow)">{mais_freq["d"]}</div><div class="hint">{mais_freq["pct"]}% ({mais_freq["abs"]}x)</div></div>
    <div class="stat-box"><div class="label">Maior Atraso</div><div class="value" style="color:var(--red)">{maior_atraso["d"]}</div><div class="hint">{maior_atraso["atraso"]} concurso(s)</div></div>
  </div>
  <div class="card" style="margin-bottom:16px;">
    <div class="card-title">Mapa de Calor — Frequência das Dezenas (% de aparições)</div>
    <div class="heatmap">{heatmap_html}</div>
  </div>
  <div class="card">
    <div class="card-title">Atraso Atual (concursos sem sair)</div>
    {atraso_html}
  </div>
</div>

<!-- PAGE: HISTORICO -->
<div class="page" id="page-historico">
  <div class="card">
    <div class="card-title">Últimos 15 Concursos Registrados</div>
    <table>
      <thead><tr><th>Concurso</th><th>Data</th><th>Dezenas Sorteadas</th><th>Soma</th><th>Pares</th></tr></thead>
      <tbody>{hist_table}</tbody>
    </table>
  </div>
</div>

<script>
function showTab(name) {{
  var tabs = document.querySelectorAll('.tab');
  var names = ['jogos','conferencia','backtest','dezenas','historico'];
  tabs.forEach(function(t, i) {{ t.classList.toggle('active', names[i] === name); }});
  document.querySelectorAll('.page').forEach(function(p) {{ p.classList.remove('active'); }});
  document.getElementById('page-' + name).classList.add('active');
}}
</script>
</body>
</html>"""


def main():
    jogos = lib.carregar_jogos()
    conferencias = lib.carregar_conferencias()

    # Backtest
    backtest = []
    sim_csv = os.path.join(lib.DADOS_DIR, "estatisticas_simulacao.csv")
    if os.path.exists(sim_csv):
        with open(sim_csv, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                dist = {str(k): int(row[f"qtd_{k}_acertos"]) for k in range(16)}
                backtest.append({
                    "metodo": row["metodo"],
                    "n": int(row["total_concursos_simulados"]),
                    "media": float(row["media_acertos"]),
                    "desvio": float(row["desvio_padrao_acertos"]),
                    "dif": float(row["diferenca_vs_esperanca"]),
                    "pct_11": float(row["pct_11_ou_mais"]),
                    "pct_13": float(row["pct_13_ou_mais"]),
                    "pct_14": float(row["pct_14_ou_mais"]),
                    "pct_15": float(row["pct_15"]),
                    "dist": dist,
                })

    # Frequência
    freq_list = []
    with open(lib.FREQUENCIA_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            freq_list.append({
                "d": row["dezena"],
                "pct": float(row["frequencia_pct"]),
                "abs": int(row["frequencia_absoluta"]),
                "atraso": int(row["atraso_atual"]),
            })

    ultimos = carregar_ultimos_resultados(15)
    ultima_atualizacao = datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M")

    html = build_html(jogos, conferencias, backtest, freq_list, ultimos, ultima_atualizacao)

    with open(PAINEL_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Painel de jogos criado em: {PAINEL_PATH}")


if __name__ == "__main__":
    main()
