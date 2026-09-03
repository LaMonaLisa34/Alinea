<div align="center">

<img src="docs/ui/logo-alinea.png" alt="Logo Alinea" width="180">

# Alinea
  
  
**Application de production de contenus structurés assistée par intelligence artificielle.**

</div>

Alinea est un projet visant à faciliter la production de contenus lorsque ceux-ci suivent une structure et des règles communes.

L'idée est d'utiliser un modèle de langage pour préparer une partie du travail, tout en conservant des sources identifiables et une validation humaine du résultat.

---

## Présentation de l'idée

La création de contenu pour un site web peut demander beaucoup de temps, en particulier lorsqu'un grand nombre de pages doit respecter la même structure.

Pour produire une page, il peut par exemple être nécessaire de rechercher des informations, consulter plusieurs sources, respecter des règles éditoriales, rédiger différents champs puis vérifier le résultat avant publication.

Ce besoin peut être particulièrement présent sur des sites ayant beaucoup de contenu et travaillant leur **référencement naturel (SEO)**.

Les outils d'intelligence artificielle peuvent aider à réaliser une partie de ce travail. Cependant, dans une utilisation classique, il faut souvent redonner les mêmes informations : le contexte, les règles à respecter, les sources à privilégier et la forme du résultat attendu.

Alinea part donc d'une idée simple : **définir ce cadre une fois dans l'application et pouvoir le réutiliser pour plusieurs contenus**.

Un projet Alinea pourrait ainsi contenir :

- des règles éditoriales ;
- des sources à privilégier ;
- un ou plusieurs modèles de contenu ;
- les documents à produire.

---

## Des modèles adaptés au contenu attendu

Tous les contenus ne se présentent pas sous la forme d'un simple article.

Un site peut par exemple disposer d'un espace d'administration dans lequel une fiche est répartie entre de nombreux champs : titre, introduction, description, caractéristiques, nombres, listes, choix prédéfinis, sources, etc.

Alinea permet de créer un modèle qui reprend cette structure.

Un modèle est composé de **blocs typés**, par exemple :

- texte ;
- texte long ;
- nombre ;
- booléen ;
- liste ;
- choix.

L'utilisateur peut ainsi définir les informations qu'il souhaite obtenir et leur organisation.

Par exemple, si un espace d'administration contient dix champs à renseigner, il est possible de créer un modèle Alinea avec les mêmes champs et dans le même ordre.

Le modèle peut ensuite être réutilisé pour plusieurs documents.

L'objectif est que le contenu préparé soit déjà séparé et organisé selon la structure attendue, afin de limiter le travail de remise en forme.

---

## Fonctionnement envisagé

Pour préparer un document, Alinea utilise le modèle choisi ainsi que les règles et les sources définies pour le projet.

Ces éléments servent de contexte au modèle de langage chargé de proposer le contenu des différents blocs.

Plusieurs documents pourront être placés dans une file de traitement afin d'être préparés successivement, sans devoir relancer manuellement chaque génération.

Une fois un traitement terminé, l'utilisateur retrouve le contenu organisé selon son modèle.

Il peut alors **relire, modifier et valider** les différents éléments avant de les utiliser.

L'IA reste donc une aide à la préparation du contenu. Le résultat n'est pas considéré comme validé automatiquement.

---

## Problématique

Produire un grand nombre de contenus qui suivent une structure similaire peut rapidement devenir répétitif et chronophage.

Pour chaque contenu, il faut retrouver les informations nécessaires, consulter les sources adaptées, respecter les mêmes règles éditoriales, renseigner les différents champs attendus puis vérifier le résultat. Lorsque ce travail doit être répété sur des dizaines ou des centaines de documents, il devient difficile de conserver un processus à la fois efficace et cohérent.

Les modèles de langage peuvent aider à automatiser une partie de ces tâches, mais leur utilisation pose aussi la question du respect des consignes, de la fiabilité des informations produites et du contrôle sur le résultat.

La problématique du projet est donc :

> **Comment automatiser une partie de la production de contenus structurés tout en conservant des règles communes, des sources identifiables et un contrôle humain sur le résultat ?**

---

## Objectif du projet

L'objectif d'Alinea est de développer une application permettant d'organiser ce processus de production.

Le projet prévoit notamment de permettre à l'utilisateur de :

- créer et gérer des projets ;
- définir des règles éditoriales ;
- enregistrer des sources de référence ;
- créer des modèles de contenu ;
- composer ces modèles avec différents types de blocs ;
- créer des documents à partir d'un modèle ;
- utiliser un modèle de langage pour préparer le contenu des blocs ;
- traiter plusieurs documents successivement ;
- retrouver les sources utilisées ;
- relire et modifier les propositions ;
- valider manuellement le résultat final.

Le projet cherchera ainsi à déterminer dans quelle mesure ce fonctionnement peut **réduire les tâches répétitives liées à la production de contenus**, sans supprimer le contrôle de l'utilisateur.

---

## MCD - Modèle Conceptuel de Données

![MCD Alinea](docs/modelisation/mcd.png)

Le modèle conceptuel de données représente les principales entités nécessaires au fonctionnement d’Alinea et leurs relations. Un utilisateur peut créer et partager des projets. Chaque projet regroupe ses sources, ses modèles de contenu et les sujets à traiter. Les modèles sont composés de blocs configurables à l’aide de paramètres. Un sujet peut ensuite faire l’objet d’un ou plusieurs traitements, dont l’exécution peut produire une génération structurée.