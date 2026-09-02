# Parcours utilisateurs — Alinea

Ce document présente les principaux parcours utilisateurs et l'enchaînement des écrans d'Alinea.

---

## Parcours principal

Le fonctionnement d'Alinea s'organise autour d'un projet.

L'utilisateur configure d'abord le cadre dans lequel ses contenus seront produits, puis crée les contenus à traiter.

```mermaid
flowchart TD
    A[Connexion / Inscription] --> B[Mes projets]

    B --> C[Créer ou ouvrir un projet]

    C --> D[Configuration du projet]

    D --> E[Choisir ou créer un modèle]
    D --> F[Définir les sources]
    D --> G[Définir les règles]

    E --> H[Configurer les blocs]
    H --> I[Type, ordre et consignes]

    F --> J[Projet configuré]
    G --> J
    I --> J

    J --> K[Créer un ou plusieurs contenus]
    K --> L[Lancer le traitement]

    L --> M[En attente / En cours]
    M --> N[Résultats]

    N --> O[Relecture et modification]
    O --> P[Validation]
```

---

## Configuration d'un projet

Lors de la création d'un projet, l'utilisateur définit les éléments qui seront réutilisés pour produire ses contenus.

```text
Projet
│
├── Modèle de contenu
│   └── Blocs
│       ├── Nom
│       ├── Type
│       ├── Ordre
│       └── Consignes
│
├── Sources
│
└── Règles
    ├── Ton
    ├── Style
    └── Consignes générales
```

Ces éléments peuvent ensuite être modifiés depuis le projet.

---

## Production des contenus

Une fois le projet configuré, l'utilisateur peut créer les contenus qu'il souhaite faire préparer.

```mermaid
flowchart LR
    A[Projet] --> B[Créer un contenu]
    B --> C[Informations de départ]
    C --> D[Ajouter au traitement]
    D --> E[Traitement]
    E --> F[Résultat structuré]
    F --> G[Relecture]
    G --> H[Validation]
```

Plusieurs contenus peuvent être ajoutés afin d'être traités successivement.

---

## Relecture et validation

Après le traitement, le résultat est présenté selon la structure du modèle utilisé.

L'utilisateur peut :

- consulter les différents blocs ;
- consulter les sources utilisées ;
- modifier les propositions ;
- valider le résultat.

Le contenu généré n'est pas considéré comme validé avant cette intervention.

---

## Partage d'un projet

Un projet peut être partagé avec un autre utilisateur.

```mermaid
flowchart LR
    A[Projet] --> B[Partager]
    B --> C[Ajouter un utilisateur]
    C --> D[Utilisateur autorisé]
    D --> E[Accès au projet]
```

L'utilisateur autorisé retrouve le projet parmi les projets auxquels il a accès.

---

## Enchaînement des écrans principaux

```text
Connexion / Inscription
        ↓
Mes projets
        ↓
Projet
        ├── Configuration
        │      ├── Modèle et blocs
        │      ├── Sources
        │      └── Règles
        │
        ├── Contenus
        │      ↓
        │   Nouveau contenu
        │      ↓
        │   Traitement
        │      ↓
        │   Résultat / Relecture
        │      ↓
        │   Validation
        │
        └── Partage
```