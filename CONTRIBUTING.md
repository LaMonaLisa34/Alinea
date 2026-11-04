# Conventions de développement

Ce document décrit les règles de développement et le parcours d’intégration des changements dans Alinea.

## Nommage

Le code et les messages de commit sont rédigés en anglais. La documentation, les issues et les textes de l’interface sont en français.

- Variables, fonctions, méthodes et fichiers Python : `snake_case`.
- Classes Python : `PascalCase`.
- Constantes : `UPPER_SNAKE_CASE`.
- Fichiers et fonctions de test : préfixe `test_`.
- Variables et fonctions JavaScript : `camelCase`.
- Classes CSS : minuscules séparées par des tirets.

Les noms décrivent clairement le rôle des éléments dans l’application, par exemple `EditorialProject` ou `WritingSubject`.

## Formatage et tests

- Encodage UTF-8 et fins de ligne LF.
- Indentation Python : quatre espaces.
- Indentation HTML, CSS, JavaScript, JSON et YAML : deux espaces.
- Longueur de ligne cible en Python : 88 caractères.

Le fichier `.editorconfig` définit les conventions communes aux éditeurs. Ruff vérifie le code Python et son formatage selon les règles définies dans `pyproject.toml`.

Les tests utilisent pytest et pytest-django. Dans la CI, ils s’exécutent avec une base PostgreSQL dédiée, isolée des données de développement et de production. Ils ne nécessitent ni service d’IA réel ni clé payante.

### Vérifications avant commit

Lefthook exécute `ruff check` et `ruff format --check` sur les fichiers Python ajoutés au commit. Il contrôle également les templates HTML ajoutés au commit à l’aide de djLint avec le profil Django. Ces vérifications ne modifient pas les fichiers.

Le hook `commit-msg` vérifie que la première ligne du message respecte la convention Conventional Commits, par exemple `feat(auth): add user registration`. Les messages de fusion et d’annulation générés par Git sont acceptés. La configuration des hooks est versionnée dans `lefthook.yml`.

Après l’installation de Lefthook, Ruff et djLint, les hooks doivent être activés à la racine du dépôt, une fois par clone :

```bash
lefthook install
```

Pour vérifier l’ensemble des templates Django indépendamment d’un commit, exécuter la commande suivante depuis la racine du dépôt :

```bash
djlint app/templates --lint --profile=django
```

En cas d’erreur signalée par Ruff ou djLint, les fichiers concernés doivent être corrigés, puis ajoutés de nouveau avec `git add` avant de relancer le commit. Si le message de commit est refusé, il doit être reformulé conformément à la convention.

Les tests Django et les analyses de sécurité sont exécutés dans GitHub Actions.

## Messages de commit

Les commits suivent la convention Conventional Commits :

```text
type(scope): description
```

Le scope est facultatif. Chaque commit regroupe un changement cohérent.

| Type | Utilisation |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Réorganisation du code sans changement de comportement |
| `style` | Formatage sans changement fonctionnel |
| `ci` | Automatisation et CI/CD |
| `build` | Dépendances et construction des images |
| `chore` | Maintenance du dépôt |

Exemples :

```text
feat(auth): add user registration
fix(projects): restrict access to project owners
docs: document CI checks and branch protections
```

## Branches

| Branche permanente | Rôle |
|---|---|
| `dev` | Intégration des fonctionnalités et des corrections |
| `main` | Versions validées |

Crée chaque branche de travail depuis `dev` à jour. Exemples : `feat/25-homepage`, `fix/login-error` ou `docs/ci-workflow`.

Le parcours d’intégration est **branche de travail → `dev` → `main`**. Les branches de travail peuvent être supprimées après fusion. `dev` et `main` sont conservées.

Alinea est développé en solo. Deux branches permanentes suffisent pour intégrer les changements au fil du développement et conserver une version validée. La branche `staging` a été testée, mais elle répétait les mêmes contrôles sans servir à une étape de recette distincte.

## Pull requests

Lorsqu’il existe des changements à intégrer, GitHub Actions ouvre une PR de la branche de travail vers `dev`, ou de `dev` vers `main`. Si une PR existe déjà entre les mêmes branches, les nouveaux commits la mettent à jour.

Chaque PR indique :

- le changement et son objectif ;
- les issues concernées, s’il y en a ;
- les vérifications effectuées ;
- les éventuelles migrations ou modifications de configuration.

Un ruleset GitHub protège `dev` et `main`. Les changements sont intégrés par PR et les contrôles obligatoires doivent réussir. Avant de fusionner, relis les modifications et vérifie les critères d’acceptation.

**La fusion reste manuelle.** Une PR `dev → main` peut rester ouverte jusqu’à ce qu’une version soit prête à être livrée. Pour la fusionner, utilise **Create a merge commit** et conserve `dev`.

GitHub peut demander d’autoriser l’exécution des workflows sur une PR ouverte par le bot. Le bouton **Approve workflows to run** lance les contrôles de la PR. La fusion se confirme séparément.

## Intégration continue

Le workflow `.github/workflows/ci.yml` lance les contrôles lors des pushs et des PR ciblant `dev` ou `main`.

| Contrôle obligatoire | Vérifications |
|---|---|
| Qualité Python | Lint et formatage avec Ruff |
| Tests et couverture | Tests Django avec pytest et génération des rapports de couverture |
| Build et sécurité Docker | Construction de l’image `runtime`, vérification des imports Django et psycopg, puis scan de l’image avec Trivy |
| Sécurité du dépôt | Audit des dépendances Python avec pip-audit et scan de la configuration et des secrets avec Trivy |

Trivy fait échouer le contrôle lorsqu’il détecte une alerte `HIGH` ou `CRITICAL`. Les rapports de tests, de couverture et de scan Docker sont accessibles dans les artefacts de l’exécution GitHub Actions.

SonarQube Cloud analyse les PR internes et les pushs sur `main`. Il utilise le rapport de couverture produit par les tests. Sa **Quality Gate reste informative** : son résultat n’est pas exigé pour fusionner une PR.

## VS Code

Les extensions recommandées sont indiquées dans `.vscode/extensions.json` :

- **Python** et **Pylance** pour l’assistance au développement Python ;
- **Ruff** pour le lint et le formatage ;
- **EditorConfig** pour les conventions communes ;
- **WSL** pour travailler dans l’environnement Linux.

Si le dépôt se trouve dans WSL, ouvre-le depuis le terminal Ubuntu avec `code .`. SonarQube for IDE peut être connecté au projet Alinea dans SonarQube Cloud pour consulter les alertes pendant le développement.

## Fichiers versionnés

Le dépôt contient le code, les migrations, les tests, la documentation et les configurations partagées.

Le `.gitignore` exclut notamment les secrets, les fichiers `.env` locaux, les environnements virtuels, les dépendances installées, les caches, les journaux, les rapports générés et les données locales de l’application.

Les fichiers d’exemple des variables d’environnement sont versionnés sans valeur confidentielle. Le jeton `SONAR_TOKEN` est enregistré dans les secrets GitHub Actions.
