from __future__ import annotations

import itertools
import json
import math
import random
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from statistics import mean
from typing import Sequence

TOTAL_DEZENAS = 25
DEZENAS_JOGO = 15
TODAS = tuple(range(1, 26))
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
MOLDURA = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}


@dataclass
class Filtros:
    soma_min: int = 180
    soma_max: int = 220
    pares_min: int = 6
    pares_max: int = 9
    primos_min: int = 5
    primos_max: int = 7
    moldura_min: int = 8
    moldura_max: int = 12
    linhas_min: int = 4
    max_sequencia: int = 6


@dataclass
class Pesos:
    frequencia_10: float = 0.19
    frequencia_30: float = 0.12
    atraso_equilibrado: float = 0.12
    repeticao_anterior: float = 0.15
    ciclo: float = 0.12
    vizinhanca: float = 0.08
    linhas_colunas: float = 0.08
    moldura: float = 0.07
    primos: float = 0.07

    def normalizar(self) -> None:
        total = sum(asdict(self).values())
        if total <= 0:
            raise ValueError("Pesos inválidos")
        for nome in asdict(self):
            setattr(self, nome, getattr(self, nome) / total)


@dataclass(frozen=True)
class Concurso:
    concurso: int
    dezenas: tuple[int, ...]
    data: str | None = None

    @classmethod
    def criar(cls, concurso: int, dezenas: Sequence[int], data: str | None = None) -> "Concurso":
        ds = tuple(sorted(set(int(d) for d in dezenas)))
        if len(ds) != 15 or any(d < 1 or d > 25 for d in ds):
            raise ValueError("Concurso deve ter 15 dezenas únicas entre 1 e 25")
        return cls(int(concurso), ds, data)


@dataclass
class ResultadoJogo:
    jogo: tuple[int, ...]
    nota: float
    soma: int
    pares: int
    primos: int
    moldura: int
    linhas: int
    colunas: int
    maior_sequencia: int
    repetidas_anterior: int


@dataclass
class ResultadoGeracao:
    base: tuple[int, ...]
    jogos: list[ResultadoJogo]
    combinacoes_completas: int
    cobertura_nominal: float
    ranking_dezenas: list[tuple[int, float]]
    explicacao_base: dict[int, dict[str, float]]


@dataclass
class MemoriaAdaptativa:
    pesos: Pesos = field(default_factory=Pesos)
    desempenho: list[dict] = field(default_factory=list)
    jogos_bons: list[dict] = field(default_factory=list)
    versao: int = 1

    @classmethod
    def carregar(cls, caminho: str | Path) -> "MemoriaAdaptativa":
        p = Path(caminho)
        if not p.exists():
            memoria = cls()
            memoria.pesos.normalizar()
            return memoria
        dados = json.loads(p.read_text(encoding="utf-8"))
        memoria = cls(
            pesos=Pesos(**dados.get("pesos", {})),
            desempenho=dados.get("desempenho", []),
            jogos_bons=dados.get("jogos_bons", []),
            versao=int(dados.get("versao", 1)),
        )
        memoria.pesos.normalizar()
        return memoria

    def salvar(self, caminho: str | Path) -> None:
        Path(caminho).write_text(json.dumps({
            "pesos": asdict(self.pesos),
            "desempenho": self.desempenho[-2000:],
            "jogos_bons": self.jogos_bons[-500:],
            "versao": self.versao,
        }, ensure_ascii=False, indent=2), encoding="utf-8")


class MotorLotofacil:
    def __init__(self, historico: Sequence[Concurso], memoria: MemoriaAdaptativa | None = None,
                 filtros: Filtros | None = None, seed: int = 20260725) -> None:
        self.historico = sorted(historico, key=lambda c: c.concurso)
        self.memoria = memoria or MemoriaAdaptativa()
        self.memoria.pesos.normalizar()
        self.filtros = filtros or Filtros()
        self.rng = random.Random(seed)
        self.historicos = {c.dezenas for c in self.historico}

    def _janela(self, n: int) -> list[Concurso]:
        return self.historico[-n:]

    def _atrasos(self) -> dict[int, int]:
        atrasos = {d: len(self.historico) for d in TODAS}
        for distancia, concurso in enumerate(reversed(self.historico)):
            for d in concurso.dezenas:
                if atrasos[d] == len(self.historico):
                    atrasos[d] = distancia
        return atrasos

    def _ciclo_pendente(self) -> set[int]:
        vistos: set[int] = set()
        for concurso in reversed(self.historico):
            vistos.update(concurso.dezenas)
            if len(vistos) == 25:
                break
        return set(TODAS) - vistos

    @staticmethod
    def _normalizar(v: float, minimo: float, maximo: float) -> float:
        return 0.5 if maximo <= minimo else max(0.0, min(1.0, (v - minimo) / (maximo - minimo)))

    def pontuar_dezenas(self) -> tuple[list[tuple[int, float]], dict[int, dict[str, float]]]:
        j10, j30 = self._janela(10), self._janela(30)
        f10 = Counter(d for c in j10 for d in c.dezenas)
        f30 = Counter(d for c in j30 for d in c.dezenas)
        atrasos = self._atrasos()
        pendentes = self._ciclo_pendente()
        anterior = set(self.historico[-1].dezenas) if self.historico else set()
        minimo, maximo = min(atrasos.values(), default=0), max(atrasos.values(), default=0)
        componentes: dict[int, dict[str, float]] = {}
        ranking: list[tuple[int, float]] = []
        p = self.memoria.pesos

        for d in TODAS:
            freq10 = 1 - abs((f10[d] / max(1, len(j10))) - 0.60) / 0.60
            freq30 = 1 - abs((f30[d] / max(1, len(j30))) - 0.60) / 0.60
            atraso_n = self._normalizar(atrasos[d], minimo, maximo)
            atraso = 1 - abs(atraso_n - 0.45) / 0.55
            vizinhos = sum(1 for x in (d - 1, d + 1) if x in anterior)
            linha, coluna = (d - 1) // 5, (d - 1) % 5
            ocup_linha = sum((x - 1) // 5 == linha for x in anterior) / 5 if anterior else 0.6
            ocup_coluna = sum((x - 1) % 5 == coluna for x in anterior) / 5 if anterior else 0.6
            comp = {
                "frequencia_10": max(0.0, freq10),
                "frequencia_30": max(0.0, freq30),
                "atraso_equilibrado": max(0.0, atraso),
                "repeticao_anterior": 1.0 if d in anterior else 0.45,
                "ciclo": 1.0 if d in pendentes else 0.55,
                "vizinhanca": min(1.0, 0.35 + 0.325 * vizinhos),
                "linhas_colunas": 1 - abs(((ocup_linha + ocup_coluna) / 2) - 0.6),
                "moldura": 1.0 if d in MOLDURA else 0.72,
                "primos": 1.0 if d in PRIMOS else 0.78,
            }
            nota = sum(comp[k] * getattr(p, k) for k in comp) * 100
            componentes[d] = {k: round(v, 4) for k, v in comp.items()}
            ranking.append((d, round(nota, 4)))

        ranking.sort(key=lambda x: (-x[1], x[0]))
        return ranking, componentes

    def selecionar_base(self, tamanho: int = 18):
        if not 15 <= tamanho <= 21:
            raise ValueError("Base deve ter entre 15 e 21 dezenas")
        ranking, componentes = self.pontuar_dezenas()
        notas = dict(ranking)
        pool = [d for d, _ in ranking[:min(23, tamanho + 5)]]
        melhor: tuple[float, tuple[int, ...]] | None = None
        for base in itertools.combinations(pool, tamanho):
            pares = sum(d % 2 == 0 for d in base)
            primos = sum(d in PRIMOS for d in base)
            moldura = sum(d in MOLDURA for d in base)
            linhas = len({(d - 1) // 5 for d in base})
            colunas = len({(d - 1) % 5 for d in base})
            penalidade = abs(pares - round(tamanho * .48)) * 2.2
            penalidade += abs(primos - round(tamanho * .36)) * 1.8
            penalidade += abs(moldura - round(tamanho * .64)) * 1.5
            penalidade += (5 - linhas) * 4 + (5 - colunas) * 4
            candidato = (sum(notas[d] for d in base) - penalidade, base)
            if melhor is None or candidato[0] > melhor[0]:
                melhor = candidato
        if melhor is None:
            raise RuntimeError("Não foi possível selecionar base")
        return tuple(sorted(melhor[1])), ranking, componentes

    @staticmethod
    def _maior_sequencia(jogo: Sequence[int]) -> int:
        maior = atual = 1
        for a, b in zip(jogo, jogo[1:]):
            atual = atual + 1 if b == a + 1 else 1
            maior = max(maior, atual)
        return maior

    def avaliar_jogo(self, jogo: Sequence[int]) -> ResultadoJogo:
        j = tuple(sorted(jogo))
        anterior = set(self.historico[-1].dezenas) if self.historico else set()
        soma = sum(j)
        pares = sum(d % 2 == 0 for d in j)
        primos = sum(d in PRIMOS for d in j)
        moldura = sum(d in MOLDURA for d in j)
        linhas = len({(d - 1) // 5 for d in j})
        colunas = len({(d - 1) % 5 for d in j})
        sequencia = self._maior_sequencia(j)
        repetidas = len(set(j) & anterior)
        nota = 100 - abs(soma - 195) * .75 - abs(pares - 7.5) * 5
        nota -= abs(primos - 5.5) * 4 + abs(moldura - 9.5) * 3.2
        nota -= (5 - linhas) * 8 + (5 - colunas) * 5
        nota -= max(0, sequencia - 4) * 6 + abs(repetidas - 9) * 3.2
        if j in self.historicos:
            nota -= 100
        return ResultadoJogo(j, round(max(0, nota), 3), soma, pares, primos, moldura,
                             linhas, colunas, sequencia, repetidas)

    def jogo_valido(self, r: ResultadoJogo) -> bool:
        f = self.filtros
        return f.soma_min <= r.soma <= f.soma_max and f.pares_min <= r.pares <= f.pares_max \
            and f.primos_min <= r.primos <= f.primos_max and f.moldura_min <= r.moldura <= f.moldura_max \
            and r.linhas >= f.linhas_min and r.maior_sequencia <= f.max_sequencia and r.jogo not in self.historicos

    def gerar_fechamento(self, base: Sequence[int], quantidade: int) -> list[ResultadoJogo]:
        base = tuple(sorted(set(base)))
        if len(base) < 15:
            raise ValueError("Base precisa ter ao menos 15 dezenas")
        candidatas = [self.avaliar_jogo(c) for c in itertools.combinations(base, 15)]
        candidatas = sorted((r for r in candidatas if self.jogo_valido(r)), key=lambda r: (-r.nota, r.jogo))
        if quantidade >= len(candidatas):
            return candidatas

        selecionadas: list[ResultadoJogo] = []
        freq = Counter()
        pares_cobertos: set[tuple[int, int]] = set()
        while candidatas and len(selecionadas) < quantidade:
            melhor_i, melhor_valor = 0, -1e18
            for i, r in enumerate(candidatas[:1500]):
                inter = max((len(set(r.jogo) & set(x.jogo)) for x in selecionadas), default=0)
                novos_pares = sum(p not in pares_cobertos for p in itertools.combinations(r.jogo, 2))
                equilibrio = -sum(freq[d] for d in r.jogo) / 15
                valor = r.nota * 3 + novos_pares * .12 + equilibrio * 2 - max(0, inter - 11) * 18
                if valor > melhor_valor:
                    melhor_i, melhor_valor = i, valor
            escolhida = candidatas.pop(melhor_i)
            selecionadas.append(escolhida)
            freq.update(escolhida.jogo)
            pares_cobertos.update(itertools.combinations(escolhida.jogo, 2))
        return selecionadas

    def gerar(self, tamanho_base: int = 18, quantidade: int = 120) -> ResultadoGeracao:
        base, ranking, componentes = self.selecionar_base(tamanho_base)
        jogos = self.gerar_fechamento(base, quantidade)
        total = math.comb(tamanho_base, 15)
        cobertura = 100 * len(jogos) / total if total else 0
        return ResultadoGeracao(base, jogos, total, round(cobertura, 3), ranking,
                                {d: componentes[d] for d in base})

    def registrar_desempenho(self, resultado: ResultadoGeracao, sorteadas: Sequence[int]) -> dict:
        alvo = set(sorteadas)
        distribuicao = Counter(len(set(j.jogo) & alvo) for j in resultado.jogos)
        registro = {
            "base": list(resultado.base),
            "acertos_base": len(set(resultado.base) & alvo),
            "melhor_acerto": max(distribuicao, default=0),
            "distribuicao": {str(k): v for k, v in sorted(distribuicao.items())},
            "quantidade_jogos": len(resultado.jogos),
        }
        self.memoria.desempenho.append(registro)
        for j in resultado.jogos:
            acertos = len(set(j.jogo) & alvo)
            if acertos >= 13:
                self.memoria.jogos_bons.append({"jogo": list(j.jogo), "acertos": acertos, "nota": j.nota})
        return registro

    def recalibrar_pesos(self, taxa: float = .03) -> Pesos:
        recentes = self.memoria.desempenho[-100:]
        if len(recentes) < 20:
            return self.memoria.pesos
        media_base = mean(x["acertos_base"] for x in recentes)
        p = self.memoria.pesos
        if media_base < 11.8:
            p.frequencia_10 *= 1 - taxa
            p.repeticao_anterior *= 1 - taxa / 2
            p.atraso_equilibrado *= 1 + taxa
            p.ciclo *= 1 + taxa
        else:
            p.frequencia_10 *= 1 + taxa / 2
            p.repeticao_anterior *= 1 + taxa / 2
            p.atraso_equilibrado *= 1 - taxa / 3
        p.normalizar()
        return p


def carregar_historico_json(caminho: str | Path) -> list[Concurso]:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    if isinstance(dados, dict):
        dados = dados.get("concursos", dados.get("resultados", []))
    return [Concurso.criar(x["concurso"], x["dezenas"], x.get("data")) for x in dados]
