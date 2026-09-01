# Projet 06 — Séries temporelles : combien de glaces préparer demain ?

Source : `Cahier-Vacances-2026/Projet_06/Projet_06.ipynb`

## 🎯 En une phrase

Une série temporelle a de la mémoire : les modèles AR (inertie des valeurs passées) et MA (écho des surprises passées) capturent chacun une forme différente de cette mémoire, et les combiner (ARMA) donne des prévisions plus fines que chacun séparément.

## 1. Explique-le à un enfant de 12 ans

Bruno vend des glaces sur la plage, et chaque matin il doit deviner combien il va en vendre. Il n'a qu'un carnet : le nombre de glaces vendues chaque jour depuis quatre étés. Pas de météo, pas de nombre de touristes, juste une suite de chiffres dans l'ordre du temps.

L'idée derrière les modèles de ce projet : les ventes d'aujourd'hui ne tombent pas du ciel, elles ressemblent souvent à celles d'hier (s'il a beaucoup vendu hier, il vendra probablement pas mal aujourd'hui aussi — c'est l'**inertie**), et un jour exceptionnel laisse un petit écho les jours suivants (un car de touristes qui parle de la plage à ses amis, par exemple — c'est la **surprise** qui se propage un peu). Un modèle qui capture l'inertie s'appelle AR (AutoRegressive), un modèle qui capture l'écho des surprises s'appelle MA (Moving Average — attention, ça n'a rien à voir avec la "moyenne mobile" de tous les jours). En combinant les deux, on obtient un modèle ARMA, capable de mieux prévoir la semaine de Bruno qu'une simple moyenne ou qu'un "comme hier".

## 2. Le vocabulaire technique

| Terme | Définition simple | Analogie |
|---|---|---|
| **Série temporelle** | Une suite de valeurs numériques ordonnées dans le temps | Le carnet de ventes de Bruno, jour après jour |
| **Autocorrélation (ACF)** | La corrélation d'une série avec elle-même, décalée de quelques jours | Est-ce que les ventes d'aujourd'hui ressemblent à celles d'il y a 3 jours ? D'il y a 7 jours ? |
| **AR (AutoRegressive)** | Les valeurs d'aujourd'hui dépendent directement des valeurs passées | "Les ventes d'aujourd'hui ressemblent à celles d'hier" — l'inertie |
| **MA (Moving Average)** | Les valeurs d'aujourd'hui dépendent des erreurs (chocs) passées, pas des valeurs passées | Un jour exceptionnel laisse un écho quelques jours, comme le bouche-à-oreille |
| **Choc / résidu** ($\varepsilon_t$) | La part d'une valeur que rien ne permettait de prévoir | L'orage soudain ou le car de touristes imprévu qui change les ventes du jour |
| **ARMA(p, q)** | La combinaison d'un modèle AR d'ordre p et d'un modèle MA d'ordre q | Prendre en compte à la fois l'inertie ET l'écho des surprises |
| **AIC** | Un score qui récompense un modèle précis avec le moins de coefficients possible | Une note qui pénalise la complexité inutile : à qualité égale, le modèle le plus simple gagne |
| **Test de Ljung-Box** | Un test statistique qui vérifie si ce qui reste après le modèle (les résidus) est du bruit pur ou contient encore de l'information | Vérifier qu'il ne reste plus de motif caché dans les erreurs du modèle : si oui, le modèle n'a pas tout capté |
| **`get_forecast`** | La méthode qui prolonge une série ajustée de plusieurs jours dans le futur | Demander au modèle : "et la semaine prochaine, ça donnerait quoi ?" |

## 3. Comment ça marche, en détail

1. **On établit une baseline simple** (par exemple "demain = moyenne historique" ou "demain = comme hier") pour avoir un point de comparaison honnête. Sans baseline, impossible de savoir si un modèle plus complexe apporte vraiment quelque chose.
2. **On découpe train/test dans l'ordre du temps, jamais au hasard.** Contrairement à d'autres problèmes de Machine Learning, mélanger les dates n'aurait aucun sens : on doit prédire le futur à partir du passé, donc le test doit être la fin de la série, jamais des dates éparpillées.
3. **On mesure la mémoire de la série avec l'autocorrélation (ACF).** Si la corrélation entre la série et elle-même décalée de k jours s'effondre brutalement après un certain nombre de jours, c'est la signature d'un MA(q). Si elle décroît progressivement sans jamais tomber à zéro, c'est le signe qu'un terme AR est nécessaire.
4. **On ajuste d'abord un MA seul**, la solution la plus naturelle vu le comportement observé sur l'ACF. On comprend sa limite : sa mémoire s'arrête net après q jours — au-delà, ses prévisions retombent immédiatement sur la moyenne, sans nuance.
5. **On ajoute un terme AR pour obtenir un ARMA.** Un seul coefficient AR suffit à créer une mémoire qui s'atténue progressivement au lieu de s'arrêter net, car l'influence se transmet de proche en proche (l'écart d'aujourd'hui hérite d'une fraction de l'écart d'hier, qui hérite lui-même de l'avant-veille).
6. **On compare objectivement les modèles avec l'AIC et le test de Ljung-Box**, pas seulement à l'œil sur un graphique : l'AIC récompense la simplicité à qualité égale, et le test de Ljung-Box vérifie que les résidus du modèle ne cachent plus de structure exploitable.
7. **On produit une vraie prévision utile pour Bruno** : combien de glaces pour les 7 prochains jours, avec `get_forecast(steps=7)`.

## 4. Le code clé, annoté

```python
from statsmodels.tsa.arima.model import ARIMA

# MA(3) pur : order=(p, d, q) = (0, 0, 3)
#  p = 0 : pas de terme AR
#  d = 0 : pas de différenciation nécessaire ici
#  q = 3 : mémoire des 3 derniers chocs
resultat_ma = ARIMA(train, order=(0, 0, 3), trend="c").fit()
```

```python
# ARMA(1,1) : un seul coefficient AR + un seul coefficient MA
resultat_arma = ARIMA(train, order=(1, 0, 1), trend="c").fit()

print(resultat_arma.aic)   # plus bas = meilleur compromis précision / simplicité
```

```python
# Prévoir les 7 prochains jours
semaine_ma = resultat_ma.get_forecast(steps=7).predicted_mean
semaine_arma = resultat_arma.get_forecast(steps=7).predicted_mean
# Le MA(3) retombe sur la moyenne dès le 4e jour (sa mémoire s'arrête net après 3 jours)
# L'ARMA(1,1) revient vers la moyenne progressivement, grâce au terme AR
```

## 5. Les pièges et questions qui bloquent

- **Le "MA" d'ARMA n'est PAS la moyenne mobile de pandas.** C'est une régression sur les erreurs passées, pas sur les valeurs passées — un faux ami classique à ne pas confondre avec `.rolling(7).mean()`.
- **Découper train/test au hasard serait une erreur grave ici**, contrairement à d'autres projets de Machine Learning : une série temporelle doit être découpée dans l'ordre chronologique, sinon on "prédirait" le passé à partir du futur.
- **Un MA(q) a une mémoire strictement bornée à q jours.** Passé ce délai, ses prévisions sont plates (juste la moyenne) — comprendre cette limite est ce qui justifie de passer à l'ARMA.
- **Un AIC plus bas ne veut pas dire "modèle parfait"**, seulement "meilleur compromis entre précision et nombre de coefficients" parmi les modèles comparés. Le test de Ljung-Box sur les résidus est le vrai juge de qualité.
- **`order=(p, d, q)`** : oublier ce que représente chaque lettre (AR, différenciation, MA) est une source d'erreur fréquente en pratique.

## 6. Test de Feynman

- Explique la différence entre AR et MA sans utiliser les mots "autorégressif" ni "moyenne mobile" dans ta définition.
- Pourquoi le "MA" d'ARMA n'a rien à voir avec une moyenne glissante calculée avec pandas ?
- Pourquoi ne peut-on pas découper une série temporelle en train/test de façon aléatoire ?
- Comment reconnaît-on sur un graphique d'autocorrélation qu'un MA(q) suffit, plutôt qu'un modèle avec un terme AR ?
- Pourquoi le MA(3) "aplatit" ses prévisions après 3 jours, alors que l'ARMA(1,1) continue de refléter une tendance ?

## 7. Pour aller plus loin

- Ajouter la saisonnalité hebdomadaire (modèle **SARIMA**, argument `seasonal_order=(P, D, Q, 7)` de `statsmodels`).
- Ajouter la température comme variable explicative externe via `exog=` avec un modèle **SARIMAX**.
