# Fiches de cours — une fiche par étape

Lis la fiche **avant** de faire la feuille de l'étape. Les formules sont là pour gagner du temps ; les démonstrations, c'est toi qui les fais sur papier. Quand l'étape est codée, ferme la fiche et réponds aux questions à voix haute (en anglais dès que tu le peux, tu t'enregistres).

Les références (Shreve, Hull, Glosten–Milgrom, Lo, Bailey–López de Prado, Ledoit–Wolf) sont citées de mémoire : vérifie qu'elles existent et que la formule est bien celle écrite avant de les citer.

# PHASE 1 — Le moteur

## P0 — Le prix juste : GBM, Itô, Black–Scholes, Monte Carlo

**Mouvement brownien `W`.** `W_0 = 0` ; `W_t − W_s ~ N(0, t−s)` ; incréments indépendants ; trajectoires continues. Règle de calcul : `(dW)² = dt`, `dt·dW = 0`, `(dt)² = 0`.
**GBM.** `dS = μ S dt + σ S dW`. Lemme d'Itô pour `f(X)` avec `dX = a dt + b dW` : `df = (a f' + ½ b² f'') dt + b f' dW`. Appliqué à `ln S` : le terme `½ b² f''` apporte le `−σ²/2` (à toi de le calculer).
**Schéma exact.** `S_{t+dt} = S_t · exp((μ − σ²/2) dt + σ √dt · Z)`, `Z ~ N(0,1)`. Exact pour **tout** `dt` : la loi de `S_t` ne dépend pas de la fréquence d'observation. C'est ce qui permet de lire le prix à des instants irréguliers (les instants d'arrivée des clients, en P3) sans approximation.
**Pourquoi `E[S_T] = S_0 e^{μT}` alors que `E[ln S_T]` a le drift `μ − σ²/2` ?** Jensen : si `X ~ N(m, s²)`, `E[e^X] = e^{m + s²/2}`.
**Valorisation risque-neutre.** Sous Q le drift est `r` (pas `μ`) : le prix d'un call est le coût de la réplication par delta-hedging, qui ne dépend pas de `μ`. `C = e^{−rT} E_Q[(S_T − K)⁺]`.
**Black–Scholes (call, sans dividende).** `d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)`, `d2 = d1 − σ√T`, `C = S·Φ(d1) − K e^{−rT} Φ(d2)`.
**Monte Carlo.** `Ĉ = e^{−rT} · moyenne(payoffs)`. Erreur-type `= e^{−rT} · écart-type(payoffs)/√N` (TCL) : diviser l'erreur par 2 coûte 4× plus de trajectoires. **Antithétiques :** on utilise `Z` et `−Z` ; les payoffs sont corrélés négativement, la moyenne d'une paire a une variance plus faible ; l'erreur-type se calcule sur les moyennes de paires (indépendantes).

**Questions de défense.**
1. D'où vient le −σ²/2 ?
2. Pourquoi le schéma exact permet-il d'observer le prix à des instants irréguliers ?
3. Pourquoi simuler avec le drift `r` pour valoriser un call ?
4. Combien de trajectoires pour un prix à ±1 centime (95 %) ?
5. Pourquoi les antithétiques marchent-ils ici ? Dans quel cas ne marcheraient-ils pas ?

---

## P1 — Le carnet d'ordres

**Le carnet.** Deux files d'ordres limites en attente : les **bids** (acheteurs, du prix le plus haut au plus bas) et les **asks** (vendeurs, du plus bas au plus haut). `best_bid < best_ask` toujours : sinon un échange aurait déjà eu lieu. Spread = `best_ask − best_bid`, mid = leur moyenne.
**Appariement : priorité prix puis temps.** Un ordre entrant s'exécute contre le meilleur prix opposé ; à prix égal, le plus ancien d'abord ; l'échange se fait **au prix de l'ordre en attente** (le « maker »), pas au prix de l'ordre entrant (le « taker »). Un ordre au marché prend ce qu'il trouve ; un ordre limite « marketable » s'exécute d'abord, le reste attend dans le carnet.
**Structures de données.** Un tas-max pour les bids, un tas-min pour les asks, clé `(prix, numéro d'arrivée)` pour la priorité de temps : insertion et extraction du meilleur en `O(log n)`. Annulation : supprimer au milieu d'un tas coûte `O(n)`. Astuce : **suppression paresseuse** (lazy deletion) : on note l'ordre comme annulé dans un dictionnaire `id → ordre`, et on l'ignore quand il arrive en haut du tas. Annulation en `O(1)`, coût amorti `O(log n)`.
**Complexité.** Liste triée : insertion `O(n)`. Tas : `O(log n)`. Sur 30 000 ordres, ça fait la différence entre une seconde et plusieurs minutes (un des tests le vérifie).
**Lien LeetCode.** Mêmes idées que « merge k sorted lists », « find median from data stream » (deux tas), « LRU cache » (dictionnaire + structure ordonnée), tous des classiques d'entretien.
**Invariants à surveiller.** Le carnet n'est jamais croisé ; la quantité est conservée (posée − annulée − exécutée = ce qui reste).

**Questions de défense.**
1. À quel prix se fait un échange, et pourquoi ?
2. Pourquoi un tas et pas une liste triée ? Quelle est la complexité de chaque opération ?
3. Explique la suppression paresseuse. Pourquoi est-elle correcte ?
4. Un ordre limite d'achat à 102 arrive alors que le meilleur ask est à 101 : que se passe-t-il ?
5. Quels invariants permettent de vérifier que ton carnet est correct ?

---

## P2 — Le flux de clients : Poisson et exponentielle

**Processus de Poisson d'intensité `λ`.** Nombre d'arrivées dans `[0, t]` : `N(t) ~ Poisson(λt)`, d'espérance et de variance `λt`. Les nombres d'arrivées sur des intervalles disjoints sont indépendants.
**Temps d'attente.** Les temps entre arrivées sont i.i.d. `Exponentielle(λ)` : `P(T > t) = P(N(t) = 0) = e^{−λt}`, d'espérance `1/λ` et d'écart-type `1/λ`.
**Absence de mémoire.** `P(T > s + u | T > s) = P(T > u)` : savoir qu'on a déjà attendu `s` ne change rien. C'est ce qui rend les processus de Poisson « sans état » et la simulation facile.
**Deux flux indépendants.** Achats `λ_b`, ventes `λ_s` : le minimum de deux exponentielles indépendantes suit une `Exponentielle(λ_b + λ_s)`, et `P(le prochain événement est un achat) = λ_b/(λ_b + λ_s)`. Les deux flux superposés forment un Poisson de taux `λ_b + λ_s`, chaque événement étant un achat avec probabilité `λ_b/(λ_b + λ_s)` (découpage, ou « thinning »).
**Fusionner des flux.** Fusionner `k` listes triées avec un tas : `O(N log k)` (LeetCode « merge k sorted lists »). Piège Python : des générateurs créés dans une boucle capturent la variable de boucle **par référence** (late binding) : tous les générateurs voient la dernière valeur.

**Questions de défense.**
1. Pourquoi les temps entre arrivées d'un Poisson sont-ils exponentiels ?
2. Montre l'absence de mémoire. Pourquoi est-ce important pour simuler ?
3. Deux flux de Poisson indépendants : quelle est la loi du temps avant le premier événement, quelle est la probabilité qu'il vienne du flux 1 ?
4. Tu as attendu 10 minutes un client qui arrive en moyenne toutes les 5 minutes : combien d'attente restante en moyenne ?
5. Comment fusionnerais-tu 1000 flux triés ? Complexité ?

---

## P3 — Le premier market maker : stock et chaînes de Markov

**Le métier.** Le market maker affiche un prix d'achat (bid) et un prix de vente (ask) autour du prix juste. Chaque fois qu'un client traite, il gagne environ la **demi-fourchette** `h`. Face à des clients qui ne savent rien, son profit espéré est `nombre d'exécutions × h` : le prix juste est une martingale, donc le stock qu'il détient n'a pas d'espérance de gain ou de perte, seulement de la **variance**.
**Le stock est une marche aléatoire.** Un client qui vend au market maker : stock `+1` (probabilité `p = λ_s/(λ_b + λ_s)` à chaque événement) ; un client qui achète : `−1`. Avec une limite de stock `±L`, on regarde quand le stock atteint une limite.
**Chaîne de Markov absorbante, analyse au premier pas.** `h_i = P(atteindre +L avant −L depuis i)` vérifie `h_i = p h_{i+1} + (1−p) h_{i−1}` avec `h_{−L} = 0`, `h_L = 1`. Le temps moyen `E_i = 1 + p E_{i+1} + (1−p) E_{i−1}` avec `E_{±L} = 0`. **Forme matricielle :** en rangeant les états transitoires d'abord, `P = [[Q, R], [0, I]]`, la matrice fondamentale `N = (I − Q)⁻¹` donne `B = N R` (probabilités d'absorption) et `t = N·1` (temps moyens). On ne simule pas : on résout un système linéaire.
**Ruine du joueur.** Cas symétrique (`p = 1/2`) depuis `x` : `P(sortir par +L) = (x + L)/(2L)` et `E[temps] = L² − x²`. Cas général, `r = (1−p)/p`, `i = x + L`, `N = 2L` : `P = (1 − rⁱ)/(1 − r^N)`.
**Vérifier une formule par simulation.** Même habitude que Black–Scholes contre Monte Carlo : théorie et simulation doivent donner le même chiffre, à quelques erreurs-types. Ici, trois méthodes doivent concorder : le calcul exact, la marche simulée, et le moteur complet (carnet + flux + prix).
**La limite de ce modèle.** Les clients acceptent n'importe quel prix et aucun n'est mieux informé : en élargissant l'écart, le profit monte sans fin. C'est faux dans la réalité, et c'est ce que la phase 2 corrige.

**Questions de défense.**
1. D'où vient le profit d'un market maker ? Où est le risque ?
2. Écris l'analyse au premier pas pour le temps moyen avant de toucher la limite, et résous-la pour `L = 2` à la main.
3. Que représente `(I − Q)⁻¹` ?
4. Pourquoi l'espérance du profit sur le stock est-elle nulle face à des clients non informés ?
5. Pourquoi ce modèle est-il trop gentil ?

---

# PHASE 2 — L'intelligence (fiches livrées avec le kit de la phase 2)

Clients informés et sélection adverse (Bayes, Glosten–Milgrom), régression du mouvement du prix sur le sens des ordres, cotations optimales. Les fiches arrivent avec les consignes.

---

# PHASE 3 — Le risque et le jugement

## Plusieurs actifs corrélés — Cholesky

**Plusieurs actifs corrélés (Cholesky).** Toute matrice de covariance `Σ` (symétrique définie positive) s'écrit `Σ = L L'` avec `L` triangulaire inférieure (`np.linalg.cholesky`). Si `z ~ N(0, I)`, alors `Var(L z) = L Var(z) L' = Σ`. C'est ainsi qu'on fabrique des chocs corrélés à partir de chocs indépendants.

**Marché avec prédictibilité (`ar1`).** Un choc `e_t = φ e_{t−1} + √(1−φ²)·ε_t` a la même variance que `ε_t` et une autocorrélation `φ` : avec `φ > 0`, un rendement positif aujourd'hui rend un rendement positif demain un peu plus probable. Le labo B de S5 et S6 est construit ainsi.

---

## Estimation — Estimation : ce qu'on peut mesurer

**Moyenne.** Pour `n` rendements i.i.d. d'écart-type `s`, `SE(moyenne) = s/√n`. Annualisée : `SE = σ_annuel/√(nombre d'années)`. Pour une action à 16 % de volatilité observée 5 ans : 7 points de pourcentage, soit autant que le rendement espéré lui-même. **Le rendement espéré ne s'estime presque pas.**
**Variance et covariance.** L'erreur relative sur une variance estimée est d'ordre `√(2/n)` : sur 1260 jours, quelques pourcents. **La volatilité et les corrélations s'estiment bien.**

**Sharpe annualisé** (taux sans risque = 0) : `SR = moyenne/écart-type × √(périodes par an)`, écart-type d'échantillon (n−1). Invariant au levier. Erreur-type pour des rendements i.i.d. : environ `√((1 + SR²/2)/n)` par période (Lo, 2002, à vérifier) ; annualisé avec un petit SR : `≈ 1/√(nombre d'années)`. **Un Sharpe de 1 mesuré sur un an n'est pas distinguable de 0.**

**Bootstrap i.i.d.** Rééchantillonner les rendements avec remise, recalculer `SR` à chaque fois, prendre les quantiles 2,5 % et 97,5 %. Limites : ignore l'autocorrélation et la volatilité qui varie (il existe des bootstraps par blocs).

**Questions d'entretien.**
1. J'ai 5 ans de données journalières sur une action ; avec quelle précision je connais son rendement espéré ? Sa volatilité ?
2. Pourquoi est-il plus facile d'estimer une volatilité qu'un rendement ?
3. Donne l'ordre de grandeur de l'erreur sur un Sharpe estimé sur 5 ans.
4. Explique le bootstrap en 30 secondes. Quelle hypothèse fait-il ?

---

## Régression — Régression linéaire et tests

**Modèle.** `y = Xβ + ε`, `E[ε|X] = 0`, `Var(ε|X) = σ² I`.
**Estimateur.** `β̂ = (X'X)⁻¹ X'y`, solution des équations normales `X'(y − Xβ) = 0` (dérive-les en annulant le gradient de `‖y − Xβ‖²`). Géométrie : `Xβ̂` est la **projection orthogonale** de `y` sur l'espace des colonnes de `X` ; les résidus sont orthogonaux aux colonnes.
**Variance.** `Var(β̂) = σ² (X'X)⁻¹`, estimée avec `σ̂² = SSE/(n − p)` (`p` = nombre de colonnes y compris l'intercept). `se_j = √(σ̂² [(X'X)⁻¹]_{jj})`, `t_j = β̂_j/se_j`. À un seul régresseur : `β̂ = cov(x,y)/var(x)`.
**R².** `1 − SSE/SST`. Ne baisse jamais quand on ajoute une variable.
**Test.** Sous l'hypothèse « aucune relation », `t` est à peu près `N(0,1)` : 5 % des essais dépassent 1,96 en valeur absolue **par hasard**. Si la relation existe, `t ≈ β/se` : la **puissance** (probabilité de détecter) dépend de la taille de l'effet et de `n`. Un petit effet réel sur peu de données est souvent raté.
**Tests multiples.** Avec `k` régresseurs de bruit testés séparément, la probabilité qu'au moins un dépasse 1,96 est `1 − 0,95^k` (64 % pour 20).
**Gauss–Markov.** Sous ces hypothèses OLS est le meilleur estimateur linéaire sans biais. Si les erreurs sont hétéroscédastiques ou autocorrélées, les erreurs-types classiques sont fausses (corrections : White, Newey–West).
**Multicolinéarité.** `VIF_j = 1/(1 − R²_j)` ; avec deux variables `VIF = 1/(1 − ρ²)`. VIF > 10 : les erreurs-types explosent.
**Finance.** CAPM : `r_i − r_f = α + β (r_m − r_f) + ε`. `t_α` dit si `α` est distinguable du bruit. Biais de variable omise : un facteur oublié et corrélé aux autres biaise `β̂`.

**Questions d'entretien.**
1. Dérive `β̂`. Quand `X'X` n'est-il pas inversible ?
2. Pourquoi divise-t-on par `n − p` ?
3. Qu'est-ce qu'une t-stat de 2 ? Une p-value ? Pourquoi 20 régressions donnent-elles presque toujours une t-stat > 2 ?
4. Un vrai signal a un `t` moyen de 2,5 : combien de fois sur 10 le détecte-t-on ?
5. Explique le VIF. Que faire d'une variable avec VIF = 50 ?

---

## Portefeuilles — Portefeuilles et optimisation

**Variance minimale.** Minimiser `w'Σw` sous `1'w = 1`. Lagrangien `L = w'Σw − λ(1'w − 1)`, condition `2Σw = λ1`, donc `w = Σ⁻¹1/(1'Σ⁻¹1)`. Test dans le dépôt : `Σw` est un vecteur constant.
**Portefeuille tangent (Sharpe maximal).** `w ∝ Σ⁻¹(μ − r_f)`, normalisé pour sommer à 1. Le Sharpe est invariant à l'échelle de `w`, donc on peut fixer la contrainte qu'on veut.
**Contraintes d'inégalité (long-only, plafond).** Pas de formule fermée en général. Conditions de Karush–Kuhn–Tucker (KKT) : à l'optimum chaque actif est soit à une borne, soit tel que son gradient égale le multiplicateur. Numériquement : `scipy.optimize.minimize(method="SLSQP")` avec contrainte d'égalité et bornes.
**Le piège.** La solution est ultra-sensible à `μ` : l'erreur d'estimation de S2 est amplifiée par `Σ⁻¹` (grandes positions longues et courtes). C'est pour ça que le portefeuille de Sharpe maximal construit avec `μ̂` fait pire que les poids égaux dans ton expérience, alors que la variance minimale (qui n'utilise que `Σ̂`) est presque optimale.
**Shrinkage.** `(1 − δ) S + δ (tr S/p) I` tire les valeurs propres vers leur moyenne ; le nombre de conditionnement `λ_max/λ_min` baisse. (Ledoit–Wolf calcule `δ` automatiquement.)
**Algèbre linéaire à connaître.** `Σ` est symétrique semi-définie positive ; valeurs propres ≥ 0 ; `Σ = QΛQ'` ; ACP = diagonalisation de `Σ`.

**Questions d'entretien.**
1. Deux actifs non corrélés de variances `a` et `b` : poids de variance minimale ? (de tête)
2. Pourquoi un portefeuille de variance minimale peut-il avoir des poids négatifs ?
3. Pourquoi dit-on que l'optimisation moyenne-variance « maximise les erreurs » ?
4. Que représente économiquement un multiplicateur de Lagrange ?
5. Pourquoi shrinker une covariance ?

---

## Backtest — Backtest honnête

**Look-ahead bias.** Utiliser à la date `t` une information connue seulement après `t`. Garde-fous : le poids de la date `t` n'utilise que des prix ≤ `t` ; il gagne le rendement de `t+1`. Les tests vérifient les deux. Exemple innocent de look-ahead : normaliser avec la moyenne de tout l'échantillon, ou calculer la matrice de covariance sur toute la période puis l'utiliser pour trader dans le passé.
**Momentum de séries temporelles.** Signal = signe du rendement passé sur `lookback` jours en sautant les `skip` derniers jours. Poids = signal/nombre d'actifs.
**Coûts.** `coût_t = bps/10⁴ × turnover_t`. Un signal à fort turnover peut perdre tout son edge net de coûts : c'est ce que tu observes dans le labo A.
**Mesures.** Sharpe net, drawdown maximal (plus grande baisse depuis un sommet de la courbe de capital), turnover moyen.
**Walk-forward.** À chaque date de rebalancement, tu n'utilises que les données passées pour estimer, puis tu appliques. C'est ce que fait `rolling_min_variance_positions`.
**Biais à connaître.** Survie (l'univers = les ETF qui existent encore), sélection de paramètres (tester 30 variantes puis garder la meilleure : S6), période courte, régimes.

**Questions d'entretien.**
1. Qu'est-ce qu'un look-ahead bias ? Un exemple qui a l'air innocent ?
2. Mon backtest a un Sharpe de 1,5 avant coûts et 0,3 après. Que dis-tu ?
3. Pourquoi sauter le dernier mois dans le signal de momentum ?
4. Pourquoi la min-variance glissante a-t-elle un meilleur Sharpe que les poids égaux dans le labo ? Est-ce du « alpha » ?
5. Pourquoi le drawdown intéresse-t-il autant les investisseurs ?

---

## Jugement — Jugement : data-snooping, tests multiples

**Idée centrale.** Tester `N` stratégies sans aucun edge et garder la meilleure donne un Sharpe positif et grand. Sur 252 jours le Sharpe d'une stratégie sans edge est ≈ `N(0,1)` ; le meilleur de `N` vaut `E[max]` : 0 pour N=1, 0,56 pour 2, 1,54 pour 10, 2,51 pour 100, 3,24 pour 1000. Ordre de grandeur asymptotique `√(2 ln N)` (converge lentement : 3,03 pour N=100).
**Loi du maximum.** `P(max ≤ x) = Φ(x)^N`, donc densité `N φ(x) Φ(x)^{N−1}`.
**Essais corrélés.** Des variantes voisines (lookback 60 et 120) donnent des résultats très corrélés : le nombre d'essais indépendants est inférieur au nombre de variantes. Le maximum observé est plus petit que la formule i.i.d. et Bonferroni est trop sévère.
**Bonferroni.** Pour garder la probabilité d'au moins un faux positif ≤ α sur `N` tests : chaque test au seuil `α/N`. (Le *deflated Sharpe ratio* de Bailey et López de Prado généralise l'idée : à lire après le projet, puis vérifier la formule.)
**Parades.** Fixer la stratégie avant de regarder les données ; hors-échantillon réel ; moins de paramètres ; justification économique ; compter honnêtement le nombre d'essais.

**Questions d'entretien.**
1. J'ai testé 200 paramètres, le meilleur donne un Sharpe de 2 sur 1 an. Est-ce bon ?
2. Quelle est la loi du maximum de N uniformes ? de N normales ?
3. Que corrige Bonferroni, et à quel prix ?
4. Comment réduire le risque de faux positif sans corriger les p-values ?
5. Que conclus-tu d'un Sharpe de 0,5 sur 5 ans avec 10 variantes essayées ?

---

## Mini-fiche calcul stochastique (banque : Santander, XVA)

- Martingale : `E[W_t | F_s] = W_s`. `W_t² − t` est une martingale. Variation quadratique `[W]_t = t`.
- Intégrale d'Itô : `∫ H dW` est une martingale (si `H` adapté et de carré intégrable), d'espérance 0 ; isométrie `E[(∫H dW)²] = E[∫H² dt]`.
- Girsanov (idée) : changer de probabilité modifie le drift du brownien mais pas sa volatilité ; on choisit le changement qui rend `e^{−rt}S_t` martingale ; c'est pourquoi le drift devient `r`.
- Black–Scholes par EDP : delta-hedging → `∂C/∂t + ½σ²S² ∂²C/∂S² + rS ∂C/∂S − rC = 0`, condition finale `(S − K)⁺`. Feynman–Kac relie cette EDP à l'espérance risque-neutre.
- Lecture : Shreve II, chapitres 3 à 5, après S1.
