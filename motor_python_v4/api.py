from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from engine import Concurso, MemoriaAdaptativa, MotorLotofacil, ResultadoGeracao, carregar_historico_json

DATA_PATH = Path(os.getenv("LOTOFACIL_HISTORICO", "historico.json"))
MEM_PATH = Path(os.getenv("LOTOFACIL_MEMORIA", "memoria.json"))
app = FastAPI(title="Cérebro Lotofácil", version="4.0.0")


def obter_motor() -> MotorLotofacil:
    historico = carregar_historico_json(DATA_PATH) if DATA_PATH.exists() else []
    return MotorLotofacil(historico, MemoriaAdaptativa.carregar(MEM_PATH))


class GerarEntrada(BaseModel):
    tamanho_base: int = Field(18, ge=15, le=21)
    quantidade_jogos: int = Field(120, ge=1, le=54264)


class RegistrarEntrada(BaseModel):
    base: list[int]
    jogos: list[list[int]]
    dezenas_sorteadas: list[int]


class ConcursoEntrada(BaseModel):
    concurso: int
    dezenas: list[int]
    data: str | None = None


@app.get("/saude")
def saude():
    return {"status": "ok", "versao": "4.0.0"}


@app.get("/analisar-dezenas")
def analisar_dezenas():
    motor = obter_motor()
    ranking, componentes = motor.pontuar_dezenas()
    return {"ranking": ranking, "componentes": componentes, "pesos": asdict(motor.memoria.pesos)}


@app.post("/gerar-fechamento")
def gerar_fechamento(entrada: GerarEntrada):
    motor = obter_motor()
    try:
        r = motor.gerar(entrada.tamanho_base, entrada.quantidade_jogos)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "base": r.base,
        "combinacoes_completas": r.combinacoes_completas,
        "quantidade_selecionada": len(r.jogos),
        "cobertura_nominal_percentual": r.cobertura_nominal,
        "ranking_dezenas": r.ranking_dezenas,
        "explicacao_base": r.explicacao_base,
        "jogos": [asdict(j) for j in r.jogos],
    }


@app.post("/registrar-resultado")
def registrar_resultado(entrada: RegistrarEntrada):
    motor = obter_motor()
    jogos = [motor.avaliar_jogo(j) for j in entrada.jogos]
    resultado = ResultadoGeracao(tuple(sorted(entrada.base)), jogos, 0, 0.0, [], {})
    registro = motor.registrar_desempenho(resultado, entrada.dezenas_sorteadas)
    motor.recalibrar_pesos()
    motor.memoria.salvar(MEM_PATH)
    return {"registro": registro, "pesos_atualizados": asdict(motor.memoria.pesos)}


@app.post("/adicionar-concurso")
def adicionar_concurso(entrada: ConcursoEntrada):
    concurso = Concurso.criar(entrada.concurso, entrada.dezenas, entrada.data)
    historico = carregar_historico_json(DATA_PATH) if DATA_PATH.exists() else []
    if any(c.concurso == concurso.concurso for c in historico):
        raise HTTPException(status_code=409, detail="Concurso já existente")
    historico.append(concurso)
    historico.sort(key=lambda c: c.concurso)
    DATA_PATH.write_text(__import__("json").dumps([
        {"concurso": c.concurso, "data": c.data, "dezenas": list(c.dezenas)} for c in historico
    ], ensure_ascii=False, indent=2), encoding="utf-8")
    return {"status": "adicionado", "concurso": concurso.concurso}
