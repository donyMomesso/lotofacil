import itertools
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from fechamento_21 import (  # noqa: E402
    TOTAL_CENARIOS_21,
    avaliar_fechamento,
    gerar_fechamento,
    validar_base,
)


class Fechamento21Test(unittest.TestCase):
    def setUp(self):
        self.base = list(range(1, 22))

    def test_base_exige_21_dezenas_unicas(self):
        with self.assertRaises(ValueError):
            validar_base(range(1, 21))
        with self.assertRaises(ValueError):
            validar_base([1] * 21)

    def test_gera_quantidade_sem_duplicatas(self):
        jogos = gerar_fechamento(
            self.base,
            quantidade=8,
            seed=123,
            amostra_cenarios=512,
            shortlist=24,
        )
        self.assertEqual(len(jogos), 8)
        self.assertEqual(len({tuple(jogo) for jogo in jogos}), 8)
        self.assertTrue(all(len(jogo) == 15 for jogo in jogos))

    def test_um_jogo_tem_garantia_minima_nove(self):
        jogo = list(range(1, 16))
        relatorio = avaliar_fechamento(self.base, [jogo])
        self.assertEqual(relatorio.garantia_minima, 9)
        self.assertEqual(relatorio.qtd_15, 1)

    def test_fechamento_completo_garante_15(self):
        jogos = itertools.combinations(self.base, 15)
        relatorio = avaliar_fechamento(self.base, jogos)
        self.assertEqual(relatorio.quantidade_jogos, TOTAL_CENARIOS_21)
        self.assertEqual(relatorio.garantia_minima, 15)
        self.assertEqual(relatorio.pct_15, 100.0)


if __name__ == "__main__":
    unittest.main()
