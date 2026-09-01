"""Mémoire d'une série temporelle : autocorrélation et simulation d'un processus MA."""

from __future__ import annotations

import numpy as np


def autocorrelation(serie: np.ndarray, lag: int) -> float:
    """Corrélation d'une série avec elle-même, décalée de `lag` pas.

    r proche de 1 : les valeurs décalées de `lag` jours se ressemblent
    beaucoup. r proche de 0 : aucun lien.
    """
    serie = np.asarray(serie, dtype=float)
    ecarts = serie - serie.mean()

    numerateur = np.sum(ecarts[lag:] * ecarts[:-lag])
    denominateur = np.sum(ecarts ** 2)

    return numerateur / denominateur


def simulate_ma(mu: float, thetas: list[float], chocs: np.ndarray) -> np.ndarray:
    """Construit une série MA(q) à partir d'une séquence de chocs aléatoires.

    y_t = mu + eps_t + theta_1 * eps_{t-1} + ... + theta_q * eps_{t-q}

    La série produite est plus courte que `chocs` de q valeurs : il faut q
    chocs passés pour calculer le tout premier point.
    """
    q = len(thetas)
    serie = []

    for t in range(q, len(chocs)):
        valeur = mu + chocs[t]
        for i, theta in enumerate(thetas, start=1):
            valeur += theta * chocs[t - i]
        serie.append(valeur)

    return np.array(serie)
