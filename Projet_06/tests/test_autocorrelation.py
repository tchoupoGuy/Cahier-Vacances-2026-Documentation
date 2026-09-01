import numpy as np

from src.models.autocorrelation import autocorrelation, simulate_ma


def test_autocorrelation_matches_statsmodels():
    statsmodels_acf = __import__("statsmodels.tsa.stattools", fromlist=["acf"]).acf
    rng = np.random.default_rng(42)
    serie = rng.normal(200, 20, 200)

    reference = statsmodels_acf(serie, nlags=4)
    assert abs(autocorrelation(serie, 1) - reference[1]) < 1e-9
    assert abs(autocorrelation(serie, 3) - reference[3]) < 1e-9


def test_simulate_ma_echo_fades_after_q_days():
    chocs = np.array([0.0, 10.0, 0.0, 0.0, 0.0])
    serie = simulate_ma(200, [0.8, 0.4], chocs)

    assert len(serie) == 3  # len(chocs) - q
    assert serie[0] == 208.0  # 200 + 0.8*10
    assert serie[1] == 204.0  # 200 + 0.4*10
    assert serie[2] == 200.0  # l'écho s'est éteint après 2 jours


def test_simulate_ma1_theoretical_autocorrelation():
    rng = np.random.default_rng(42)
    chocs = rng.normal(0, 15, 4000)
    serie = simulate_ma(200, [0.5], chocs)

    # valeur théorique d'un MA(1) : r1 = theta / (1 + theta^2)
    assert abs(autocorrelation(serie, 1) - 0.4) < 0.03
    assert abs(autocorrelation(serie, 2)) < 0.03  # un MA(1) n'a pas de mémoire au-delà du retard 1
