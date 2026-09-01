"""Diagnostic des résidus : reste-t-il de l'information non captée par le modèle ?"""

from __future__ import annotations


def ljung_box_pvalue(fitted_result, lags: int = 10) -> float:
    """p-value du test de Ljung-Box sur les résidus d'un modèle ajusté.

    p > 0.05 : les résidus ressemblent à du bruit pur, le modèle n'a rien
    laissé sur la table. p <= 0.05 : il reste une structure exploitable,
    le modèle est incomplet.
    """
    from statsmodels.stats.diagnostic import acorr_ljungbox

    result = acorr_ljungbox(fitted_result.resid, lags=[lags], return_df=True)
    return float(result["lb_pvalue"].iloc[0])
