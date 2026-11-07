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
**Ce que j'ai compris (une phrase, avec mes mots) :** Ce projet suit le travail d'un market maker (prix juste, carnet, flux d'ordres, risque). Chaque étape correspond à une question d'entretien quant, et la règle « tests + explication orale » m'entraîne aussi à l'oral.
**Question à laquelle je ne sais pas encore répondre :** 

## Jeudi 22 – samedi 24 octobre

**Date / durée :** jeu. 22 au sam. 24 oct. [durées à compléter]
**Module et fonction(s) :** P0, théorie sur papier (pas de code encore).
**Ce que j'ai fait :** reconstruit le chemin du mouvement brownien au lemme d'Itô : marche aléatoire, théorème central limite, (dW)² = dt, formule de Taylor, lemme d'Itô sur ln S, schéma exact du GBM, inégalité de Jensen, puis prix risque-neutre (réplication, pourquoi μ est remplacé par r). Corrections de mes feuilles papier. Premier exemple chiffré de Monte Carlo (3 trajectoires, 2 pas).
**Ce qui m'a bloqué (et combien de temps) :** plusieurs points d'affilée : pourquoi (dW)² = dt, pourquoi la règle de dérivation ordinaire est fausse avec du bruit, le passage à Jensen, la réplication, et le vocabulaire Monte Carlo (« trajectoire » contre « pas », pourquoi il y a plusieurs S1). La théorie a pris environ 2 jours de plus que prévu.
**Ce que j'ai compris (une phrase, avec mes mots) :** Avec du bruit, la dérivation ordinaire est fausse parce que (dW)² = dt n'est pas négligeable. Pour ln S, ça donne un terme −σ²/2 qui vient de la concavité de ln. La loi de S_T sous la probabilité risque-neutre a pour drift r et non μ : on se couvre par réplication, donc le portefeuille sans risque rapporte r.
**Question à laquelle je ne sais pas encore répondre :** [à compléter]

## Dimanche 25 octobre

**Date / durée :** dim. 25 oct., environ 3 h.
**Module et fonction(s) :** P0, `simulate_gbm` et `simulate_gbm_at_times`.
**Ce que j'ai fait :** codé le schéma exact du GBM (`exp((mu - sigma²/2)·dt + sigma·sqrt(dt)·Z)`), d'abord avec un pas constant, puis avec des dates irrégulières (un `dt` par pas, `np.diff`, `ValueError` si les dates ne sont pas strictement croissantes). 9 tests verts.
**Ce qui m'a bloqué (et combien de temps) :** la notation numpy (`S[:, j]`, `rng.standard_normal((n_paths, n_steps))`) et les parenthèses du `ValueError` (environ 1 h en tout). Aide de niveau 2 (diagnostic).
**Ce que j'ai compris (une phrase, avec mes mots) :** Avec le schéma exact, la loi de S à une date ne dépend pas du nombre de pas, parce que des incréments gaussiens indépendants se somment en une gaussienne dont les variances s'additionnent. Euler, lui, a une erreur de discrétisation qui dépend de dt.
**Question à laquelle je ne sais pas encore répondre :** pourquoi Euler converge mal et où l'erreur apparaît exactement ?

## Lundi 26 octobre

**Date / durée :** lun. 26 oct., environ 4 h (15 h 30 à 19 h 30).
**Module et fonction(s) :** P0, `bs_call`, `mc_call_price` (sans antithétiques), `scripts/p0_fair_price.py`.
**Ce que j'ai fait :** dérivé la formule de Black-Scholes (S0·N(d1) − K·e^{−rT}·N(d2)) à partir de E[(S_T − K)⁺], codé `bs_call` (10,4506 pour S=K=100, r=5 %, σ=20 %, T=1) et `mc_call_price` (prix et erreur standard σ/√N). Le script compare les deux prix et trace 20 trajectoires. 4 tests verts de plus. Décision de la journée : pause du projet après P0 pour passer aux entretiens (refus de Squarepoint et Santander).
**Ce qui m'a bloqué (et combien de temps) :** (1) la dérivation de BS : symétrie de Z, densité, complétion du carré (environ 1 h 30) ; (2) parenthèses de d2 dans `bs_call` (10 min) ; (3) dans `mc_call_price`, une double boucle et l'écart-type calculé sur le prix au lieu du tableau des gains (20 min).
**Ce que j'ai compris (une phrase, avec mes mots) :** Le prix d'un call est la moyenne actualisée du gain sous la probabilité risque-neutre. Black-Scholes la calcule exactement (10,4506). Monte Carlo l'approche avec une erreur en σ/√N : le bon test est que la formule tombe dans l'intervalle estimation ± 1,96·SE.
**Question à laquelle je ne sais pas encore répondre :** pourquoi utiliser Z et −Z (variables antithétiques) réduit-il l'erreur ?

## Antithétiques (commit a23f1dd, ## Mardi 27 octobre)

**Date / durée :** [date]
**Module et fonction(s) :** P0, `mc_call_price` avec variables antithétiques.
**Ce que j'ai fait :** pour chaque tirage Z, j'utilise aussi −Z et je moyenne les deux gains. J'ai comparé l'erreur standard avant et après : [mes deux valeurs de SE]. omparaison à N = 100 000 et seed = 0 : SE 0,0465 sans antithétiques, 0,0331 avec (−29 %). Les deux intervalles contiennent le prix Black-Scholes (10,4506).
**Ce qui m'a bloqué (et combien de temps) :** [à compléter]
**Ce que j'ai compris (une phrase, avec mes mots) :** Le gain d'un call est monotone en Z, donc les gains de Z et de −Z sont négativement corrélés. La variance d'une moyenne de deux variables est (Var/2)·(1+ρ), donc elle baisse quand ρ < 0. Point d'attention : l'erreur standard se calcule sur les moyennes de paires, pas sur tous les gains comme s'ils étaient indépendants. Le rapport des variances (0,0331/0,0465)² ≈ 0,5 correspond à 1+ρ, donc ρ ≈ −0,5 entre le gain de Z et celui de −Z.
**Question à laquelle je ne sais pas encore répondre :** que se passe-t-il pour un payoff non monotone (par exemple un straddle) ?

## Mardi 27 octobre

**Date / durée :** mar. 27 oct. [durée]
**Module et fonction(s) :** P1, design du carnet sur papier.
**Ce que j'ai fait :** décidé de continuer le projet (P1) plutôt que de passer aux entretiens cette semaine-là. Comparé un tas et une liste triée en calculant le coût de scénarios précis.
**Ce qui m'a bloqué (et combien de temps) :** la somme contre le produit en Big-O, et le coût d'une annulation au milieu d'un tas (il faut d'abord la retrouver, donc O(n)).
**Ce que j'ai compris (une phrase, avec mes mots) :** Des étapes qui se suivent s'additionnent (le terme dominant l'emporte), seule une répétition imbriquée multiplie. Tas : meilleur prix O(1), insertion O(log n), retrait du meilleur O(log n). Liste triée : O(1), O(n), O(n). Le tas gagne parce qu'on n'a besoin que du meilleur prix, pas d'un ordre total.
**Question à laquelle je ne sais pas encore répondre :** à partir de quelle taille de carnet la différence se voit-elle en pratique ?

## Mercredi 28 octobre – vendredi 6 novembre : le code (commit fb5cefc, 17/17 tests)

**Date / durée :** mer. 28 oct. (session principale, soirée difficile), finition le ven. 6 nov. [durées]
**Module et fonction(s) :** `orderbook.py` : `add_limit_order`, `add_market_order`, `_apparier`, `best_bid`, `best_ask`, `cancel` et les accesseurs.
**Ce que j'ai fait :** deux tas (bids avec prix en négatif), un dictionnaire {id: [côté, prix, quantité restante]}, un compteur d'ids, priorité prix puis temps grâce aux tuples (clé, id). Une fonction commune `_apparier(side, qty, limite)` pour les deux types d'ordres (l'ordre au marché a une limite infinie). Annulation paresseuse.
**Ce qui m'a bloqué (et combien de temps) :** c'est l'étape la plus longue. Bugs : oubli de `self.`, `side == "buy" or "sell"` (toujours vrai), `is not int` au lieu de `isinstance`, `append` au lieu de `heappush`, id et quantité confondus dans le tas, `self.asks = self.bids` (même liste), méthode stockée avec parenthèses (appel) au lieu de sans, `break` mal placé. J'ai aussi mélangé « limite / marché » (le type d'ordre) et « maker / taker » (le rôle).
**Ce que j'ai compris (une phrase, avec mes mots) :** L'échange se fait au prix du maker (l'ordre qui attendait), parce que le taker ne fixe qu'une limite. L'annulation paresseuse supprime l'ordre du dictionnaire en O(1) et laisse le tas intact. L'entrée morte est retirée en O(log n) quand elle arrive au sommet, donc chaque ordre est retiré au plus une fois. Deux invariants : best_bid < best_ask (strict) et reçu = exécuté + posé + abandonné.
**Question à laquelle je ne sais pas encore répondre :** comment un vrai marché gère-t-il la priorité à prix égal quand les ordres ont des tailles ou des types différents ?

## Vendredi 6 novembre : l'expérience (commit f1739c2)

**Date / durée :** ven. 6 nov. [5H]
**Module et fonction(s) :** `scripts/p1_book.py` (`niveaux`, `afficher`, rejeu de 20 actions, graphique, `chrono`).
**Ce que j'ai fait :** rejoué 20 actions et vérifié les résultats clés à la main (action 9 : [(101,2,5),(102,3,6),(102,3,7)] ; annulation du 3 : True puis False ; action 18 : un ordre limite qui échange puis se pose). Tracé le meilleur bid/ask. Chronométré : 100 000 ordres limites en 0,209 s (2,09 µs/op), 100 000 opérations mélangées en 0,194 s (1,94 µs/op), MacBook, Python 3.13.
**Ce qui m'a bloqué (et combien de temps) :** `enumerate(liste, 1)`, f-strings et `join`, `rng.integers` (borne haute exclue, `np.int64` n'est pas un `int`), où appeler `chrono()`.
**Ce que j'ai compris (une phrase, avec mes mots) :** Le temps total ne prouve pas la complexité, il la rend seulement plausible. Pour prouver O(log n) il faudrait mesurer le temps par opération en fonction de la taille du carnet. Ligne de CV : « Carnet d'ordres en Python (tas + suppression paresseuse) : 100 000 opérations en 0,19 s sur un MacBook (~2 µs/op) ».
**Question à laquelle je ne sais pas encore répondre :** le temps par opération reste-t-il quasi plat si le carnet contient 10 fois plus d'ordres posés ? (Non mesuré.)

## Vendredi 6 novembre (soirée) : P2, début

**Date / durée :** ven. 6 nov., de 18 h à 21 h 45 environ, avec des pauses.
**Module et fonction(s) :** P2, feuille de maths (étapes 1 à 3), `poisson_arrival_times`, `merge_event_streams`.
**Ce que j'ai fait :**
- Démontré à la main que le temps d'attente entre deux clients est exponentiel : P(T > t) = P(N(t) = 0) = e^(−λt). Calculé sa densité, son espérance 1/λ et son écart-type 1/λ.
- Montré l'absence de mémoire : P(T > s+u | T > s) = P(T > u).
- Montré que pour deux flux indépendants, le premier événement arrive après un temps exponentiel de taux λ_b + λ_s, et que c'est un achat avec la probabilité λ_b / (λ_b + λ_s) (formule des probabilités totales).
- Codé `poisson_arrival_times` (somme cumulée de durées exponentielles, jusqu'à l'horizon) : tests verts.
- Codé `merge_event_streams` (fusion de flux triés avec un tas de tuples (instant, rang, indice, étiquette)) : tests verts.
**Ce qui m'a bloqué (et combien de temps) :**
- Poisson contre exponentielle : j'ai mis du temps à voir que ce sont deux regards sur le même processus (on compte les clients, ou on attend le suivant).
- J'ai voulu additionner les **taux** au lieu des **durées** pour fabriquer les instants d'arrivée.
- `for i in range(horizon+1)` au lieu d'un `while` : on ne sait pas à l'avance combien de clients arrivent.
- `if not tableau` plante sur un tableau numpy (alors que ça marche sur une liste) : il faut `len(tableau) == 0`.
- Le design du tuple du tas (quoi mettre, dans quel ordre) et la logique « on remet le suivant du même flux », surtout `streams[etiquette][indice]`. Environ 1 h 30 sur `merge_event_streams`.
**Ce que j'ai compris (une phrase, avec mes mots) :** Les temps entre clients sont exponentiels et sans mémoire, donc on fabrique les arrivées en additionnant des durées tirées au hasard. Pour fusionner plusieurs flux déjà triés, le tas contient le prochain événement de chaque flux : le plus petit est forcément le prochain de tous, et on remet ensuite le suivant du flux qui vient de sortir.
**Question à laquelle je ne sais pas encore répondre :** comment fabriquer deux flux vraiment indépendants (achats et ventes) à partir d'une seule graine, tout en restant reproductible ?

## Samedi 7 novembre : P2, fin

**Date / durée :** sam. 7 nov., de 11 h 45 à 13 h 25 environ.
**Module et fonction(s) :** P2, `generate_order_flow`, `scripts/p2_flow.py` (trois expériences).
**Ce que j'ai fait :**
- Codé `generate_order_flow` : deux flux de Poisson indépendants (deux graines tirées d'un même `seed` avec `rng.integers`), fusionnés par `merge_event_streams`. 9/9 tests verts.
- Expérience 1 : les temps d'attente (λ = 2) suivent la densité λ·e^(−λt). Moyenne mesurée 0,497 pour 0,5 attendu.
- Expérience 2 : le nombre de clients sur 5 s (λ = 2) suit une loi de Poisson de paramètre 10. Moyenne 10,01 et variance 9,81 (théorie : égales à 10).
- Expérience 3 : avec λ_b = 3 et λ_s = 1, la fréquence des achats est 0,7508 pour 0,75 attendu (erreur standard 0,003).
**Ce qui m'a bloqué (et combien de temps) :**
- Les deux flux doivent être indépendants : avec la même graine, achats et ventes auraient les mêmes instants.
- Une variable passée comme argument nommé (`rate = 2` dans l'appel) n'existe pas comme variable : il faut la définir avant.
- `sum(1 for _, cote in flux if cote == "buy")` : la structure avec condition, et le fait qu'un couple se défait en autant de noms qu'il a d'éléments. Environ 30 min sur les expériences au total.
**Ce que j'ai compris (une phrase, avec mes mots) :** Un flux de Poisson se simule en additionnant des durées exponentielles, et on peut le vérifier de trois façons indépendantes : la loi des attentes (exponentielle), la loi des comptes (Poisson, moyenne = variance), et la part des achats (λ_b / (λ_b + λ_s)). La comparaison d'une simulation à la théorie doit toujours se faire avec une erreur standard, pas à l'œil.
**Question à laquelle je ne sais pas encore répondre :** que se passe-t-il si les taux ne sont pas constants dans la journée (ouverture et clôture plus actives), ou si les ordres arrivent par grappes ? Le Poisson homogène ne suffit plus.


**Défense orale P2 (7 nov., en anglais, de mémoire) :**
- Question 4 (attente restante de 10 minutes) : comprise. Réponse : 5 minutes, par absence de mémoire.
- Question 2 : l'importance pour la simulation est comprise (à chaque tour on tire une durée exponentielle indépendante du passé). La démonstration en 3 lignes (conditionnelle, simplification du numérateur, calcul avec e^(−λt)) est encore à refaire de mémoire.
- Question 1 : à refaire. Erreur : j'ai écrit « arrive à l'instant t » au lieu de « arrive après t » (T > t ⇔ N(t) = 0 ⇔ aucun client dans [0, t]). Il faut donner la valeur e^(−λt) et dire pourquoi toutes les durées sont exponentielles (le processus repart de zéro).
- Question 3 : la loi (exponentielle de taux λ_b + λ_s) et la formule λ_b/(λ_b + λ_s) sont justes. Erreurs : « on additionne les taux » sans dire que c'est le produit des probabilités qui l'explique, et « intégration par parties » alors que c'est une intégrale d'exponentielle simple.
- Question 5 : méthode et O(N log k) justes. Erreurs : condition d'arrêt inversée (« tant que le tas n'est pas vide »), et j'ai oublié de comparer avec « concaténer puis trier » en O(N log N), moins bon quand k est petit devant N.