# Fonctionnalités envisagées et périmètre du projet

Alinea a pour objectif d'aider à préparer des contenus structurés à partir de règles, de sources et de modèles définis par l'utilisateur.

Plusieurs fonctionnalités sont envisagées pour répondre à ce besoin. Elles ne seront cependant pas toutes développées dans la première version du projet.

L'objectif du MVP est de permettre un parcours complet, de la création d'un projet jusqu'à la validation d'un contenu préparé avec l'aide d'un modèle de langage.

---

## Fonctionnalités envisagées

### Gestion et partage des projets

Un utilisateur peut créer plusieurs projets afin de séparer différents contextes de production.

Chaque projet peut disposer de ses propres :

- règles éditoriales ;
- sources de référence ;
- modèles de contenu ;
- documents.

Un projet peut être partagé avec d'autres utilisateurs afin de leur permettre d'accéder au même espace de travail.

### Règles éditoriales

L'utilisateur peut définir des règles communes à un projet.

Elles permettent de conserver des consignes réutilisables lors de la préparation de plusieurs contenus : style rédactionnel, contraintes particulières, règles concernant les sources ou autres indications propres au projet.

### Gestion des sources

L'utilisateur peut enregistrer des sources de référence pour un projet.

Ces sources servent à orienter la recherche et la préparation du contenu et permettent de conserver une trace des références utilisées.

Certaines sources peuvent être définies comme prioritaires.

### Modèles de contenu

L'utilisateur peut créer des modèles correspondant à la structure des contenus qu'il souhaite produire.

Un modèle est composé de blocs ordonnés représentant les différentes informations attendues.

Pour chaque bloc, l'utilisateur peut définir notamment :

- un nom ;
- un type ;
- sa position dans le modèle ;
- des consignes propres au bloc.

Plusieurs types de blocs sont envisagés :

- texte court ;
- texte long ;
- nombre ;
- booléen ;
- liste ;
- choix parmi plusieurs valeurs.

Un modèle peut par exemple reproduire les différents champs présents dans l'espace d'administration d'un site.

Si une fiche contient un titre, une introduction, plusieurs textes, des valeurs numériques, des listes et des choix prédéfinis, le modèle Alinea peut reprendre cette même organisation.

Le modèle peut ensuite être réutilisé pour plusieurs documents partageant la même structure.

### Gestion des documents

L'utilisateur peut créer plusieurs documents à partir d'un même modèle.

Chaque document correspond à un contenu à préparer et possède son propre sujet ou ses propres informations de départ.

### Génération assistée par un modèle de langage

Alinea prépare le contexte nécessaire à partir du projet, de ses règles, de ses sources et du modèle sélectionné.

Un modèle de langage local est ensuite utilisé pour proposer le contenu correspondant aux différents blocs du document.

Le résultat attendu doit respecter autant que possible les types et la structure définis dans le modèle.

### Traitement de plusieurs documents

Plusieurs documents peuvent être placés dans une file de traitement.

Ils sont préparés successivement afin que l'utilisateur n'ait pas besoin de lancer manuellement chaque génération.

L'état de chaque traitement peut être consulté depuis l'application.

### Relecture et validation

Les propositions générées sont présentées à l'utilisateur selon les blocs définis dans le modèle.

L'utilisateur peut les relire, les modifier puis les valider.

Un contenu généré par l'IA n'est donc pas considéré comme finalisé sans intervention de l'utilisateur.

### Traçabilité

Alinea conserve les principales informations liées à un traitement, notamment les sources utilisées et le résultat produit.

L'objectif est de permettre à l'utilisateur de retrouver les éléments ayant servi à préparer le contenu.

---

## Périmètre du projet

Le projet porte sur la création d'une application web permettant d'organiser la production de contenus structurés avec l'aide d'un modèle de langage.

Le fonctionnement principal retenu est :

**Projet → règles et sources → modèle composé de blocs → document → traitement → proposition → relecture → validation**

Alinea prend en charge l'organisation du projet, la définition de la structure attendue, la préparation du contexte transmis au modèle de langage, le suivi des traitements et la validation des résultats.

Le projet ne vise pas à créer ou entraîner un modèle d'intelligence artificielle. Alinea utilise un modèle existant exécuté localement.

Le projet ne prévoit pas non plus, dans sa première version, de publier automatiquement les contenus sur un site ou un CMS. Le résultat reste contrôlé et utilisé par l'utilisateur.

---

## Fonctionnalités du MVP

La première version doit permettre de tester le fonctionnement principal d'Alinea avec un parcours complet.

### Comptes utilisateurs

- créer un compte ;
- se connecter et se déconnecter ;
- accéder aux projets créés par l'utilisateur ;
- accéder aux projets partagés avec l'utilisateur.

### Protection des données personnelles

Le MVP prend en compte les principes de protection des données personnelles dans la gestion des comptes et des contenus.

Cela comprend notamment :

- limiter les données personnelles collectées à celles nécessaires au fonctionnement de l'application ;
- informer l'utilisateur sur les données collectées et leur utilisation ;
- permettre la modification des informations liées au compte ;
- permettre la suppression du compte et des données personnelles associées ;
- protéger l'accès aux données des projets ;
- limiter l'accès aux projets aux utilisateurs autorisés ;
- définir une durée de conservation adaptée aux données ;
- prendre en compte les données pouvant être présentes dans les contenus transmis au modèle de langage.

Le modèle de langage utilisé pour le MVP étant exécuté localement, les contenus traités n'ont pas vocation à être transmis à un fournisseur d'IA externe.  


### Projets et partage

- créer un projet ;
- modifier un projet ;
- consulter ses projets ;
- définir les règles éditoriales du projet ;
- partager un projet avec un autre utilisateur ;
- limiter l'accès au propriétaire et aux utilisateurs autorisés.

Le MVP prévoit un partage simple. La gestion de rôles et de permissions détaillées n'est pas nécessaire dans cette première version.

### Sources

- ajouter une source à un projet ;
- modifier ou supprimer une source ;
- identifier les sources à privilégier.

### Modèles de contenu

- créer un modèle ;
- modifier ou supprimer un modèle ;
- ajouter des blocs au modèle ;
- définir le nom et le type d'un bloc ;
- définir des consignes propres à un bloc ;
- ordonner les blocs ;
- modifier ou supprimer un bloc ;
- réutiliser un modèle pour plusieurs documents.

Les premiers types de blocs retenus pour le MVP sont :

- texte ;
- nombre ;
- booléen ;
- liste.

### Documents

- créer un document à partir d'un modèle ;
- renseigner son sujet ou ses informations de départ ;
- consulter les documents d'un projet ;
- retrouver la structure du modèle dans le document.

### Traitement IA

- préparer le contexte à partir du projet, des règles, des sources et du modèle ;
- transmettre le traitement à un modèle de langage local ;
- récupérer une réponse structurée ;
- associer les résultats aux blocs correspondants ;
- contrôler la compatibilité du résultat avec le type de bloc attendu ;
- gérer les principales erreurs de traitement.

### File de traitement

- ajouter plusieurs documents à traiter ;
- exécuter les traitements successivement ;
- afficher l'état d'un traitement ;
- identifier un traitement terminé ou en erreur.

### Relecture et validation

- afficher le résultat selon la structure du modèle ;
- consulter les propositions bloc par bloc ;
- permettre leur modification manuelle ;
- afficher les sources associées au traitement ;
- permettre à l'utilisateur de valider le document.

---

## Fonctionnalités reportées

Certaines fonctionnalités sont envisagées pour faire évoluer Alinea, mais ne sont pas nécessaires pour tester son fonctionnement principal.

Elles sont donc volontairement exclues du MVP :

- prise en charge de plusieurs fournisseurs ou modèles d'IA ;
- choix du modèle d'IA depuis l'interface ;
- plusieurs workers exécutant des traitements en parallèle ;
- répartition automatique des traitements entre plusieurs machines ;
- rôles et permissions avancés pour les projets partagés ;
- édition collaborative en temps réel ;
- connexion directe à des CMS ou espaces d'administration ;
- publication automatique des contenus ;
- extension navigateur permettant de remplir directement un formulaire ;
- import massif de contenus depuis un CMS ;
- génération automatique de FAQ ;
- génération de données structurées JSON ou JSON-LD ;
- traduction automatique de contenus ;
- comparaison avancée entre plusieurs versions d'un document ;
- système avancé de notation ou de classement des sources ;
- recherche documentaire avancée ou système RAG ;
- planification automatique des traitements ;
- tableaux de bord et statistiques avancées.

Ces fonctionnalités pourront être réévaluées après la réalisation du MVP en fonction du temps disponible et des résultats obtenus.