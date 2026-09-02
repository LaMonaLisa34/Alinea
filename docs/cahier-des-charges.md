# Cahier des charges — Alinea

## 1. Présentation du projet

Alinea est une application web de production de contenus structurés assistée par intelligence artificielle.

Le projet part du constat que la production d'un grand nombre de contenus partageant une structure et des règles communes peut devenir répétitive.

Pour chaque contenu, il peut être nécessaire de rechercher des informations, consulter des sources, appliquer les mêmes règles éditoriales, renseigner plusieurs champs puis vérifier le résultat.

Alinea vise à permettre à l'utilisateur de définir ce cadre une fois au niveau d'un projet, puis de le réutiliser pour plusieurs documents.

L'intelligence artificielle intervient comme une aide à la préparation du contenu. Les propositions restent soumises à la relecture, à la modification et à la validation de l'utilisateur.

---

## 2. Problématique

> **Comment automatiser une partie de la production de contenus structurés tout en conservant des règles communes, des sources identifiables et un contrôle humain sur le résultat ?**

---

## 3. Utilisateurs ciblés

Alinea s'adresse principalement aux personnes devant produire ou maintenir plusieurs contenus partageant une structure commune.

Les utilisateurs ciblés peuvent notamment être :

- des gestionnaires de sites éditoriaux ;
- des créateurs de contenu ;
- des freelances travaillant sur plusieurs projets ;
- des personnes devant reprendre un volume important de contenus à la suite d'une évolution de leurs règles éditoriales.

Les personas et leurs besoins sont détaillés dans le document consacré aux utilisateurs cibles.

---

## 4. Besoins fonctionnels

### BF-01 — Gestion des comptes

L'utilisateur doit pouvoir :

- créer un compte ;
- se connecter et se déconnecter ;
- gérer les informations principales de son compte ;
- supprimer son compte.

### BF-02 — Gestion des projets

L'utilisateur doit pouvoir :

- créer un projet ;
- consulter ses projets ;
- modifier un projet ;
- supprimer un projet ;
- accéder aux différents éléments associés à un projet.

### BF-03 — Partage d'un projet

Le propriétaire d'un projet doit pouvoir le partager avec un autre utilisateur.

Seuls le propriétaire et les utilisateurs autorisés doivent pouvoir accéder au projet.

Le MVP ne prévoit pas de système avancé de rôles et de permissions.

### BF-04 — Gestion des règles

L'utilisateur doit pouvoir définir des règles communes à un projet.

Ces règles doivent pouvoir être réutilisées lors de la préparation des différents documents du projet.

### BF-05 — Gestion des sources

L'utilisateur doit pouvoir :

- ajouter des sources de référence à un projet ;
- modifier ou supprimer une source ;
- définir certaines sources comme prioritaires ;
- retrouver les sources utilisées lors de la préparation d'un contenu.

### BF-06 — Gestion des modèles de contenu

L'utilisateur doit pouvoir :

- créer un modèle ;
- modifier ou supprimer un modèle ;
- réutiliser un modèle pour plusieurs documents.

Un modèle représente la structure du contenu attendu.

### BF-07 — Composition des modèles

Un modèle doit pouvoir être composé de plusieurs blocs ordonnés.

Pour chaque bloc, l'utilisateur doit pouvoir définir :

- son nom ;
- son type ;
- sa position ;
- des consignes propres au bloc.

Le MVP doit au minimum prendre en charge les blocs de type :

- texte ;
- nombre ;
- booléen ;
- liste.

### BF-08 — Gestion des documents

L'utilisateur doit pouvoir :

- créer un document à partir d'un modèle ;
- fournir le sujet ou les informations de départ ;
- consulter les documents associés à un projet ;
- retrouver dans le document la structure définie par son modèle.

### BF-09 — Préparation assistée par IA

L'application doit pouvoir préparer le contexte nécessaire à partir :

- des informations du document ;
- des règles du projet ;
- des sources disponibles ;
- du modèle ;
- des consignes associées aux blocs.

Ce contexte doit pouvoir être transmis à un modèle de langage afin d'obtenir des propositions pour les différents blocs.

### BF-10 — Structuration des réponses

L'application doit pouvoir récupérer la réponse du modèle de langage et associer les résultats aux blocs correspondants.

Elle doit vérifier que le résultat obtenu est compatible avec la structure et les principaux types de données attendus.

### BF-11 — File de traitement

L'utilisateur doit pouvoir placer plusieurs documents dans une file de traitement.

Le système doit pouvoir :

- conserver les traitements en attente ;
- les exécuter successivement ;
- indiquer lorsqu'un traitement est en cours ;
- identifier un traitement terminé ;
- identifier un traitement en erreur.

### BF-12 — Relecture et validation

L'utilisateur doit pouvoir :

- consulter les propositions générées ;
- retrouver les résultats selon la structure du modèle ;
- modifier manuellement un résultat ;
- consulter les sources associées ;
- valider le contenu.

Une proposition générée par l'IA ne doit pas être considérée comme validée automatiquement.

### BF-13 — Traçabilité

L'application doit conserver les principales informations permettant de retrouver le contexte d'un traitement, notamment :

- le document concerné ;
- le modèle utilisé ;
- le résultat obtenu ;
- les sources associées ;
- l'état du traitement.

---

## 5. Contraintes principales

### Contraintes techniques

Alinea doit être développé sous la forme d'une application web.

Le modèle de langage utilisé pour le MVP est exécuté localement. L'application utilise un modèle existant et n'a pas pour objectif de créer ou d'entraîner son propre modèle d'intelligence artificielle.

Les traitements liés au modèle de langage doivent être séparés du fonctionnement classique de l'application afin qu'un traitement long ne bloque pas les autres actions de l'utilisateur.

Le MVP prévoit une exécution séquentielle des traitements. La gestion de plusieurs traitements IA simultanés n'est pas nécessaire.

L'application doit prendre en compte les erreurs pouvant survenir lors d'un traitement et conserver un état permettant d'identifier les traitements en attente, en cours, terminés ou en erreur.

### Contraintes liées à l'intelligence artificielle

Les réponses d'un modèle de langage ne peuvent pas être considérées comme systématiquement exactes.

L'application doit donc conserver une validation humaine avant qu'un contenu soit considéré comme finalisé.

Les réponses doivent autant que possible respecter la structure définie par le modèle de contenu.

Une réponse invalide ou incompatible avec le type de bloc attendu doit pouvoir être détectée.

Le volume d'informations transmis au modèle doit également rester compatible avec sa capacité de traitement.

### Contraintes de sécurité

L'application doit mettre en place une authentification permettant de protéger les comptes utilisateurs.

Les contrôles d'autorisation doivent être réalisés côté serveur.

Un utilisateur ne doit pas pouvoir consulter ou modifier un projet auquel il n'est pas autorisé à accéder.

Les données reçues par l'application doivent être contrôlées et validées.

Une attention particulière doit être portée aux contenus et sources externes utilisés lors des traitements.

### Protection des données personnelles

La collecte de données personnelles doit être limitée aux informations nécessaires au fonctionnement de l'application.

L'utilisateur doit être informé de l'utilisation de ses données et pouvoir gérer les informations associées à son compte.

La suppression d'un compte et des données personnelles associées doit être prévue.

L'accès aux projets et à leurs contenus doit être limité aux utilisateurs autorisés.

Une durée de conservation adaptée doit être définie pour les données concernées.

Le modèle de langage du MVP étant exécuté localement, les contenus traités n'ont pas vocation à être transmis à un fournisseur d'IA externe.

### Contraintes de qualité

Le code doit rester organisé de manière à séparer les principales responsabilités de l'application.

Les fonctionnalités principales doivent être couvertes par des tests adaptés.

Les erreurs importantes doivent être gérées sans entraîner de perte silencieuse des données ou laisser un traitement dans un état incohérent.

### Contraintes de projet

Le développement est réalisé dans le cadre du projet CDA et doit rester compatible avec le temps disponible.

La priorité est donnée à la réalisation d'un parcours fonctionnel complet plutôt qu'à la multiplication des fonctionnalités.

Les fonctionnalités non indispensables au fonctionnement principal sont reportées après le MVP.

---

## 6. Périmètre du MVP

Le parcours principal du MVP est :

**Compte → Projet → règles et sources → modèle composé de blocs → document → file de traitement → traitement IA → proposition structurée → relecture → validation**

Le MVP comprend :

- la gestion des comptes ;
- la gestion et le partage simple des projets ;
- les règles éditoriales ;
- les sources de référence ;
- les modèles et leurs blocs ;
- les documents ;
- la préparation du contexte ;
- l'utilisation d'un modèle de langage local ;
- la file de traitement ;
- la récupération de résultats structurés ;
- la relecture et la modification ;
- la validation humaine ;
- la traçabilité des principales informations du traitement ;
- les fonctions nécessaires à la protection des données personnelles.

---

## 7. Hors périmètre du MVP

Ne sont notamment pas prévus dans la première version :

- plusieurs fournisseurs ou modèles d'IA ;
- le choix du modèle depuis l'interface ;
- l'exécution parallèle de plusieurs traitements IA ;
- les rôles et permissions avancés ;
- l'édition collaborative en temps réel ;
- la connexion directe à des CMS ;
- la publication automatique ;
- l'import massif depuis un CMS ;
- une extension navigateur ;
- la génération automatique de FAQ ;
- la génération JSON-LD ;
- la traduction automatique ;
- un système RAG avancé ;
- un système avancé de notation des sources ;
- la planification des traitements ;
- les statistiques avancées.

Ces fonctionnalités pourront être étudiées après la réalisation du MVP.

---