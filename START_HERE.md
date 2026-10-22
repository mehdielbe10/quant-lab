# START HERE — « Un market maker, du carnet d'ordres au risque »

## Ce qu'on construit, et pourquoi

Une **petite bourse simulée**, et toi dans le rôle du **teneur de marché** (market maker). Tu affiches un prix d'achat et un prix de vente ; des clients arrivent au hasard ; certains en savent plus que toi ; tu dois gagner de l'argent sans te faire ruiner par ton stock. Tout est écrit par toi, testé, et chaque résultat est vérifié par la théorie.

**La question du projet :** *comment un teneur de marché doit-il coter, que lui coûtent les clients informés, quel risque son stock lui fait-il courir, et comment sait-il que sa stratégie vaut mieux que la chance ?*

**Ce que ce n'est pas :** une stratégie qui gagnerait de l'argent sur un vrai marché. C'est un laboratoire. Sa valeur est ce que tu y apprends et ce que tu sais en dire.

## Les trois phases

| Phase | Étapes | Ce que tu construis |
|---|---|---|
| **1 – Le moteur** *(ce kit)* | P0 le prix juste · P1 le carnet d'ordres · P2 le flux de clients · P3 le premier market maker | Un simulateur qui tourne de bout en bout, avec le risque de stock calculé exactement |
| **2 – L'intelligence** *(kit livré quand tu y arrives)* | P4 clients informés (Bayes) et régression · P5 cotations optimales | Un market maker qui s'adapte aux informés |
| **3 – Le risque et le jugement** *(plus tard, selon ton temps)* | Plusieurs actifs corrélés, couverture, jugement honnête, bonus | Un système complet et évalué sans se mentir |

Les phases 1 et 2 forment déjà un projet complet. La phase 3 l'enrichit.

## Tes règles

**Aucune échéance ne prime sur l'apprentissage.** Les durées ci-dessous sont des repères. Une étape est finie quand **(a)** les tests passent **et (b)** tu sais l'expliquer à voix haute, sans notes (questions de défense dans `LEARNING_CARDS.md`, tu t'enregistres 3 minutes). Pas avant.

**La feuille d'abord.** Chaque étape commence par des maths **sur papier**, que tu photographies dans `notes/`. Le code est la traduction de ta feuille.

**Tu écris le code toi-même.** Les fichiers de `src/quantlab/` sont vides (`NotImplementedError`) et les tests sont ta consigne. `lab.py` et les fichiers de la phase 3 ne te concernent pas encore.

**L'échelle d'aide (je ne te donne rien avant que tu l'aies demandé).** Écris-moi : « Je bloque sur `fonction`. Voici ma feuille, mon code, l'erreur, ce que j'ai essayé. »
1. **Après 25 min de blocage :** je te réponds par une question qui oriente.
2. **Si ça ne suffit pas :** le nom de la méthode ou de la formule, et pourquoi ton code échoue.
3. **Après 45 min (avec ta feuille et ton essai) :** un pseudo-code ou un squelette.
4. **Si tu es vraiment bloqué (≈ 1 h sur la même fonction, ou toujours bloqué le lendemain) :** la solution, commentée ligne par ligne. **Condition :** le lendemain, tu la refais **de mémoire**, sans regarder, jusqu'à ce que les tests passent, et tu notes « solution donnée » dans le journal.

**Le journal.** À la fin de chaque session, cinq lignes dans `JOURNAL.md` : ce que j'ai fait, ce qui m'a bloqué, ce que j'ai compris, ce que je ne sais pas encore expliquer.

**Le CV.** Une ligne n'apparaît que pour une étape finie au sens ci-dessus, code sur GitHub. Écris « implemented », pas « designed » (les tests viennent de moi).

**Les 2 h d'entretien par jour** (LeetCode, brainteasers, anglais) se font à côté ; elles couvrent ce que le projet ne couvre pas.

## Installation (15 minutes)

```bash
cd quant-lab
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

Le dernier `pytest` doit afficher **53 failed** (`NotImplementedError`) : c'est ton point de départ. Pour travailler sur un fichier : `pytest tests/phase1/test_orderbook.py -q` ; sur un seul test : ajoute `-k nom_du_test`. Puis `git init`, dépôt GitHub public `quant-lab`, un commit à chaque étape finie.

---

# PHASE 1 — Le moteur

## P0 — Le prix juste *(repère : 3 à 4 h)*

**Question.** Comment modéliser le « vrai prix » autour duquel on cote, et comment être sûr que le simulateur est correct ?

**Feuille.**
1. Un actif suit `dS = μ S dt + σ S dW`. Applique le lemme d'Itô à `ln S` et trouve `d(ln S)`. Explique d'où vient le terme `−σ²/2`.
2. En déduis `S_{t+dt}` en fonction de `S_t` et de `Z ~ N(0,1)`, pour un pas `dt` **quelconque**. Pourquoi la loi de `S_t` ne dépend-elle pas du pas utilisé ?
3. Calcule `E[S_T]` et explique pourquoi elle vaut `S_0 e^{μT}` alors que le drift du logarithme est `μ − σ²/2` (Jensen).

**Code (dans `simulation.py`).** `simulate_gbm`, `simulate_gbm_at_times` (même chose, mais à des instants irréguliers), `bs_call`, `mc_call_price` (d'abord sans antithétiques, puis avec).
**Tests.** `pytest tests/phase1/test_fair_price.py -q`.
**Expérience (`scripts/p0_fair_price.py`).** Trace des trajectoires ; vérifie `E[S_T]` ; compare le prix Monte Carlo d'un call at-the-money (S=K=100, r=5 %, σ=20 %, T=1) à Black–Scholes (10,4506) ; trace l'erreur-type en fonction de N en log-log (pente ≈ −1/2) ; vérifie que les antithétiques réduisent l'erreur-type d'environ 30 %.
**Pont.** Tu sais maintenant lire un prix juste à **n'importe quels instants**, en particulier les instants d'arrivée des clients (P2, P3).

## P1 — Le carnet d'ordres *(repère : 6 à 8 h)*

**Question.** Comment une bourse met en face acheteurs et vendeurs, et comment le faire vite ?

**Feuille.**
1. Dessine un carnet avec 3 bids et 3 asks, puis applique à la main un ordre d'achat au marché de 4 lots : écris chaque exécution, son prix et l'état du carnet après.
2. Pourquoi un tas-max pour les bids et un tas-min pour les asks ? Quelle clé permet de respecter « prix puis ordre d'arrivée » ?
3. Complexité de chaque opération avec une liste triée, puis avec un tas. Pourquoi l'annulation d'un ordre au milieu d'un tas est-elle coûteuse, et comment l'éviter (suppression paresseuse) ?
4. Quels invariants doivent toujours être vrais (carnet non croisé, quantité conservée) ?

**Code (`orderbook.py`).** Dans cet ordre : `__init__`, `add_limit_order` pour des ordres qui ne s'exécutent pas, `best_bid` / `best_ask` / `mid_price` / `spread`, puis `add_market_order`, la priorité prix puis temps, `cancel`, enfin l'ordre limite qui croise le carnet.
**Tests.** `pytest tests/phase1/test_orderbook.py -q`. Le dernier test vérifie la vitesse : s'il échoue sur le temps, ta structure n'est pas la bonne.
**Expérience (`scripts/p1_book.py`).** Rejoue une journée scriptée de 20 ordres en affichant le carnet après chaque action ; mesure le temps de 100 000 opérations ; trace `best_bid` et `best_ask`.
**Pont.** Les exécutions te renvoient l'identifiant du maker : ton market maker saura quand sa cotation est touchée.

## P2 — Le flux de clients *(repère : 4 à 5 h)*

**Question.** À quelle vitesse et dans quel ordre arrivent les clients ?

**Feuille.**
1. Montre que `P(T > t) = e^{−λt}` pour le temps d'attente d'un Poisson de taux `λ` (indice : `P(T > t) = P(N(t) = 0)`). Calcule son espérance et son écart-type.
2. Montre l'absence de mémoire.
3. Deux flux indépendants (achats `λ_b`, ventes `λ_s`) : quelle est la loi du temps avant le premier événement ? Montre que `P(le premier est un achat) = λ_b/(λ_b + λ_s)` (une intégrale).

**Code (`flow.py`).** `poisson_arrival_times`, `merge_event_streams` (avec un tas : « merge k sorted lists »), `generate_order_flow`.
**Tests.** `pytest tests/phase1/test_flow.py -q`.
**Expérience (`scripts/p2_flow.py`).** Histogramme des temps d'attente contre la densité exponentielle ; loi du nombre d'arrivées contre `scipy.stats.poisson` ; fréquence des achats contre `λ_b/(λ_b + λ_s)`.
**Pont.** Tu as des ordres de clients rangés dans le temps, et un prix juste à ces instants : tout pour P3.

## P3 — Le premier market maker *(repère : 5 à 6 h)*

**Question.** Quel risque le stock fait-il courir, et peut-on le calculer **exactement** ?

**Feuille.**
1. Face à des clients qui ne savent rien, que vaut le profit espéré d'une exécution ? Pourquoi l'espérance du gain sur le stock est-elle nulle, mais pas sa variance ?
2. Le stock fait +1 avec probabilité `p = λ_s/(λ_b + λ_s)` à chaque événement, −1 sinon. Écris `h_i = P(toucher +L avant −L depuis i)` par analyse au premier pas, puis le temps moyen `E_i`. Résous à la main pour `L = 2`, `p = 1/2` (tu dois trouver `E_0 = 4`).
3. Mets le système sous forme matricielle `P = [[Q, R], [0, I]]` : montre que `B = (I − Q)⁻¹ R` et `t = (I − Q)⁻¹ 1`.

**Code.** `markov.py` (`birth_death_transition_matrix`, `absorption_analysis`, `simulate_inventory_exit`), puis `marketmaker.run_market_making`, qui relie ton carnet, ton flux et ton prix juste.
**Tests.** `pytest tests/phase1/test_markov.py -q`, puis `test_marketmaker.py`. Le dernier test compare ton moteur complet à ta formule exacte.
**Expérience (`scripts/p3_market_maker.py`).** Pour `L = 3 … 8` : temps moyen avant de toucher la limite par (a) calcul exact, (b) marche simulée, (c) moteur complet. Les trois doivent concorder. Trace le stock au cours du temps. Sur 500 simulations, la distribution du profit : moyenne = spread gagné, écart-type = risque de stock. Écris en 3 phrases pourquoi ce modèle est trop gentil (indice : les clients acceptent n'importe quel prix, aucun n'est informé).
**Pont.** C'est cette limite que la phase 2 corrige : des clients informés, et une probabilité d'exécution qui baisse quand l'écart augmente.

---

## Phases 2 et 3 (aperçu)

**Phase 2.** P4 : des clients informés connaissent le prix futur ; tu calcules avec Bayes `P(informé | achat)` et l'écart de prix qui rend ton profit nul (Glosten–Milgrom), et tu testes par régression si le sens des ordres prédit le prix (`ols`, déjà préparé dans `tests/phase2`). P5 : tu estimes `λ(δ) = A·e^{−kδ}` par régression log-linéaire, tu maximises le profit espéré `δ·A·e^{−kδ}` (`δ* = 1/k`), puis tu ajoutes une pénalité de stock. Petit module de jugement : intervalle de confiance du profit par bootstrap.
**Phase 3.** Plusieurs actifs corrélés, couverture du stock, Markowitz, Sharpe, data-snooping, Black–Scholes et couverture en delta. Les fonctions et leurs tests existent déjà dans `tests/phase3`.

## Pour la soirée de départ (1 h, sans ordinateur)

La feuille de P0, étape 1 (Itô sur ln S), et celle de P2, étapes 1 à 3 (temps d'attente exponentiel, absence de mémoire, `λ_b/(λ_b + λ_s)`). Photographie-les dans `notes/`.
