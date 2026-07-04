"""
Gera painel_jogos.html: painel visual avançado de jogos e conferências.
Inspirado na planilha Lotocerta, com estilo dark/elegante.

Seções:
  - Aba 🎯 Jogos: moldura, miolo, desdobramento dos 5 métodos
  - Aba ✅ Conferidor: conferidor visual com acertos destacados + desempenho + financeiro
  - Aba 📊 Backtest: gráficos SVG + tabela comparativa
  - Aba 🔥 Dezenas: mapa de calor + ranking de atraso
  - Aba 📋 Histórico: últimos 15 concursos

Uso:
    python3 gerar_painel_jogos.py
"""
import csv, os, json
from datetime import datetime, timezone, timedelta
import lotofacil_lib as lib

PAINEL_PATH = os.path.join(lib.BASE_DIR, "painel_jogos.html")
BRASILIA = timezone(timedelta(hours=-3))

CORES = ["#58a6ff", "#3fb950", "#d29922", "#f85149", "#a78bfa"]
METODO_LABELS = {
    "M1_aleatorio_puro":      "M1 Aleatório",
    "M2_mais_frequentes":     "M2 Mais Freq.",
    "M3_mais_atrasadas":      "M3 Mais Atras.",
    "M4_par_impar_balanceado":"M4 Par/Ímpar",
    "M5_soma_faixa_comum":    "M5 Soma Faixa",
}
METODO_CLASS = {
    "M1_aleatorio_puro":      "m1",
    "M2_mais_frequentes":     "m2",
    "M3_mais_atrasadas":      "m3",
    "M4_par_impar_balanceado":"m4",
    "M5_soma_faixa_comum":    "m5",
}
PREMIOS = {11: 6.00, 12: 10.00, 13: 25.00, 14: 1500.00, 15: 1_630_000.00}


# ─────────────────────────────────────────────
# SVG helpers
# ─────────────────────────────────────────────
def svg_bar_chart(datasets, labels, width=520, height=240):
    pad_l, pad_r, pad_t, pad_b = 48, 16, 28, 36
    cw = width - pad_l - pad_r
    ch = height - pad_t - pad_b
    n_g = len(labels); n_s = len(datasets)
    bar_w = max(4, (cw / n_g - 4) / n_s)
    all_v = [v for ds in datasets for v in ds["data"]]
    max_v = max(all_v) if all_v else 1
    ticks = 5
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" style="overflow:visible">']
    for i in range(ticks + 1):
        y = pad_t + ch - (i / ticks) * ch
        svg.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l+cw}" y2="{y:.1f}" stroke="#30363d" stroke-width="1"/>')
        svg.append(f'<text x="{pad_l-5}" y="{y+4:.1f}" text-anchor="end" fill="#8b949e" font-size="10">{int(i*max_v/ticks)}</text>')
    for gi, label in enumerate(labels):
        gx = pad_l + gi * (cw / n_g)
        for si, ds in enumerate(datasets):
            val = ds["data"][gi] if gi < len(ds["data"]) else 0
            bh = (val / max_v) * ch if max_v else 0
            bx = gx + si * bar_w + 2
            by = pad_t + ch - bh
            c = ds.get("color", CORES[si % len(CORES)])
            svg.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w:.1f}" height="{bh:.1f}" fill="{c}99" stroke="{c}" stroke-width="1" rx="2"/>')
        lx = gx + (bar_w * n_s) / 2
        svg.append(f'<text x="{lx:.1f}" y="{pad_t+ch+15}" text-anchor="middle" fill="#8b949e" font-size="10">{label}</text>')
    svg.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t+ch}" stroke="#30363d" stroke-width="1.5"/>')
    svg.append(f'<line x1="{pad_l}" y1="{pad_t+ch}" x2="{pad_l+cw}" y2="{pad_t+ch}" stroke="#30363d" stroke-width="1.5"/>')
    lx = pad_l
    ly = height - 6
    for si, ds in enumerate(datasets):
        c = ds.get("color", CORES[si % len(CORES)])
        svg.append(f'<rect x="{lx}" y="{ly-8}" width="10" height="10" fill="{c}99" stroke="{c}" rx="2"/>')
        svg.append(f'<text x="{lx+13}" y="{ly}" fill="#8b949e" font-size="10">{ds["label"]}</text>')
        lx += len(ds["label"]) * 6.5 + 20
    svg.append('</svg>')
    return "\n".join(svg)


def svg_media_chart(backtest, width=520, height=240):
    pad_l, pad_r, pad_t, pad_b = 128, 16, 16, 20
    cw = width - pad_l - pad_r
    ch = height - pad_t - pad_b
    n = len(backtest)
    bh = ch / n - 8
    mn, mx = 8.85, 9.15
    esp = lib.ESPERANCA_TEORICA
    def xp(v): return pad_l + (v - mn) / (mx - mn) * cw
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">']
    for tick in [8.9, 8.95, 9.0, 9.05, 9.1]:
        x = xp(tick)
        c = "#58a6ff" if tick == 9.0 else "#30363d"
        svg.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{pad_t+ch}" stroke="{c}" stroke-width="1" stroke-dasharray="{"0" if tick==9.0 else "4,3"}"/>')
        svg.append(f'<text x="{x:.1f}" y="{pad_t+ch+13}" text-anchor="middle" fill="#8b949e" font-size="9">{tick}</text>')
    for i, b in enumerate(backtest):
        by = pad_t + i * (ch / n) + 4
        label = METODO_LABELS.get(b["metodo"], b["metodo"])
        c = CORES[i % len(CORES)]
        media = b["media"]
        bx = xp(min(media, esp))
        bw = max(abs(xp(media) - xp(esp)), 2)
        svg.append(f'<text x="{pad_l-5}" y="{by+bh/2+4:.1f}" text-anchor="end" fill="{c}" font-size="11" font-weight="600">{label}</text>')
        svg.append(f'<rect x="{pad_l}" y="{by:.1f}" width="{cw}" height="{bh:.1f}" fill="#ffffff08" rx="4"/>')
        svg.append(f'<rect x="{bx:.1f}" y="{by+2:.1f}" width="{bw:.1f}" height="{bh-4:.1f}" fill="{c}99" stroke="{c}" stroke-width="1" rx="3"/>')
        vx = xp(media) + (5 if media >= esp else -5)
        anchor = "start" if media >= esp else "end"
        svg.append(f'<text x="{vx:.1f}" y="{by+bh/2+4:.1f}" text-anchor="{anchor}" fill="{c}" font-size="11" font-weight="700">{media:.4f}</text>')
    ex = xp(esp)
    svg.append(f'<line x1="{ex:.1f}" y1="{pad_t}" x2="{ex:.1f}" y2="{pad_t+ch}" stroke="#58a6ff" stroke-width="2"/>')
    svg.append(f'<text x="{ex+4:.1f}" y="{pad_t+11}" fill="#58a6ff" font-size="10">E=9.0</text>')
    svg.append('</svg>')
    return "\n".join(svg)


# ─────────────────────────────────────────────
# Helpers de renderização
# ─────────────────────────────────────────────
def bola(num, cls="bola-normal"):
    return f'<div class="bola {cls}">{num:02d}</div>'


def render_heatmap(freq_list):
    pcts = [f["pct"] for f in freq_list]
    mn, mx = min(pcts), max(pcts)
    cells = []
    for f in freq_list:
        t = (f["pct"] - mn) / (mx - mn) if mx > mn else 0.5
        r = int(t * 200); g = int(100 + t * 100); b = int(255 - t * 200)
        bg = f"rgba({r},{g},{b},0.18)"; border = f"rgba({r},{g},{b},0.45)"
        ac = "#3fb950" if f["atraso"] == 0 else ("#d29922" if f["atraso"] <= 2 else "#f85149")
        cells.append(f'''<div class="hm-cell" style="background:{bg};border-color:{border}">
          <div class="hm-num">{f["d"]:02d}</div>
          <div class="hm-pct">{f["pct"]}%</div>
          <div class="hm-atraso" style="color:{ac}">atr:{f["atraso"]}</div>
        </div>''')
    return "\n".join(cells)


def render_atraso_bars(freq_list):
    sl = sorted(freq_list, key=lambda x: x["atraso"], reverse=True)
    mx = max(f["atraso"] for f in sl) or 1
    bars = []
    for f in sl:
        pct = f["atraso"] / mx * 100
        c = "#3fb950" if f["atraso"] == 0 else ("#d29922" if f["atraso"] <= 2 else "#f85149")
        bars.append(f'''<div style="display:flex;align-items:center;gap:10px;margin-bottom:7px">
          <span style="width:28px;text-align:center;font-weight:700;color:{c};font-size:13px">{f["d"]:02d}</span>
          <div style="flex:1;height:7px;background:#30363d;border-radius:4px;overflow:hidden">
            <div style="width:{pct:.1f}%;height:100%;background:{c};border-radius:4px"></div>
          </div>
          <span style="width:65px;font-size:12px;color:#8b949e">{f["atraso"]} conc.</span>
        </div>''')
    return "\n".join(bars)


# ─────────────────────────────────────────────
# ABA JOGOS — Moldura + Miolo + Desdobramento
# ─────────────────────────────────────────────
def render_aba_jogos(jogos, freq_list):
    if not jogos:
        return '<div class="empty"><div class="icon">🎯</div><p>Nenhum jogo gerado ainda.</p></div>'

    # Agrupa por concurso
    concursos = {}
    for j in jogos:
        c = j["concurso_alvo"]
        if c not in concursos:
            concursos[c] = {"data": j["data_geracao"], "jogos": []}
        concursos[c]["jogos"].append(j)

    # Frequência para destacar dezenas quentes/frias
    freq_map = {f["d"]: f for f in freq_list}
    top5_freq = sorted(freq_list, key=lambda x: x["pct"], reverse=True)[:5]
    top5_atraso = sorted(freq_list, key=lambda x: x["atraso"], reverse=True)[:5]
    hot_nums = {f["d"] for f in top5_freq}
    cold_nums = {f["d"] for f in top5_atraso}

    html = []
    for c in sorted(concursos.keys(), reverse=True):
        info = concursos[c]
        html.append(f'''
        <div class="section-title">
          <span class="concurso-num">Concurso #{c}</span>
          <span class="concurso-data">Gerado em {info["data"]}</span>
          <span class="badge-info">Próximo sorteio</span>
        </div>

        <!-- LEGENDA DE CORES -->
        <div class="legenda-row">
          <div class="leg-item"><span class="bola bola-quente" style="width:22px;height:22px;font-size:10px">01</span> Mais frequente (top 5)</div>
          <div class="leg-item"><span class="bola bola-atrasada" style="width:22px;height:22px;font-size:10px">01</span> Maior atraso (top 5)</div>
          <div class="leg-item"><span class="bola bola-normal" style="width:22px;height:22px;font-size:10px">01</span> Normal</div>
        </div>

        <!-- MOLDURA / MIOLO -->
        <div class="grid-2" style="margin-bottom:20px">
          <div class="card">
            <div class="card-title">🔲 Moldura (dezenas da borda 01–25)</div>
            <div class="moldura-grid">
              {render_moldura(hot_nums, cold_nums)}
            </div>
            <div style="margin-top:10px;font-size:11px;color:#8b949e">
              As 16 dezenas da borda do volante. Estratégia: escolha 2 para excluir do seu jogo.
            </div>
          </div>
          <div class="card">
            <div class="card-title">🔵 Miolo (dezenas internas)</div>
            <div class="miolo-grid">
              {render_miolo(hot_nums, cold_nums)}
            </div>
            <div style="margin-top:10px;font-size:11px;color:#8b949e">
              As 9 dezenas do centro do volante. Estratégia: inclua pelo menos 6 no seu jogo.
            </div>
          </div>
        </div>

        <!-- DESDOBRAMENTO DOS MÉTODOS -->
        <div class="card" style="margin-bottom:20px">
          <div class="card-title">📋 Desdobramento — 5 Métodos × 15 Dezenas</div>
          <div class="table-scroll">
            <table class="desd-table">
              <thead>
                <tr>
                  <th>Jogo</th><th>Método</th>
                  {" ".join(f"<th>{i:02d}</th>" for i in range(1,16))}
                  <th>Soma</th><th>P</th><th>Í</th>
                </tr>
              </thead>
              <tbody>
                {render_desdobramento(info["jogos"], hot_nums, cold_nums)}
              </tbody>
            </table>
          </div>
        </div>
        ''')
    return "\n".join(html)


def render_moldura(hot, cold):
    # Moldura: linha de cima (01-05), lados (06,11,16,21 | 10,15,20,25), linha de baixo (21-25)
    # Representação visual 5x5 do volante — borda = moldura
    volante = [
        [1,  2,  3,  4,  5],
        [6,  7,  8,  9,  10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20],
        [21, 22, 23, 24, 25],
    ]
    borda = {1,2,3,4,5,6,10,11,15,16,20,21,22,23,24,25}
    rows = []
    for row in volante:
        cells = []
        for d in row:
            if d in borda:
                cls = "bola-quente" if d in hot else ("bola-atrasada" if d in cold else "bola-moldura")
            else:
                cls = "bola-miolo-off"
            cells.append(f'<div class="bola {cls}" style="width:36px;height:36px;font-size:13px">{d:02d}</div>')
        rows.append(f'<div style="display:flex;gap:5px;justify-content:center">' + "".join(cells) + '</div>')
    return "\n".join(rows)


def render_miolo(hot, cold):
    volante = [
        [1,  2,  3,  4,  5],
        [6,  7,  8,  9,  10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20],
        [21, 22, 23, 24, 25],
    ]
    miolo = {7,8,9,12,13,14,17,18,19}
    rows = []
    for row in volante:
        cells = []
        for d in row:
            if d in miolo:
                cls = "bola-quente" if d in hot else ("bola-atrasada" if d in cold else "bola-miolo")
            else:
                cls = "bola-moldura-off"
            cells.append(f'<div class="bola {cls}" style="width:36px;height:36px;font-size:13px">{d:02d}</div>')
        rows.append(f'<div style="display:flex;gap:5px;justify-content:center">' + "".join(cells) + '</div>')
    return "\n".join(rows)


def render_desdobramento(jogos, hot, cold):
    rows = []
    for i, j in enumerate(jogos, 1):
        label = METODO_LABELS.get(j["metodo"], j["metodo"])
        cls = METODO_CLASS.get(j["metodo"], "m1")
        dezenas = [int(d) for d in j["dezenas"].split("-")]
        cells = []
        for d in dezenas:
            bc = "td-quente" if d in hot else ("td-atrasada" if d in cold else "")
            cells.append(f'<td class="{bc}"><b>{d:02d}</b></td>')
        rows.append(f'''<tr>
          <td><b style="color:#8b949e">{i}</b></td>
          <td><span class="metodo-badge {cls}">{label}</span></td>
          {"".join(cells)}
          <td><b>{j["soma"]}</b></td>
          <td>{j["pares"]}</td>
          <td>{j["impares"]}</td>
        </tr>''')
    return "\n".join(rows)


# ─────────────────────────────────────────────
# ABA CONFERIDOR — Conferência + Desempenho + Financeiro
# ─────────────────────────────────────────────
def render_aba_conferidor(conferencias):
    if not conferencias:
        return '''<div class="empty">
          <div class="icon">⏳</div>
          <p>Nenhuma conferência registrada ainda.</p>
          <p style="margin-top:8px;font-size:12px;color:#8b949e">
            As conferências aparecem aqui após o sorteio do concurso alvo.<br>
            O ciclo diário roda às 22h e captura o resultado da noite.
          </p>
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

        # Dezenas sorteadas
        bolas_sort = "".join(bola(d, "bola-sorteada") for d in sorted(sorteadas))

        # Conferidor visual (tabela estilo planilha)
        conf_rows = []
        acertos_list = []
        for j in info["jogos"]:
            label = METODO_LABELS.get(j["metodo"], j["metodo"])
            cls = METODO_CLASS.get(j["metodo"], "m1")
            ac = j["acertos"]
            acertos_list.append(ac)
            ac_cls = "ac-low" if ac < 9 else ("ac-mid" if ac < 11 else ("ac-good" if ac < 13 else "ac-great"))
            cells = "".join(
                f'<td class="{"td-acerto" if d in sorteadas else "td-erro"}"><b>{d:02d}</b></td>'
                for d in j["dezenas"]
            )
            conf_rows.append(f'''<tr>
              <td><span class="metodo-badge {cls}">{label}</span></td>
              {cells}
              <td><span class="acertos-badge {ac_cls}">{ac}</span></td>
            </tr>''')

        # Desempenho
        desemp_html = render_desempenho(info["jogos"])

        # Financeiro
        financeiro_html = render_financeiro(info["jogos"])

        html.append(f'''
        <div class="section-title">
          <span class="concurso-num">Concurso #{c}</span>
          <span class="concurso-data">Sorteado em {info["data"]}</span>
        </div>

        <!-- DEZENAS SORTEADAS -->
        <div class="card" style="margin-bottom:16px">
          <div class="card-title">🎰 Dezenas Sorteadas no Concurso #{c}</div>
          <div class="dezenas-grid" style="gap:8px">{bolas_sort}</div>
        </div>

        <!-- CONFERIDOR VISUAL -->
        <div class="card" style="margin-bottom:16px">
          <div class="card-title">🔍 Conferidor — Acertos por Método</div>
          <div class="table-scroll">
            <table class="conf-table">
              <thead>
                <tr>
                  <th>Método</th>
                  {" ".join(f"<th>D{i:02d}</th>" for i in range(1,16))}
                  <th>Acertos</th>
                </tr>
              </thead>
              <tbody>{"".join(conf_rows)}</tbody>
            </table>
          </div>
        </div>

        <!-- DESEMPENHO + FINANCEIRO -->
        <div class="grid-2" style="margin-bottom:28px">
          {desemp_html}
          {financeiro_html}
        </div>
        ''')
    return "\n".join(html)


def render_desempenho(jogos):
    faixas = {11: 0, 12: 0, 13: 0, 14: 0, 15: 0}
    for j in jogos:
        ac = j["acertos"]
        if ac >= 11:
            faixas[11] += 1
        if ac >= 12:
            faixas[12] += 1
        if ac >= 13:
            faixas[13] += 1
        if ac >= 14:
            faixas[14] += 1
        if ac >= 15:
            faixas[15] += 1

    acertos_vals = [j["acertos"] for j in jogos]
    media = sum(acertos_vals) / len(acertos_vals) if acertos_vals else 0

    rows = []
    for pts, qtd in faixas.items():
        c = "#3fb950" if qtd > 0 else "#8b949e"
        rows.append(f'''<tr>
          <td><b style="color:#58a6ff">{pts} pontos</b></td>
          <td><span style="color:{c};font-weight:700;font-size:16px">{qtd}</span></td>
        </tr>''')

    return f'''<div class="card">
      <div class="card-title">📈 Desempenho do Concurso</div>
      <div style="display:flex;gap:20px;margin-bottom:14px;flex-wrap:wrap">
        <div class="stat-mini"><div class="label">Média de Acertos</div><div class="value" style="color:#58a6ff">{media:.1f}</div></div>
        <div class="stat-mini"><div class="label">Melhor Resultado</div><div class="value" style="color:#3fb950">{max(acertos_vals) if acertos_vals else 0}</div></div>
        <div class="stat-mini"><div class="label">Jogos Conferidos</div><div class="value" style="color:#d29922">{len(jogos)}</div></div>
      </div>
      <table>
        <thead><tr><th>Faixa</th><th>Qtd. Jogos</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>'''


def render_financeiro(jogos):
    investimento = len(jogos) * 3.00  # R$ 3,00 por jogo simples
    ganho = 0.0
    ganhos_detail = []
    for j in jogos:
        ac = j["acertos"]
        premio = PREMIOS.get(ac, 0)
        if premio > 0:
            ganho += premio
            label = METODO_LABELS.get(j["metodo"], j["metodo"])
            ganhos_detail.append(f'<div style="font-size:11px;color:#3fb950;margin-top:4px">+ R$ {premio:,.2f} ({label})</div>')
    lucro = ganho - investimento
    lucro_color = "#3fb950" if lucro >= 0 else "#f85149"
    lucro_label = "LUCRO" if lucro >= 0 else "PREJUÍZO"

    premios_rows = "".join(
        f'<tr><td><b style="color:#58a6ff">{pts} pontos</b></td><td>R$ {val:,.2f}</td></tr>'
        for pts, val in PREMIOS.items()
    )

    return f'''<div class="card">
      <div class="card-title">💰 Resumo Financeiro</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">
        <div class="stat-mini"><div class="label">Investimento</div><div class="value" style="color:#d29922">R$ {investimento:.2f}</div></div>
        <div class="stat-mini"><div class="label">Total Ganho</div><div class="value" style="color:#3fb950">R$ {ganho:,.2f}</div></div>
        <div class="stat-mini" style="grid-column:1/-1;background:rgba({("63,185,80" if lucro >= 0 else "248,81,73")},.08);border-color:rgba({("63,185,80" if lucro >= 0 else "248,81,73")},.3)">
          <div class="label">{lucro_label}</div>
          <div class="value" style="color:{lucro_color};font-size:22px">R$ {abs(lucro):,.2f}</div>
        </div>
      </div>
      {"".join(ganhos_detail) if ganhos_detail else '<div style="font-size:12px;color:#8b949e;margin-bottom:12px">Nenhum prêmio neste concurso.</div>'}
      <div class="card-title" style="margin-top:12px">Tabela de Prêmios</div>
      <table>
        <thead><tr><th>Faixa</th><th>Prêmio Aprox.</th></tr></thead>
        <tbody>{premios_rows}</tbody>
      </table>
    </div>'''


# ─────────────────────────────────────────────
# ABA BACKTEST
# ─────────────────────────────────────────────
def render_aba_backtest(backtest):
    dist_datasets = []
    for i, b in enumerate(backtest):
        dist_datasets.append({
            "label": METODO_LABELS.get(b["metodo"], b["metodo"]),
            "data": [b["dist"].get(str(k), 0) for k in range(6, 14)],
            "color": CORES[i % len(CORES)],
        })
    svg_dist = svg_bar_chart(dist_datasets, [str(k) for k in range(6, 14)])
    svg_med = svg_media_chart(backtest)

    boxes = []
    for i, b in enumerate(backtest):
        label = METODO_LABELS.get(b["metodo"], b["metodo"])
        c = CORES[i % len(CORES)]
        dif = b["dif"]
        ds = f"+{dif:.4f}" if dif >= 0 else f"{dif:.4f}"
        dc = "#3fb950" if abs(dif) < 0.05 else "#d29922"
        boxes.append(f'''<div class="stat-box" style="border-top:3px solid {c}">
          <div class="label">{label.upper()}</div>
          <div class="value" style="color:{c};font-size:20px">{b["media"]:.4f}</div>
          <div class="hint" style="color:{dc}">Dif: {ds} vs esperança</div>
        </div>''')

    table_rows = []
    for i, b in enumerate(backtest):
        label = METODO_LABELS.get(b["metodo"], b["metodo"])
        cls = METODO_CLASS.get(b["metodo"], "m1")
        dif = b["dif"]
        ds = f"+{dif:.4f}" if dif >= 0 else f"{dif:.4f}"
        dc = "#3fb950" if abs(dif) < 0.05 else "#d29922"
        table_rows.append(f'''<tr>
          <td><span class="metodo-badge {cls}">{label}</span></td>
          <td>{b["n"]:,}</td><td><b>{b["media"]:.4f}</b></td><td>{b["desvio"]:.4f}</td>
          <td style="color:{dc};font-weight:600">{ds}</td>
          <td>{b["pct_11"]}%</td><td>{b["pct_13"]}%</td><td>{b["pct_14"]}%</td><td>{b["pct_15"]}%</td>
        </tr>''')

    n = backtest[0]["n"] if backtest else 0
    return f'''
    <div class="disclaimer">
      <b>Backtest em {n:,} concursos reais:</b> Simulação retroativa de todos os métodos no histórico completo.
      A diferença entre as médias e a esperança teórica (9.0) é estatisticamente insignificante — confirmando que nenhum método tem vantagem preditiva.
    </div>
    <div class="stat-row">{"".join(boxes)}</div>
    <div class="grid-2" style="margin-top:4px">
      <div class="card">
        <div class="card-title">Distribuição de Acertos por Método (faixa 6–13)</div>
        <div class="svg-wrap">{svg_dist}</div>
      </div>
      <div class="card">
        <div class="card-title">Média de Acertos vs. Esperança Teórica (9.0)</div>
        <div class="svg-wrap">{svg_med}</div>
      </div>
    </div>
    <div class="card" style="margin-top:16px">
      <div class="card-title">Tabela Comparativa dos Métodos</div>
      <table>
        <thead><tr><th>Método</th><th>Concursos</th><th>Média</th><th>Desvio</th>
        <th>Dif. Esperança</th><th>% 11+</th><th>% 13+</th><th>% 14+</th><th>% 15</th></tr></thead>
        <tbody>{"".join(table_rows)}</tbody>
      </table>
    </div>'''


# ─────────────────────────────────────────────
# ABA DEZENAS
# ─────────────────────────────────────────────
def render_aba_dezenas(freq_list):
    mais_freq = max(freq_list, key=lambda x: x["pct"])
    maior_atraso = max(freq_list, key=lambda x: x["atraso"])
    heatmap = render_heatmap(freq_list)
    atraso_bars = render_atraso_bars(freq_list)

    # Top 5 mais frequentes
    top5f = sorted(freq_list, key=lambda x: x["pct"], reverse=True)[:5]
    top5a = sorted(freq_list, key=lambda x: x["atraso"], reverse=True)[:5]
    top5f_html = "".join(f'<div class="bola bola-quente" style="width:38px;height:38px;font-size:14px">{f["d"]:02d}</div>' for f in top5f)
    top5a_html = "".join(f'<div class="bola bola-atrasada" style="width:38px;height:38px;font-size:14px">{f["d"]:02d}</div>' for f in top5a)

    return f'''
    <div class="stat-row">
      <div class="stat-box"><div class="label">Total Concursos</div><div class="value" style="color:var(--accent)">3.725</div><div class="hint">histórico completo</div></div>
      <div class="stat-box"><div class="label">Freq. Teórica</div><div class="value" style="color:var(--green)">60%</div><div class="hint">15/25 dezenas por sorteio</div></div>
      <div class="stat-box"><div class="label">Mais Frequente</div><div class="value" style="color:var(--yellow)">{mais_freq["d"]:02d}</div><div class="hint">{mais_freq["pct"]}% ({mais_freq["abs"]}x)</div></div>
      <div class="stat-box"><div class="label">Maior Atraso</div><div class="value" style="color:var(--red)">{maior_atraso["d"]:02d}</div><div class="hint">{maior_atraso["atraso"]} concurso(s)</div></div>
    </div>

    <div class="grid-2" style="margin-bottom:16px">
      <div class="card">
        <div class="card-title">🔥 Top 5 Mais Frequentes</div>
        <div class="dezenas-grid" style="gap:8px">{top5f_html}</div>
        <div style="margin-top:10px;font-size:11px;color:#8b949e">Dezenas que mais saíram no histórico completo</div>
      </div>
      <div class="card">
        <div class="card-title">❄️ Top 5 Maior Atraso Atual</div>
        <div class="dezenas-grid" style="gap:8px">{top5a_html}</div>
        <div style="margin-top:10px;font-size:11px;color:#8b949e">Dezenas que estão há mais concursos sem sair</div>
      </div>
    </div>

    <div class="card" style="margin-bottom:16px">
      <div class="card-title">Mapa de Calor — Frequência das Dezenas (% de aparições)</div>
      <div class="heatmap">{heatmap}</div>
    </div>
    <div class="card">
      <div class="card-title">Atraso Atual (concursos sem sair)</div>
      {atraso_bars}
    </div>'''


# ─────────────────────────────────────────────
# ABA HISTÓRICO
# ─────────────────────────────────────────────
def render_aba_historico(ultimos):
    rows = []
    for r in reversed(ultimos):
        dezenas = sorted(list(r["dezenas"]))
        pares = sum(1 for d in dezenas if d % 2 == 0)
        soma = sum(dezenas)
        dez_html = "".join(
            f'<span class="chip">{d:02d}</span>' for d in dezenas
        )
        rows.append(f'''<tr>
          <td><b style="color:#58a6ff">#{r["concurso"]}</b></td>
          <td style="color:#8b949e">{r["data"]}</td>
          <td>{dez_html}</td>
          <td>{soma}</td>
          <td>{pares}</td>
          <td>{15-pares}</td>
        </tr>''')
    return f'''
    <div class="card">
      <div class="card-title">Últimos 15 Concursos Registrados</div>
      <table>
        <thead><tr><th>Concurso</th><th>Data</th><th>Dezenas Sorteadas</th><th>Soma</th><th>Pares</th><th>Ímpares</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </div>'''


# ─────────────────────────────────────────────
# HTML PRINCIPAL
# ─────────────────────────────────────────────
def build_html(jogos, conferencias, backtest, freq_list, ultimos, ultima_atualizacao):
    aba_jogos = render_aba_jogos(jogos, freq_list)
    aba_conf = render_aba_conferidor(conferencias)
    aba_bt = render_aba_backtest(backtest)
    aba_dez = render_aba_dezenas(freq_list)
    aba_hist = render_aba_historico(ultimos)

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lotofácil Lab — Painel Avançado</title>
<style>
  :root {{
    --bg:#0d1117; --card:#161b22; --card2:#1c2230; --border:#30363d;
    --text:#e6edf3; --muted:#8b949e; --accent:#58a6ff; --green:#3fb950;
    --yellow:#d29922; --red:#f85149; --purple:#a78bfa; --orange:#f0883e;
    --font:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:var(--font);font-size:14px;line-height:1.5}}

  /* HEADER */
  .header{{background:linear-gradient(135deg,#161b22 0%,#1c2230 100%);border-bottom:1px solid var(--border);padding:18px 28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
  .header h1{{font-size:20px;font-weight:700}} .header h1 span{{color:var(--accent)}}
  .header .sub{{color:var(--muted);font-size:12px;margin-top:3px}}
  .badge{{background:rgba(240,136,62,.15);color:var(--orange);border:1px solid rgba(240,136,62,.3);border-radius:6px;padding:4px 10px;font-size:11px;font-weight:600}}
  .badge-info{{background:rgba(88,166,255,.12);color:var(--accent);border:1px solid rgba(88,166,255,.25);border-radius:6px;padding:3px 9px;font-size:11px;font-weight:600}}

  /* TABS */
  .tabs{{display:flex;border-bottom:1px solid var(--border);padding:0 28px;background:var(--card);overflow-x:auto}}
  .tab{{padding:12px 18px;font-size:13px;font-weight:500;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;white-space:nowrap;transition:color .2s,border-color .2s;user-select:none}}
  .tab:hover{{color:var(--text)}} .tab.active{{color:var(--accent);border-bottom-color:var(--accent)}}

  /* PAGES */
  .page{{display:none;padding:24px 28px;max-width:1280px;margin:0 auto}} .page.active{{display:block}}

  /* CARDS */
  .card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;margin-bottom:0}}
  .card-title{{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:14px}}
  .grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
  @media(max-width:768px){{.grid-2{{grid-template-columns:1fr}}}}

  /* STAT BOXES */
  .stat-row{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px}}
  .stat-box{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 18px;flex:1;min-width:130px}}
  .stat-box .label{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
  .stat-box .value{{font-size:24px;font-weight:700;margin-top:4px}} .stat-box .hint{{font-size:11px;color:var(--muted);margin-top:2px}}
  .stat-mini{{background:var(--card2);border:1px solid var(--border);border-radius:8px;padding:10px 14px}}
  .stat-mini .label{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em}}
  .stat-mini .value{{font-size:20px;font-weight:700;margin-top:2px}}

  /* BOLINHAS */
  .bola{{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;border:2px solid;flex-shrink:0}}
  .bola-normal{{background:rgba(255,255,255,.06);border-color:var(--border);color:var(--text)}}
  .bola-acerto{{background:rgba(63,185,80,.2);border-color:#3fb950;color:#3fb950}}
  .bola-erro{{background:rgba(248,81,73,.08);border-color:rgba(248,81,73,.2);color:#8b949e}}
  .bola-sorteada{{background:rgba(88,166,255,.2);border-color:#58a6ff;color:#58a6ff}}
  .bola-quente{{background:rgba(210,153,34,.2);border-color:#d29922;color:#d29922}}
  .bola-atrasada{{background:rgba(248,81,73,.2);border-color:#f85149;color:#f85149}}
  .bola-moldura{{background:rgba(88,166,255,.1);border-color:rgba(88,166,255,.3);color:#58a6ff}}
  .bola-miolo{{background:rgba(63,185,80,.1);border-color:rgba(63,185,80,.3);color:#3fb950}}
  .bola-miolo-off{{background:rgba(255,255,255,.02);border-color:rgba(255,255,255,.05);color:#30363d}}
  .bola-moldura-off{{background:rgba(255,255,255,.02);border-color:rgba(255,255,255,.05);color:#30363d}}
  .dezenas-grid{{display:flex;flex-wrap:wrap;gap:6px}}

  /* BADGES */
  .metodo-badge{{font-size:12px;font-weight:600;padding:3px 10px;border-radius:20px;white-space:nowrap}}
  .m1{{background:rgba(88,166,255,.15);color:#58a6ff;border:1px solid rgba(88,166,255,.3)}}
  .m2{{background:rgba(63,185,80,.15);color:#3fb950;border:1px solid rgba(63,185,80,.3)}}
  .m3{{background:rgba(210,153,34,.15);color:#d29922;border:1px solid rgba(210,153,34,.3)}}
  .m4{{background:rgba(248,81,73,.15);color:#f85149;border:1px solid rgba(248,81,73,.3)}}
  .m5{{background:rgba(167,139,250,.15);color:#a78bfa;border:1px solid rgba(167,139,250,.3)}}
  .acertos-badge{{font-size:13px;font-weight:700;padding:4px 12px;border-radius:20px}}
  .ac-low{{background:rgba(248,81,73,.15);color:#f85149;border:1px solid rgba(248,81,73,.3)}}
  .ac-mid{{background:rgba(210,153,34,.15);color:#d29922;border:1px solid rgba(210,153,34,.3)}}
  .ac-good{{background:rgba(63,185,80,.15);color:#3fb950;border:1px solid rgba(63,185,80,.3)}}
  .ac-great{{background:rgba(88,166,255,.15);color:#58a6ff;border:1px solid rgba(88,166,255,.3)}}

  /* TABELAS */
  table{{width:100%;border-collapse:collapse;font-size:13px}}
  th{{text-align:left;padding:9px 10px;border-bottom:1px solid var(--border);color:var(--muted);font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap}}
  td{{padding:8px 10px;border-bottom:1px solid rgba(48,54,61,.5);white-space:nowrap}}
  tr:last-child td{{border-bottom:none}} tr:hover td{{background:rgba(255,255,255,.02)}}
  .table-scroll{{overflow-x:auto}}
  .desd-table th, .desd-table td{{padding:6px 8px;font-size:12px;text-align:center}}
  .desd-table th:first-child, .desd-table td:first-child{{text-align:left}}
  .desd-table th:nth-child(2), .desd-table td:nth-child(2){{text-align:left}}
  .conf-table th, .conf-table td{{padding:6px 7px;font-size:12px;text-align:center}}
  .conf-table th:first-child, .conf-table td:first-child{{text-align:left;min-width:120px}}
  .td-quente{{background:rgba(210,153,34,.12);color:#d29922;font-weight:700}}
  .td-atrasada{{background:rgba(248,81,73,.1);color:#f85149;font-weight:700}}
  .td-acerto{{background:rgba(63,185,80,.15);color:#3fb950;font-weight:700}}
  .td-erro{{color:#8b949e}}
  .chip{{display:inline-block;background:rgba(88,166,255,.1);border:1px solid rgba(88,166,255,.2);border-radius:4px;padding:1px 5px;margin:1px;font-size:12px;font-weight:600;color:#58a6ff}}

  /* HEATMAP */
  .heatmap{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}}
  .hm-cell{{border-radius:8px;padding:10px 6px;text-align:center;border:1px solid}}
  .hm-num{{font-size:15px;font-weight:700}} .hm-pct{{font-size:10px;color:var(--muted);margin-top:2px}} .hm-atraso{{font-size:10px;margin-top:2px}}

  /* MOLDURA / MIOLO */
  .moldura-grid, .miolo-grid{{display:flex;flex-direction:column;gap:5px;align-items:center}}

  /* LEGENDA */
  .legenda-row{{display:flex;gap:20px;flex-wrap:wrap;margin-bottom:16px;align-items:center;font-size:12px;color:var(--muted)}}
  .leg-item{{display:flex;align-items:center;gap:6px}}

  /* SECTION TITLE */
  .section-title{{display:flex;align-items:center;gap:12px;margin-bottom:16px;flex-wrap:wrap}}
  .concurso-num{{font-size:22px;font-weight:700;color:var(--accent)}}
  .concurso-data{{font-size:13px;color:var(--muted)}}

  /* DISCLAIMER */
  .disclaimer{{background:rgba(210,153,34,.08);border:1px solid rgba(210,153,34,.25);border-radius:8px;padding:12px 16px;font-size:12px;color:var(--muted);margin-bottom:20px;line-height:1.6}}
  .disclaimer b{{color:var(--yellow)}}

  /* MISC */
  .svg-wrap{{overflow-x:auto}}
  .empty{{text-align:center;padding:48px 24px;color:var(--muted)}}
  .empty .icon{{font-size:40px;margin-bottom:12px}} .empty p{{font-size:13px}}
  .gap-16{{gap:16px}}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>Lotofácil <span>Lab</span> — Painel Avançado</h1>
    <div class="sub">Laboratório Estatístico Educativo · Atualizado em {ultima_atualizacao}</div>
  </div>
  <div class="badge">⚠ Apenas estudo estatístico — não é recomendação de aposta</div>
</div>

<div class="tabs">
  <div class="tab active" onclick="showTab('jogos')">🎯 Jogos & Moldura</div>
  <div class="tab" onclick="showTab('conferidor')">✅ Conferidor</div>
  <div class="tab" onclick="showTab('backtest')">📊 Backtest</div>
  <div class="tab" onclick="showTab('dezenas')">🔥 Dezenas</div>
  <div class="tab" onclick="showTab('historico')">📋 Histórico</div>
</div>

<div class="page active" id="page-jogos">
  <div class="disclaimer">
    <b>Lembrete educativo:</b> Os jogos são gerados por 5 métodos estatísticos para fins de estudo comparativo.
    Nenhum método tem vantagem preditiva — todos convergem para a média teórica de <b>9 acertos</b> no longo prazo.
    Dezenas em <b style="color:#d29922">amarelo</b> = top 5 mais frequentes · em <b style="color:#f85149">vermelho</b> = top 5 maior atraso.
  </div>
  {aba_jogos}
</div>

<div class="page" id="page-conferidor">
  {aba_conf}
</div>

<div class="page" id="page-backtest">
  {aba_bt}
</div>

<div class="page" id="page-dezenas">
  {aba_dez}
</div>

<div class="page" id="page-historico">
  {aba_hist}
</div>

<script>
function showTab(name) {{
  var names = ['jogos','conferidor','backtest','dezenas','historico'];
  document.querySelectorAll('.tab').forEach(function(t,i){{ t.classList.toggle('active', names[i]===name); }});
  document.querySelectorAll('.page').forEach(function(p){{ p.classList.remove('active'); }});
  document.getElementById('page-'+name).classList.add('active');
}}
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    jogos = lib.carregar_jogos()
    conferencias = lib.carregar_conferencias()

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

    freq_list = []
    with open(lib.FREQUENCIA_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            freq_list.append({
                "d": int(row["dezena"]),
                "pct": float(row["frequencia_pct"]),
                "abs": int(row["frequencia_absoluta"]),
                "atraso": int(row["atraso_atual"]),
            })

    ultimos = lib.carregar_resultados()[-15:]
    ultima_atualizacao = datetime.now(BRASILIA).strftime("%d/%m/%Y %H:%M")

    html = build_html(jogos, conferencias, backtest, freq_list, ultimos, ultima_atualizacao)
    with open(PAINEL_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Painel avançado criado em: {PAINEL_PATH}")


if __name__ == "__main__":
    main()
