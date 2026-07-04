"""
Gera painel-educativo.html: pagina didatica sobre probabilidade e
esperanca matematica, com o novo design (roxo/rosa/ambar) baseado no
mockup do manus.ai, mas com os numeros reais do laboratorio (nao os
valores de exemplo do mockup).

Uso:
    python3 gerar_painel_educativo.py
"""
import json
import os

import lotofacil_lib as lib

PAINEL_PATH = os.path.join(lib.BASE_DIR, "painel-educativo.html")

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel Educativo — Laboratório Lotofácil</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family:'Inter',sans-serif; color:#1F1235; background:#FAF7FF; }
  details summary::-webkit-details-marker { color:#7C3AED; }
</style>
</head>
<body>

<div style="background: radial-gradient(1100px 420px at 18% -10%, rgba(245,158,11,.25) 0%, transparent 55%), linear-gradient(160deg,#3B0764 0%,#5B21B6 55%,#7C3AED 100%); color:#fff; padding:56px 8vw 50px;">
  <a href="index.html" style="font-size:12px; color:rgba(255,255,255,.6); text-decoration:none;">← Lotofácil Lab</a>
  <div style="display:flex; align-items:center; gap:10px; margin:18px 0 32px;">
    <div style="width:34px; height:34px; border-radius:9px; background:linear-gradient(135deg,#F59E0B,#EC4899); display:flex; align-items:center; justify-content:center; font-weight:800; color:#fff; font-size:15px;">L</div>
    <div style="font-weight:700; font-size:16px; letter-spacing:.01em;">Laboratório Lotofácil</div>
  </div>
  <h1 style="font-family:'Sora',sans-serif; font-weight:800; font-size:clamp(28px,4vw,44px); line-height:1.15; margin:0 0 16px; max-width:760px;">
    A matemática por trás da Lotofácil, sem prometer o que a matemática não entrega.
  </h1>
  <p style="font-size:17px; color:#E9D9FF; max-width:620px; line-height:1.6; margin:0 0 28px;">
    Um estudo estatístico contínuo sobre resultados reais da Lotofácil: frequência, atraso, distribuição e o comportamento de diferentes formas de montar um jogo — comparadas sempre contra o valor teórico esperado, não entre si por "quem ganha mais".
  </p>
  <div style="display:flex; gap:10px; flex-wrap:wrap;">
    <span style="background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2); color:#fff; padding:7px 14px; border-radius:999px; font-size:13px;">Atualizado diariamente</span>
    <span style="background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2); color:#fff; padding:7px 14px; border-radius:999px; font-size:13px;">__TOTAL_CONCURSOS__ concursos reais analisados</span>
    <span style="background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.2); color:#fff; padding:7px 14px; border-radius:999px; font-size:13px;">Esperança teórica: __ESPERANCA__ acertos</span>
  </div>
</div>

<div style="background:#FFF7EA; border-top:1px solid #FDE9C4; border-bottom:1px solid #FDE9C4; color:#92400E; padding:14px 8vw; font-size:13.5px; line-height:1.6;">
  <b style="color:#7C2D12;">Isto não é um método para ganhar.</b> Nenhum conteúdo aqui aumenta a chance de acertar 14 ou 15 dezenas. A Lotofácil é um sorteio aleatório e cada concurso é independente dos anteriores. Este material é um estudo de matemática e estatística — não é aconselhamento financeiro nem recomendação de aposta.
</div>

<main style="max-width:1040px; margin:0 auto; padding:56px 8vw 80px;">

  <section style="margin-bottom:64px;">
    <div style="text-transform:uppercase; letter-spacing:.08em; font-size:12px; color:#7C3AED; font-weight:700; margin-bottom:8px;">Como funciona</div>
    <h2 style="font-family:'Sora',sans-serif; font-size:26px; margin:0 0 14px;">Um experimento estatístico contínuo, não uma fórmula</h2>
    <p style="color:#6B5B8A; font-size:15.5px; line-height:1.7; max-width:720px; margin:0 0 28px;">Todo dia, o laboratório registra o resultado real da Lotofácil e testa 5 formas diferentes de montar um jogo de 15 dezenas — cada uma é uma hipótese, não uma estratégia.</p>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:18px;">
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:20px; box-shadow:0 2px 10px rgba(43,10,77,.05);">
        <div style="display:inline-flex; width:26px; height:26px; border-radius:8px; background:#EDE4FF; color:#7C3AED; align-items:center; justify-content:center; font-weight:700; font-size:13px; margin-bottom:10px;">1</div>
        <h3 style="font-size:15.5px; margin:0 0 6px;">Coleta</h3>
        <p style="font-size:13.5px; color:#6B5B8A; line-height:1.6; margin:0;">Busca o resultado oficial mais recente e soma ao histórico real, concurso a concurso.</p>
      </div>
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:20px; box-shadow:0 2px 10px rgba(43,10,77,.05);">
        <div style="display:inline-flex; width:26px; height:26px; border-radius:8px; background:#EDE4FF; color:#7C3AED; align-items:center; justify-content:center; font-weight:700; font-size:13px; margin-bottom:10px;">2</div>
        <h3 style="font-size:15.5px; margin:0 0 6px;">Comparação</h3>
        <p style="font-size:13.5px; color:#6B5B8A; line-height:1.6; margin:0;">Gera 5 jogos fictícios por métodos diferentes (aleatório, frequência, atraso, par/ímpar, soma) só para observar.</p>
      </div>
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:20px; box-shadow:0 2px 10px rgba(43,10,77,.05);">
        <div style="display:inline-flex; width:26px; height:26px; border-radius:8px; background:#EDE4FF; color:#7C3AED; align-items:center; justify-content:center; font-weight:700; font-size:13px; margin-bottom:10px;">3</div>
        <h3 style="font-size:15.5px; margin:0 0 6px;">Conferência</h3>
        <p style="font-size:13.5px; color:#6B5B8A; line-height:1.6; margin:0;">Confere cada jogo contra o resultado real e registra quantas dezenas bateram — sem exceção.</p>
      </div>
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:20px; box-shadow:0 2px 10px rgba(43,10,77,.05);">
        <div style="display:inline-flex; width:26px; height:26px; border-radius:8px; background:#EDE4FF; color:#7C3AED; align-items:center; justify-content:center; font-weight:700; font-size:13px; margin-bottom:10px;">4</div>
        <h3 style="font-size:15.5px; margin:0 0 6px;">Conclusão honesta</h3>
        <p style="font-size:13.5px; color:#6B5B8A; line-height:1.6; margin:0;">Compara tudo contra o valor esperado por acaso (9 acertos). Se convergir para lá, é matemática funcionando — não um método "achado".</p>
      </div>
    </div>
  </section>

  <section style="margin-bottom:64px;">
    <div style="text-transform:uppercase; letter-spacing:.08em; font-size:12px; color:#7C3AED; font-weight:700; margin-bottom:8px;">Estado atual</div>
    <h2 style="font-family:'Sora',sans-serif; font-size:26px; margin:0 0 14px;">O que os dados mostram até agora</h2>
    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin:0 0 40px;">
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:18px 20px;">
        <div style="font-size:12.5px; color:#8B76B0; text-transform:uppercase; letter-spacing:.03em;">Concursos analisados</div>
        <div style="font-size:28px; font-weight:700; margin-top:6px; font-family:'Sora',sans-serif;">__TOTAL_CONCURSOS__</div>
        <div style="font-size:12px; color:#8B76B0; margin-top:4px;">histórico real, crescendo todo dia</div>
      </div>
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:18px 20px;">
        <div style="font-size:12.5px; color:#8B76B0; text-transform:uppercase; letter-spacing:.03em;">Próximo concurso</div>
        <div style="font-size:28px; font-weight:700; margin-top:6px; font-family:'Sora',sans-serif;">__PROXIMO_CONCURSO__</div>
        <div style="font-size:12px; color:#8B76B0; margin-top:4px;">jogos de estudo já gerados</div>
      </div>
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:18px 20px;">
        <div style="font-size:12.5px; color:#8B76B0; text-transform:uppercase; letter-spacing:.03em;">Esperança teórica</div>
        <div style="font-size:28px; font-weight:700; margin-top:6px; font-family:'Sora',sans-serif; color:#7C3AED;">__ESPERANCA__</div>
        <div style="font-size:12px; color:#8B76B0; margin-top:4px;">acertos por jogo, via hipergeométrica</div>
      </div>
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:14px; padding:18px 20px;">
        <div style="font-size:12.5px; color:#8B76B0; text-transform:uppercase; letter-spacing:.03em;">Dezena mais frequente</div>
        <div style="font-size:28px; font-weight:700; margin-top:6px; font-family:'Sora',sans-serif;">__DEZENA_MAIS_FREQ__</div>
        <div style="font-size:12px; color:#8B76B0; margin-top:4px;">__PCT_MAIS_FREQ__% dos concursos observados</div>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:18px;">
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:16px; padding:24px;">
        <div style="font-size:13px; color:#8B76B0; margin-bottom:10px;">Frequência de cada dezena (%)</div>
        <canvas id="freqChart" style="max-height:280px;" role="img" aria-label="Frequência relativa de cada dezena de 1 a 25"></canvas>
      </div>
      <div style="background:#fff; border:1px solid #E9DFFB; border-radius:16px; padding:24px;">
        <div style="font-size:13px; color:#8B76B0; margin-bottom:10px;">Atraso atual (concursos sem sair)</div>
        <canvas id="atrasoChart" style="max-height:280px;" role="img" aria-label="Atraso atual de cada dezena de 1 a 25"></canvas>
      </div>
    </div>
  </section>

  <section style="margin-bottom:64px;">
    <div style="text-transform:uppercase; letter-spacing:.08em; font-size:12px; color:#7C3AED; font-weight:700; margin-bottom:8px;">Métodos em teste</div>
    <h2 style="font-family:'Sora',sans-serif; font-size:26px; margin:0 0 14px;">5 hipóteses, comparadas de forma neutra</h2>
    <p style="color:#6B5B8A; font-size:15.5px; line-height:1.7; max-width:720px; margin:0 0 28px;">Nenhuma é chamada de "melhor". A expectativa matemática é que todas convirjam para perto de 9 acertos em média — e é justamente isso que este estudo acompanha ao longo do tempo.</p>
    <div style="background:#fff; border:1px solid #E9DFFB; border-radius:16px; padding:24px; overflow:auto;">
      <table style="width:100%; border-collapse:collapse; font-size:13.5px;">
        <thead><tr><th style="text-align:left; padding:10px 12px; border-bottom:1px solid #E9DFFB; color:#8B76B0; font-size:11.5px; text-transform:uppercase;">Método</th><th style="text-align:left; padding:10px 12px; border-bottom:1px solid #E9DFFB; color:#8B76B0; font-size:11.5px; text-transform:uppercase;">O que faz</th></tr></thead>
        <tbody>
          <tr><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">Aleatório puro</td><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">15 dezenas sorteadas sem nenhum critério — o "controle" do experimento.</td></tr>
          <tr><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">Mais frequentes</td><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">As 15 dezenas que mais saíram no histórico até aquele momento.</td></tr>
          <tr><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">Mais atrasadas</td><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">As 15 dezenas há mais concursos sem sair.</td></tr>
          <tr><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">Par/ímpar balanceado</td><td style="padding:10px 12px; border-bottom:1px solid #F1ECFB;">Aleatório, forçando 8 pares e 7 ímpares.</td></tr>
          <tr><td style="padding:10px 12px;">Soma na faixa comum</td><td style="padding:10px 12px;">Aleatório, só aceita jogos com soma entre 180 e 210.</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <section>
    <div style="text-transform:uppercase; letter-spacing:.08em; font-size:12px; color:#7C3AED; font-weight:700; margin-bottom:8px;">Perguntas frequentes</div>
    <h2 style="font-family:'Sora',sans-serif; font-size:26px; margin:0 0 14px;">Antes de qualquer dúvida</h2>
    <details open style="background:#fff; border:1px solid #E9DFFB; border-radius:12px; padding:16px 18px; margin-bottom:10px;">
      <summary style="cursor:pointer; font-weight:600; font-size:14.5px;">Isso aumenta minha chance de ganhar?</summary>
      <p style="color:#6B5B8A; font-size:13.8px; line-height:1.65; margin:10px 0 0;">Não. Nenhum método estudado aqui muda a probabilidade real de um jogo acertar 14 ou 15 dezenas. A Lotofácil é um sorteio aleatório: cada concurso é independente dos anteriores, e frequência ou atraso passados não influenciam o próximo resultado.</p>
    </details>
    <details style="background:#fff; border:1px solid #E9DFFB; border-radius:12px; padding:16px 18px; margin-bottom:10px;">
      <summary style="cursor:pointer; font-weight:600; font-size:14.5px;">Então por que estudar frequência e atraso?</summary>
      <p style="color:#6B5B8A; font-size:13.8px; line-height:1.65; margin:10px 0 0;">Porque é um jeito prático e visual de aprender estatística de verdade: distribuição, variância, viés de confirmação e o que significa "esperança matemática". O objetivo é entender o acaso, não escapar dele.</p>
    </details>
    <details style="background:#fff; border:1px solid #E9DFFB; border-radius:12px; padding:16px 18px; margin-bottom:10px;">
      <summary style="cursor:pointer; font-weight:600; font-size:14.5px;">Algum dos 5 métodos "está ganhando"?</summary>
      <p style="color:#6B5B8A; font-size:13.8px; line-height:1.65; margin:10px 0 0;">Se algum aparecer com média mais alta por um tempo, isso é variação estatística normal em amostra pequena — não sinal de que funciona. O próprio propósito do laboratório é mostrar essa oscilação se equilibrando conforme mais concursos entram na conta.</p>
    </details>
    <details style="background:#fff; border:1px solid #E9DFFB; border-radius:12px; padding:16px 18px;">
      <summary style="cursor:pointer; font-weight:600; font-size:14.5px;">Posso usar os jogos gerados aqui para apostar?</summary>
      <p style="color:#6B5B8A; font-size:13.8px; line-height:1.65; margin:10px 0 0;">Os jogos são gerados só para fins de estudo estatístico. Se decidir apostar, a decisão e o risco são inteiramente seus — este material não recomenda, não promete e não se responsabiliza por resultado de aposta.</p>
    </details>
  </section>

</main>

<footer style="background:#3B0764; color:#C9AEEA; padding:34px 8vw; font-size:12.8px; line-height:1.7;">
  <b style="color:#F3E8FF;">Laboratório Lotofácil</b> — conteúdo educativo sobre matemática, estatística e probabilidade aplicadas a resultados reais da Lotofácil. Não possui vínculo com a Caixa Econômica Federal. Resultados passados não garantem resultados futuros. Loteria é aleatória; este material não constitui aconselhamento financeiro nem recomendação de aposta.
</footer>

<script>
const dados = __DADOS_JSON__;
new Chart(document.getElementById('freqChart'), {
  type:'bar',
  data:{ labels:dados.dezenas, datasets:[{ data:dados.freq_pct, backgroundColor:'#7C3AED', borderRadius:4 }] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}},
    scales:{ x:{grid:{display:false}}, y:{grid:{color:'#F1ECFB'}, ticks:{callback:v=>v+'%'}} } }
});
new Chart(document.getElementById('atrasoChart'), {
  type:'bar',
  data:{ labels:dados.dezenas, datasets:[{ data:dados.atraso, backgroundColor:'#F59E0B', borderRadius:4 }] },
  options:{ responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}},
    scales:{ x:{grid:{display:false}}, y:{grid:{color:'#F1ECFB'}, ticks:{stepSize:1}} } }
});
</script>
</body>
</html>
"""


def main():
    freq, atraso, total = lib.frequencia_e_atraso()
    resultados = lib.carregar_resultados()
    proximo_concurso = (resultados[-1]["concurso"] + 1) if resultados else 1

    maior_freq_valor = max(freq[d] for d in lib.TODAS_DEZENAS)
    mais_frequentes = sorted([d for d in lib.TODAS_DEZENAS if freq[d] == maior_freq_valor])
    dezena_mais_freq_str = " e ".join(f"{d:02d}" for d in mais_frequentes) if len(mais_frequentes) <= 3 else f"{mais_frequentes[0]:02d} (+{len(mais_frequentes)-1})"
    pct_mais_freq = round(100 * maior_freq_valor / total, 1) if total else 0.0

    dados_json = {
        "dezenas": [f"{d:02d}" for d in lib.TODAS_DEZENAS],
        "freq_pct": [round(100 * freq[d] / total, 2) if total else 0 for d in lib.TODAS_DEZENAS],
        "atraso": [atraso[d] for d in lib.TODAS_DEZENAS],
    }

    html = TEMPLATE
    html = html.replace("__TOTAL_CONCURSOS__", f"{total:,}".replace(",", "."))
    html = html.replace("__PROXIMO_CONCURSO__", f"{proximo_concurso:,}".replace(",", "."))
    html = html.replace("__ESPERANCA__", str(lib.ESPERANCA_TEORICA).replace(".", ","))
    html = html.replace("__DEZENA_MAIS_FREQ__", dezena_mais_freq_str)
    html = html.replace("__PCT_MAIS_FREQ__", str(pct_mais_freq).replace(".", ","))
    html = html.replace("__DADOS_JSON__", json.dumps(dados_json, ensure_ascii=False))

    with open(PAINEL_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"painel-educativo.html gerado em: {PAINEL_PATH}")


if __name__ == "__main__":
    main()
