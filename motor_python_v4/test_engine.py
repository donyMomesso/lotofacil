from engine import Concurso, MotorLotofacil


def historico():
    bases = [
        [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
        [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16],
        [1,3,5,7,9,11,13,15,17,19,21,22,23,24,25],
    ]
    return [Concurso.criar(i + 1, x) for i, x in enumerate(bases)]


def test_combinacoes_18():
    motor = MotorLotofacil(historico())
    resultado = motor.gerar(18, 10)
    assert resultado.combinacoes_completas == 816
    assert len(resultado.base) == 18
    assert len(resultado.jogos) <= 10


def test_jogos_validos():
    motor = MotorLotofacil(historico())
    base, _, _ = motor.selecionar_base(18)
    jogos = motor.gerar_fechamento(base, 20)
    assert all(len(j.jogo) == 15 for j in jogos)
    assert all(motor.jogo_valido(j) for j in jogos)
