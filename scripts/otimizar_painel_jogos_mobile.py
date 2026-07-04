"""
Aplica uma camada de correção mobile no painel_jogos.html.

Objetivo:
- impedir faixa branca lateral no celular;
- forçar largura real da tela;
- transformar grids em 1 coluna em celular/tablet;
- reduzir bolinhas e espaçamentos;
- deixar abas e tabelas roláveis sem estourar a página.

Uso:
    python3 otimizar_painel_jogos_mobile.py
"""
import os

import lotofacil_lib as lib

PAINEL_PATH = os.path.join(lib.BASE_DIR, "painel_jogos.html")

MOBILE_CSS = r"""

/* ─────────────────────────────────────────────
   MOBILE FIX V2 — injetado automaticamente
   Corrige overflow lateral no painel avançado
   ───────────────────────────────────────────── */
html {
  width: 100% !important;
  min-width: 0 !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
  background: #F8F5FF !important;
}

body {
  width: 100% !important;
  min-width: 0 !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
  background: #F8F5FF !important;
  -webkit-text-size-adjust: 100%;
}

*, *::before, *::after {
  box-sizing: border-box !important;
}

img,
svg,
canvas,
table {
  max-width: 100%;
}

.page,
.header,
.tabs,
.card,
.disclaimer,
.section-title,
.stat-row,
.grid-2,
.legenda-row,
.table-scroll,
.svg-wrap {
  max-width: 100% !important;
}

.table-scroll,
.svg-wrap {
  overflow-x: auto !important;
  -webkit-overflow-scrolling: touch;
}

/* Alguns celulares abrem o Chrome com viewport CSS grande.
   Por isso o breakpoint precisa ser alto. */
@media (max-width: 1280px) {
  body {
    display: block !important;
  }

  .page {
    padding: 18px 12px !important;
    margin: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  .header {
    width: 100% !important;
    max-width: 100% !important;
    padding: 16px 12px !important;
    display: block !important;
  }

  .header h1 {
    font-size: 18px !important;
    line-height: 1.2 !important;
    max-width: 100% !important;
  }

  .header .sub {
    font-size: 12px !important;
    line-height: 1.35 !important;
    max-width: 100% !important;
  }

  .header .badge {
    display: inline-block !important;
    margin-top: 12px !important;
    max-width: 100% !important;
    white-space: normal !important;
    line-height: 1.35 !important;
  }

  .tabs {
    width: 100% !important;
    max-width: 100% !important;
    padding: 0 8px !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    white-space: nowrap !important;
    -webkit-overflow-scrolling: touch;
  }

  .tab {
    flex: 0 0 auto !important;
    padding: 11px 12px !important;
    font-size: 12px !important;
  }

  .grid-2 {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) !important;
    gap: 14px !important;
    width: 100% !important;
    max-width: 100% !important;
  }

  .card {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    padding: 14px !important;
    border-radius: 14px !important;
    overflow: hidden !important;
  }

  .card-title {
    font-size: 11px !important;
    line-height: 1.35 !important;
    overflow-wrap: anywhere !important;
  }

  .section-title {
    display: block !important;
    margin-bottom: 14px !important;
    width: 100% !important;
  }

  .concurso-num {
    display: block !important;
    font-size: 24px !important;
    line-height: 1.2 !important;
    margin-bottom: 8px !important;
  }

  .concurso-data,
  .badge-info {
    display: inline-block !important;
    margin: 0 6px 6px 0 !important;
  }

  .legenda-row {
    gap: 10px !important;
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) !important;
    font-size: 12px !important;
    width: 100% !important;
  }

  .leg-item {
    width: 100% !important;
    min-width: 0 !important;
    overflow-wrap: anywhere !important;
  }

  .moldura-grid,
  .miolo-grid,
  .mj-volante {
    width: 100% !important;
    max-width: 100% !important;
    align-items: center !important;
    overflow: hidden !important;
  }

  .moldura-grid > div,
  .miolo-grid > div,
  .mj-row {
    width: 100% !important;
    max-width: 100% !important;
    display: grid !important;
    grid-template-columns: repeat(5, minmax(0, 1fr)) !important;
    gap: 6px !important;
    justify-items: center !important;
  }

  .bola,
  .moldura-grid .bola,
  .miolo-grid .bola {
    width: clamp(34px, 13vw, 48px) !important;
    height: clamp(34px, 13vw, 48px) !important;
    font-size: clamp(11px, 3.5vw, 14px) !important;
    border-width: 2px !important;
  }

  .mj-bola {
    width: clamp(38px, 14vw, 52px) !important;
    height: clamp(38px, 14vw, 52px) !important;
    font-size: clamp(12px, 4vw, 15px) !important;
  }

  .dezenas-grid {
    justify-content: center !important;
  }

  .stat-row {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) !important;
    gap: 10px !important;
    width: 100% !important;
  }

  .stat-box,
  .stat-mini {
    min-width: 0 !important;
    width: 100% !important;
  }

  table {
    min-width: 620px;
  }
}

@media (max-width: 600px) {
  .page {
    padding: 16px 10px !important;
  }

  .card {
    padding: 12px !important;
  }

  .moldura-grid > div,
  .miolo-grid > div,
  .mj-row {
    gap: 5px !important;
  }

  .bola,
  .moldura-grid .bola,
  .miolo-grid .bola {
    width: clamp(32px, 14vw, 42px) !important;
    height: clamp(32px, 14vw, 42px) !important;
    font-size: 12px !important;
  }

  .stat-row {
    grid-template-columns: minmax(0, 1fr) !important;
  }
}
"""


def main():
    if not os.path.exists(PAINEL_PATH):
        print(f"[skip] Arquivo não encontrado: {PAINEL_PATH}")
        return

    with open(PAINEL_PATH, encoding="utf-8") as f:
        html = f.read()

    marcador_v1 = "MOBILE FIX — injetado automaticamente"
    marcador_v2 = "MOBILE FIX V2 — injetado automaticamente"

    if marcador_v2 in html:
        print("[ok] Painel já contém correção mobile V2.")
        return

    # Se existir a versão antiga, remove para não conflitar.
    if marcador_v1 in html:
        inicio = html.find("/* ─────────────────────────────────────────────\n   MOBILE FIX")
        fim = html.find("</style>", inicio)
        if inicio != -1 and fim != -1:
            html = html[:inicio] + html[fim:]

    if "</style>" in html:
        html = html.replace("</style>", MOBILE_CSS + "\n</style>", 1)
    else:
        html = html.replace("</head>", f"<style>{MOBILE_CSS}</style>\n</head>", 1)

    with open(PAINEL_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[ok] Correção mobile V2 aplicada em: {PAINEL_PATH}")


if __name__ == "__main__":
    main()
