# Feuille de route d'entraînement — Concevoir des agents en entreprise

Six projets originaux (pas de notebook source cette fois : c'est à toi de les coder), pensés pour t'entraîner spécifiquement sur l'approche discutée avec le Projet 07 : identifier les outils d'abord, puis concevoir la boucle de l'agent (essayer → évaluer → corriger), puis protéger toute action irréversible par un garde-fou. Les principes transversaux (injection de dépendance, source unique de vérité, contrat d'interface...) sont dans [`Projet_07/PRINCIPES-INGENIERIE.md`](./Projet_07/PRINCIPES-INGENIERIE.md) — ne les recopie pas ici, réfère-toi à ce document pendant que tu codes.

**Comment utiliser cette feuille de route.** Pour chaque projet : lis la fiche, écris toi-même un cahier des charges plus détaillé que celui donné ici (précise les colonnes exactes de tes données, les cas limites), écris tes tests AVANT le code en calculant à la main ce qu'ils doivent vérifier (comme `tests/test_planner.py` du Projet 07), puis code jusqu'à ce qu'ils passent. Ce document te donne le "quoi" et le "pourquoi" ; le "comment" doit venir de toi — c'est ce qui rend l'entraînement utile.

**Ordre conseillé :** 1 → 3 → 5 → 2 → 6 → 4. Les deux premiers n'ont qu'une seule boucle simple et un seul garde-fou ; le dernier (supervision d'infrastructure) est le plus délicat parce qu'une mauvaise décision de l'agent a un coût opérationnel immédiat.

---

## 1. Agent de support client (triage de tickets)

**En une phrase.** Un standardiste qui répond lui-même aux questions qu'il connaît, et transmet à un collègue humain dès qu'il n'est pas sûr — plutôt que d'inventer une réponse plausible mais fausse.

**Contexte métier.** Un service client reçoit des questions en langage libre ("comment annuler ma commande ?"). Certaines ont une réponse déjà écrite dans une base de connaissance, d'autres nécessitent un humain.

**Outils à concevoir en premier.**
- `chercher_dans_la_base_de_connaissance(question, k=3)` — recherche sémantique (comme `find_hotels` du Projet 07 / le RAG du Projet 04), renvoie les k passages les plus proches avec un score.
- `historique_client(id_client)` — SQL paramétré, pour donner du contexte à la réponse.
- `escalader_vers_un_humain(ticket, raison)` — enregistre la transmission, avec la raison.

**La boucle de l'agent.** Chercher la meilleure réponse, évaluer le score de similarité du meilleur résultat. Si le score dépasse un seuil, répondre. Sinon, reformuler la recherche une seule fois (par exemple avec des mots-clés extraits différemment) avant d'abandonner et d'escalader — ne jamais boucler indéfiniment (garde-fou anti-boucle infinie, comme `MAX_ITERATIONS` dans le Projet 07).

**Le garde-fou.** Ne jamais envoyer une réponse en dessous du seuil de confiance sans passer par `escalader_vers_un_humain`. Écris le seuil comme une constante nommée et documentée, pas un nombre magique caché dans une condition.

**Cahier des charges à détailler toi-même.** Quelle structure pour une "question" (texte brut + id client) ? Quelle structure pour une "réponse" (texte + score + source citée) ? Quels cas limites tes tests doivent-ils couvrir : aucune réponse trouvée, deux réponses à score quasi identique, une question vide ?

---

## 2. Agent de réapprovisionnement de stock

**En une phrase.** Un gestionnaire d'entrepôt qui prépare la commande du mois, et qui, si le budget ne suffit pas pour tout commander, retire d'abord les produits les moins critiques — jamais au hasard.

**Contexte métier.** Un stock de produits, avec des ventes qui varient dans le temps, un budget d'achat mensuel limité.

**Outils à concevoir en premier.**
- `niveau_de_stock(produit)` — SQL.
- `prevoir_la_demande(produit, horizon_jours)` — série temporelle (réutilise directement l'approche du Projet 06 : baseline puis modèle, jamais de split aléatoire sur des données temporelles).
- `prix_fournisseur(produit, quantite)`.
- `passer_commande(produit, quantite, confirme=False)` — irréversible.

**La boucle de l'agent.** Pour chaque produit sous son seuil de réassort, composer une quantité à commander à partir de la prévision de demande. Sommer le coût total ; si ça dépasse le budget mensuel, retirer ou réduire d'abord les produits au score de criticité le plus bas (ex. faible marge, faible rotation) — exactement le principe "sacrifier dans un ordre réfléchi, jamais au hasard" du Projet 07.

**Le garde-fou.** `passer_commande` n'écrit rien tant que `confirme=False`. Ajoute une deuxième limite : jamais de commande unique au-dessus d'un montant plafond sans validation, même si le calcul dit que le budget mensuel le permettrait.

**Cahier des charges à détailler toi-même.** Comment définis-tu le "score de criticité" d'un produit ? Que fait l'agent si la prévision de demande elle-même est incertaine (peu d'historique) — commande-t-il quand même, avec quelle marge de prudence ?

---

## 3. Agent de validation de notes de frais

**En une phrase.** Un comptable qui approuve sans hésiter les petites dépenses habituelles, mais qui s'arrête net et demande un avis dès qu'un montant ou un motif sort de l'ordinaire.

**Contexte métier.** Des employés soumettent des notes de frais (montant, catégorie, justificatif). La plupart respectent la politique interne ; certaines doivent être examinées.

**Outils à concevoir en premier.**
- `lire_la_note_de_frais(pdf)` — extraction de texte (comme `load_brochures` du Projet 07), pour en tirer montant/date/catégorie.
- `regles_de_politique_interne(note)` — un petit moteur de règles (ex. plafond par catégorie, justificatif obligatoire au-delà d'un montant).
- `detecter_anomalie(note, historique_employe)` — écart statistique par rapport aux habitudes de dépense de cet employé.
- `escalader_a_un_manager(note, raison)`.

**La boucle de l'agent.** Évaluer chaque note contre les règles ET contre l'anomalie statistique. Si les deux sont au vert, approuver automatiquement. Si une règle est violée OU qu'une anomalie est détectée, escalader avec la raison précise (pas juste "à vérifier").

**Le garde-fou.** Une règle dure, non négociable par l'agent quel que soit son "score de confiance" : jamais d'approbation automatique au-dessus d'un montant plafond fixé dans la politique de l'entreprise, point final.

**Cahier des charges à détailler toi-même.** Comment représentes-tu "l'historique de dépenses" d'un employé pour détecter une anomalie sans trop de fausses alertes ? Que se passe-t-il si `lire_la_note_de_frais` échoue à extraire un montant (PDF illisible) ?

---

## 4. Agent de supervision d'infrastructure (DevOps)

**En une phrase.** Un opérateur d'astreinte qui essaie d'abord le geste le plus léger pour réparer un service en panne, puis un geste plus lourd seulement si le premier ne suffit pas — et qui réveille un humain plutôt que de prendre un risque non maîtrisé.

**Contexte métier.** Des services en production, surveillés en continu ; certaines pannes se réparent seules avec une action simple, d'autres nécessitent une intervention humaine.

**Outils à concevoir en premier.**
- `etat_du_service(service)` — appel d'un health check.
- `lire_les_logs(service, depuis)` — recherche sémantique dans des logs, pour repérer un motif d'erreur connu (encore les embeddings, appliqués à un texte technique cette fois).
- `redemarrer_le_service(service, confirme=False)` — irréversible et risqué.
- `notifier_astreinte(message)`.

**La boucle de l'agent.** Détecter une anomalie, tenter d'abord une remédiation légère (ex. relancer une seule requête en échec), réévaluer l'état. Si ça ne suffit pas, tenter le redémarrage complet — seulement si les conditions de sécurité sont réunies (voir garde-fou). Journaliser chaque étape tentée, dans l'ordre, avec le résultat de chacune.

**Le garde-fou.** C'est le projet où le garde-fou doit être le plus strict de toute la feuille de route : jamais de redémarrage automatique en heures de pointe, jamais sans notifier l'astreinte au préalable, et une limite dure sur le nombre de redémarrages automatiques par service et par jour (pour éviter qu'un agent bloqué dans une boucle ne redémarre le même service en continu).

**Cahier des charges à détailler toi-même.** Quelles sont, très précisément, "les conditions de sécurité" qui autorisent un redémarrage automatique ? Comment le distingues-tu d'une simple lenteur passagère qui se serait résolue seule ?

---

## 5. Agent de présélection de candidatures (RH)

**En une phrase.** Un recruteur qui compare chaque CV à la fiche de poste par le sens plutôt que par les mots-clés exacts, et qui élargit ses critères avant de conclure "personne ne convient" — sans jamais rejeter définitivement à la place d'un humain.

**Contexte métier.** Une CVthèque, une fiche de poste avec des critères (compétences, expérience). L'agent aide à trier, pas à décider seul.

**Outils à concevoir en premier.**
- `analyser_un_cv(pdf)` — extraction de texte.
- `chercher_dans_la_cvtheque(criteres)` — SQL paramétré (années d'expérience, localisation...).
- `comparer_au_poste(cv, fiche_de_poste)` — recherche sémantique, même logique que comparer un hôtel à l'envie d'un voyageur dans le Projet 07.

**La boucle de l'agent.** Scorer chaque candidat retenu par `chercher_dans_la_cvtheque` contre la fiche de poste. Si trop peu de candidats dépassent le score minimum, élargir progressivement les critères de recherche SQL (rayon géographique, expérience minimale) avant de revenir avec une liste vide — le même principe que l'agent qui explore les jours voisins dans le Projet 07 plutôt que de s'arrêter au premier échec.

**Le garde-fou.** L'agent présélectionne et classe, il ne rejette et n'accepte jamais définitivement une candidature : la dernière étape reste toujours une décision humaine, quelle que soit la qualité du score.

**Cahier des charges à détailler toi-même.** Comment gères-tu un CV dans une langue différente de la fiche de poste ? Quels critères peux-tu élargir automatiquement, et lesquels (diplôme requis obligatoire, par exemple) ne doivent jamais être assouplis par l'agent seul ?

---

## 6. Agent de planification de tournées de livraison

**En une phrase.** Un dispatcheur qui construit la tournée de chaque chauffeur, et qui réaffecte la livraison la moins prioritaire à quelqu'un d'autre plutôt que de faire arriver toutes les livraisons en retard.

**Contexte métier.** Des commandes à livrer dans la journée, plusieurs chauffeurs, des fenêtres horaires à respecter, du trafic qui varie.

**Outils à concevoir en premier.**
- `commandes_du_jour(zone)` — SQL.
- `calculer_un_itineraire(commandes, point_de_depart)` — optimisation de tournée, reprend directement l'heuristique du Projet 03 (construction gloutonne + 2-opt).
- `trafic_en_temps_reel(itineraire)` — un appel externe (ou une simulation, pour s'entraîner sans vraie API).

**La boucle de l'agent.** Construire une tournée par chauffeur, évaluer si chaque livraison tient dans sa fenêtre horaire compte tenu du trafic. Si une livraison ne peut pas tenir, la retirer de cette tournée et l'ajouter à la liste des livraisons à réaffecter (repli), puis reconstruire les tournées affectées. Journaliser chaque réaffectation avec sa raison, pour que le responsable logistique comprenne pourquoi telle livraison a changé de chauffeur.

**Le garde-fou.** Aucune livraison ne doit disparaître silencieusement de la liste : si l'agent ne trouve aucune tournée qui la fasse tenir dans les délais, il doit le signaler explicitement (comme l'agent du Projet 07 qui répond "impossible" plutôt que de forcer une réponse fausse), jamais l'omettre.

**Cahier des charges à détailler toi-même.** Comment représentes-tu une "fenêtre horaire" et le temps de trajet estimé dans ta structure de données ? Sur quel critère précis choisis-tu la livraison "la moins prioritaire" à réaffecter en premier ?

---

## Pour aller plus loin, une fois les 6 codés

- Reprends chaque projet et ajoute une vraie API + un petit frontend (comme pour le Projet 07), pour t'entraîner aussi sur le contrat d'interface entre couches.
- Compare, projet par projet, l'ordre de repli que tu as choisi avec celui d'un camarade ou d'une IA : c'est une décision de conception défendable, pas une vérité unique — l'exercice utile est de savoir *justifier* ton choix.
- Relis [`Projet_07/PRINCIPES-INGENIERIE.md`](./Projet_07/PRINCIPES-INGENIERIE.md) après avoir codé, pas avant : les principes se comprennent mieux une fois qu'on a buté sur le problème qu'ils résolvent.
