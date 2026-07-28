"""
Ponte scripts/ → motor_python_v4 (Cérebro Python).

Garante que lotofacil_lib e o ciclo diário usem a mesma implementação
de métodos M1–M9 sem depender de PYTHONPATH manual.
"""
from __future__ import annotations

import sys
from pathlib import Path

_MOTOR_DIR = Path(__file__).resolve().parent.parent / "motor_python_v4"


def ensure_motor_on_path() -> Path:
    motor = _MOTOR_DIR
    motor_str = str(motor)
    if motor_str not in sys.path:
        sys.path.insert(0, motor_str)
    return motor


def gerar_metodos_cerebro(resultados_sets, seed=None):
    """
    resultados_sets: lista de set/list de 15 dezenas (histórico até o concurso
    imediatamente anterior ao alvo).
    Retorna dict[str, set[int]] com M1–M9.
    """
    ensure_motor_on_path()
    from metodos import gerar_todos_metodos  # type: ignore

    return gerar_todos_metodos(resultados_sets, seed=seed)
