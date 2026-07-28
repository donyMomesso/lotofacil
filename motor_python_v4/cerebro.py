"""
Cérebro Python — fachada única do Laboratório Estatístico Lotofácil.

Source of truth para:
  - métodos de estudo M1–M9
  - pontuação de dezenas / seleção de base / fechamentos (engine)
  - memória adaptativa
  - checkpoint operacional (consumo pelo Worker / ciclo diário)
  - auditoria histórica (audit_core)

Propósito: estudo estatístico educativo. Não prevê sorteios nem recomenda apostas.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from audit_core import BRAIN_VERSION as AUDIT_BRAIN_VERSION
from audit_core import build_report
from engine import (
    Concurso,
    Filtros,
    MemoriaAdaptativa,
    MotorLotofacil,
    Pesos,
    ResultadoGeracao,
    carregar_historico_json,
)
from metodos import (
    ESPERANCA_TEORICA,
    METODOS,
    gerar_todos_metodos,
    resumo_jogo,
)

CEREBRO_VERSION = "cerebro-python-v2.0.0"
PURPOSE = "historical_education_only"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_payload(payload: object) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def concursos_de_csv_ou_lista(
    valores: Sequence[dict] | Sequence[Concurso],
) -> list[Concurso]:
    out: list[Concurso] = []
    for item in valores:
        if isinstance(item, Concurso):
            out.append(item)
            continue
        concurso = int(item.get("concurso", item.get("contest", 0)))
        raw = item.get("dezenas", item.get("numbers", []))
        if isinstance(raw, str):
            parts = raw.replace("-", " ").replace(",", " ").split()
            dezenas = [int(x) for x in parts]
        else:
            dezenas = list(raw)
        data = item.get("data") or item.get("date")
        out.append(Concurso.criar(concurso, dezenas, data))
    out.sort(key=lambda c: c.concurso)
    return out


class Cerebro:
    """Fachada única: métodos + motor de fechamento + checkpoint."""

    def __init__(
        self,
        historico: Sequence[Concurso] | Sequence[dict],
        memoria: MemoriaAdaptativa | None = None,
        filtros: Filtros | None = None,
        seed: int = 20260728,
    ) -> None:
        self.historico = concursos_de_csv_ou_lista(historico)
        self.memoria = memoria or MemoriaAdaptativa()
        self.filtros = filtros or Filtros()
        self.seed = seed
        self.motor = MotorLotofacil(
            self.historico,
            memoria=self.memoria,
            filtros=self.filtros,
            seed=seed,
        )

    @classmethod
    def de_json(cls, caminho: str | Path, **kwargs) -> "Cerebro":
        return cls(carregar_historico_json(caminho), **kwargs)

    @property
    def ultimo_concurso(self) -> int | None:
        return self.historico[-1].concurso if self.historico else None

    @property
    def total_concursos(self) -> int:
        return len(self.historico)

    def sets_historico(self) -> list[set[int]]:
        return [set(c.dezenas) for c in self.historico]

    # ---- métodos de estudo -------------------------------------------------

    def gerar_metodos(self, seed: int | None = None) -> dict[str, dict]:
        jogos = gerar_todos_metodos(self.sets_historico(), seed=seed if seed is not None else self.seed)
        return {nome: resumo_jogo(dezenas) for nome, dezenas in jogos.items()}

    # ---- motor de base / fechamento ----------------------------------------

    def pontuar_dezenas(self):
        return self.motor.pontuar_dezenas()

    def gerar_fechamento(
        self,
        tamanho_base: int = 18,
        quantidade: int = 120,
    ) -> ResultadoGeracao:
        return self.motor.gerar(tamanho_base=tamanho_base, quantidade=quantidade)

    def registrar_desempenho(self, resultado: ResultadoGeracao, sorteadas: Sequence[int]) -> dict:
        return self.motor.registrar_desempenho(resultado, sorteadas)

    def recalibrar_pesos(self, taxa: float = 0.03) -> Pesos:
        return self.motor.recalibrar_pesos(taxa=taxa)

    # ---- auditoria histórica (sem campos acionáveis) -----------------------

    def auditoria_historica(self, min_training: int = 30) -> dict:
        valores = [
            {"concurso": c.concurso, "data": c.data or "", "dezenas": list(c.dezenas)}
            for c in self.historico
        ]
        return build_report(valores, min_training=min_training)

    # ---- checkpoint operacional (ciclo diário / Worker) --------------------

    def checkpoint_operacional(
        self,
        concurso_alvo: int | None = None,
        seed: int | None = None,
        incluir_fechamento: bool = False,
        tamanho_base: int = 18,
        quantidade_fechamento: int = 30,
    ) -> dict:
        """
        Payload consumido pelo ciclo diário e pelo Worker.
        Inclui jogos de estudo por método (já existentes no fluxo atual).
        NÃO é previsão — é material de laboratório.
        """
        if not self.historico:
            raise ValueError("Histórico vazio: impossível gerar checkpoint.")

        ultimo = self.historico[-1]
        alvo = concurso_alvo or (ultimo.concurso + 1)
        metodos = self.gerar_metodos(seed=seed)

        ranking, componentes = self.pontuar_dezenas()
        # ranking interno do motor (estudo); não publicar como "previsão"
        ranking_resumo = [
            {"dezena": d, "nota": nota}
            for d, nota in ranking[:25]
        ]

        payload: dict = {
            "ok": True,
            "purpose": PURPOSE,
            "cerebro_version": CEREBRO_VERSION,
            "audit_brain_version": AUDIT_BRAIN_VERSION,
            "source_of_truth": "python",
            "generated_at": _utc_now(),
            "ultimo_concurso": ultimo.concurso,
            "ultimo_data": ultimo.data,
            "total_concursos": self.total_concursos,
            "concurso_alvo": alvo,
            "esperanca_teorica": ESPERANCA_TEORICA,
            "metodos_disponiveis": list(METODOS),
            "jogos_estudo": metodos,
            "pesos_memoria": asdict(self.memoria.pesos),
            "memoria_versao": self.memoria.versao,
            "ranking_estudo_dezenas": ranking_resumo,
            "aviso": (
                "Material de laboratório estatístico. "
                "Sorteios são independentes; esperança teórica = 9 acertos. "
                "Não usar como recomendação de aposta."
            ),
        }

        if incluir_fechamento:
            geracao = self.gerar_fechamento(tamanho_base, quantidade_fechamento)
            payload["fechamento_estudo"] = {
                "base": list(geracao.base),
                "quantidade_jogos": len(geracao.jogos),
                "combinacoes_completas": geracao.combinacoes_completas,
                "cobertura_nominal_pct": geracao.cobertura_nominal,
                "jogos": [
                    {
                        "dezenas": list(j.jogo),
                        "nota": j.nota,
                        "soma": j.soma,
                        "pares": j.pares,
                        "primos": j.primos,
                        "moldura": j.moldura,
                        "linhas": j.linhas,
                        "maior_sequencia": j.maior_sequencia,
                        "repetidas_anterior": j.repetidas_anterior,
                    }
                    for j in geracao.jogos
                ],
            }

        # hash sem o próprio campo hash
        payload["checkpoint_hash"] = _hash_payload(payload)
        return payload

    def salvar_checkpoint(
        self,
        caminho: str | Path,
        **kwargs,
    ) -> dict:
        payload = self.checkpoint_operacional(**kwargs)
        path = Path(caminho)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return payload


def saude() -> dict:
    return {
        "status": "ok",
        "cerebro_version": CEREBRO_VERSION,
        "audit_brain_version": AUDIT_BRAIN_VERSION,
        "purpose": PURPOSE,
        "source_of_truth": "python",
        "metodos": list(METODOS),
        "esperanca_teorica": ESPERANCA_TEORICA,
    }
