# Journal de bord

Une entrée par session. Cinq lignes suffisent. Ce journal sert à te souvenir de ce que tu as appris et à préparer les questions d'entretien (« raconte-moi un moment où tu as été bloqué »).

## Modèle d'entrée

**Date / durée :**
**Module et fonction(s) :**
**Ce que j'ai fait :**
**Ce qui m'a bloqué (et combien de temps) :**
**Ce que j'ai compris (une phrase, avec mes mots) :**
**Question à laquelle je ne sais pas encore répondre :**

---

## Mercredi 21 octobre

**Date / durée :** mer. 21 oct., soirée. 
**Module et fonction(s) :** choix du projet et mise en place.
**Ce que j'ai fait :** choisi le projet C (« un market maker, du carnet d'ordres au risque »), en trois phases ; installé le kit quant-lab (107 tests dont 53 pour la phase 1) ; fixé la règle : une étape est finie quand les tests passent ET que je sais l'expliquer à voix haute.
**Ce qui m'a bloqué (et combien de temps) :** 
**Ce que j'ai compris (une phrase, avec mes mots) :** [à toi : pourquoi ce projet sert aussi la préparation aux entretiens]
**Question à laquelle je ne sais pas encore répondre :** 

## Jeudi 22 – samedi 24 octobre

**Date / durée :** jeu. 22 au sam. 24 oct. [durées à compléter]
**Module et fonction(s) :** P0, théorie sur papier (pas de code encore).
**Ce que j'ai fait :** reconstruit le chemin du mouvement brownien au lemme d'Itô : marche aléatoire, théorème central limite, (dW)² = dt, formule de Taylor, lemme d'Itô sur ln S, schéma exact du GBM, inégalité de Jensen, puis prix risque-neutre (réplication, pourquoi μ est remplacé par r). Corrections de mes feuilles papier. Premier exemple chiffré de Monte Carlo (3 trajectoires, 2 pas).
**Ce qui m'a bloqué (et combien de temps) :** plusieurs points d'affilée : pourquoi (dW)² = dt, pourquoi la règle de dérivation ordinaire est fausse avec du bruit, le passage à Jensen, la réplication, et le vocabulaire Monte Carlo (« trajectoire » contre « pas », pourquoi il y a plusieurs S1). La théorie a pris environ 2 jours de plus que prévu.
**Ce que j'ai compris (une phrase, avec mes mots) :** [à toi : par exemple « le −σ²/2 vient du fait que ln est concave et que (dW)² vaut dt »]
**Question à laquelle je ne sais pas encore répondre :** [à compléter]

## Dimanche 25 octobre

**Date / durée :** dim. 25 oct., environ 3 h.
**Module et fonction(s) :** P0, `simulate_gbm` et `simulate_gbm_at_times`.
**Ce que j'ai fait :** codé le schéma exact du GBM (`exp((mu - sigma²/2)·dt + sigma·sqrt(dt)·Z)`), d'abord avec un pas constant, puis avec des dates irrégulières (un `dt` par pas, `np.diff`, `ValueError` si les dates ne sont pas strictement croissantes). 9 tests verts.
**Ce qui m'a bloqué (et combien de temps) :** la notation numpy (`S[:, j]`, `rng.standard_normal((n_paths, n_steps))`) et les parenthèses du `ValueError` (environ 1 h en tout). Aide de niveau 2 (diagnostic).
**Ce que j'ai compris (une phrase, avec mes mots) :** [à toi : par exemple « avec le schéma exact, la loi du prix à une date ne dépend pas du nombre de pas, parce que les incréments gaussiens indépendants s'additionnent »]
**Question à laquelle je ne sais pas encore répondre :** pourquoi Euler converge mal et où l'erreur apparaît exactement ?

## Lundi 26 octobre

**Date / durée :** lun. 26 oct., environ 4 h (15 h 30 à 19 h 30).
**Module et fonction(s) :** P0, `bs_call`, `mc_call_price` (sans antithétiques), `scripts/p0_fair_price.py`.
**Ce que j'ai fait :** dérivé la formule de Black-Scholes (S0·N(d1) − K·e^{−rT}·N(d2)) à partir de E[(S_T − K)⁺], codé `bs_call` (10,4506 pour S=K=100, r=5 %, σ=20 %, T=1) et `mc_call_price` (prix et erreur standard σ/√N). Le script compare les deux prix et trace 20 trajectoires. 4 tests verts de plus. Décision de la journée : pause du projet après P0 pour passer aux entretiens (refus de Squarepoint et Santander).
**Ce qui m'a bloqué (et combien de temps) :** (1) la dérivation de BS : symétrie de Z, densité, complétion du carré (environ 1 h 30) ; (2) parenthèses de d2 dans `bs_call` (10 min) ; (3) dans `mc_call_price`, une double boucle et l'écart-type calculé sur le prix au lieu du tableau des gains (20 min).
**Ce que j'ai compris (une phrase, avec mes mots) :** [à toi : par exemple « le prix d'un call, c'est la moyenne actualisée du gain sous la probabilité risque-neutre ; Black-Scholes la calcule exactement, Monte Carlo l'approche avec une erreur en 1/√N »]
**Question à laquelle je ne sais pas encore répondre :** pourquoi utiliser Z et −Z (variables antithétiques) réduit-il l'erreur ?
