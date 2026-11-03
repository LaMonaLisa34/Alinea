# Conventions de développement

Ce document définit les règles de développement et de gestion du code source d’Alinea.

## Nommage

Le code et les messages de commit sont rédigés en anglais. La documentation, les issues et les textes de l’interface sont en français.

- Variables, fonctions, méthodes et fichiers Python : `snake_case`.
- Classes Python : `PascalCase`.
- Constantes : `UPPER_SNAKE_CASE`.
- Fichiers et fonctions de test : préfixe `test_`.
- Variables et fonctions JavaScript : `camelCase`.
- Classes CSS : minuscules séparées par des tirets.

Les noms sont explicites et correspondent au métier de l’application, par exemple `EditorialProject` ou `WritingSubject`.

## Formatage et contrôles

- Encodage UTF-8 et fins de ligne LF.
- Indentation Python : quatre espaces.
- Indentation HTML, CSS, JavaScript, JSON et YAML : deux espaces.
- Ruff assure le lint et le formatage Python, avec une longueur de ligne cible de 88 caractères.
- pre-commit exécute les vérifications configurées avant les commits.
- `.editorconfig` définit les règles communes aux éditeurs.

Les configurations sont conservées dans le dépôt. Les règles de formatage et de lint de Ruff sont définies dans `pyproject.toml`.

Les tests utilisent pytest et pytest-django. coverage mesure leur couverture et SonarQube complète l’analyse de qualité.

## Messages de commit

Les commits suivent la convention Conventional Commits :

```text
type(scope): description
```

Le scope est facultatif. Les principaux types sont :

| Type | Utilisation |
|---|---|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Réorganisation du code |
| `style` | Formatage sans changement fonctionnel |
| `ci` | Automatisation et CI/CD |
| `build` | Dépendances et construction des images |
| `chore` | Maintenance du dépôt |

Exemples :

```text
feat(auth): add user registration
fix(projects): restrict access to project owners
docs: document architecture and technical choices
```

Chaque commit regroupe un changement cohérent.

## Branches

Le projet utilise trois branches durables :

| Branche | Rôle |
|---|---|
| `dev` | Intégration des développements |
| `staging` | Vérification avant livraison |
| `main` | Versions validées |

Chaque fonctionnalité ou correction est développée dans une branche créée depuis `dev`, par exemple :

```text
feat/25-homepage
fix/login-error
docs/development-conventions
```

Le parcours d’intégration est :

**Branche de travail → dev → staging → main**

Les branches de travail peuvent être supprimées après fusion. Les trois branches durables sont conservées.

## Pull Requests

Les PR sont créées automatiquement lorsqu’il existe des changements à intégrer. Les nouveaux commits alimentent la PR ouverte sans créer de doublon.

Chaque PR contient :

- une description du changement ;
- une référence aux issues concernées ;
- les vérifications effectuées ;
- les éventuelles migrations ou modifications de configuration.

Avant fusion, le code est relu, les critères d’acceptation sont vérifiés et les contrôles requis doivent réussir.

La fusion reste manuelle. Les règles de protection des branches et l’automatisation des PR sont configurées dans le cadre de CI-01.

## VS Code

Les extensions retenues sont :

- **Python** et **Pylance** pour l’assistance au développement Python ;
- **Ruff** pour le lint et le formatage ;
- **EditorConfig** pour appliquer les conventions communes ;
- **WSL** pour travailler dans l’environnement Linux.

Les recommandations sont enregistrées dans `.vscode/extensions.json`.

## Fichiers versionnés

Le dépôt contient le code, les migrations, les tests, la documentation et les configurations partagées.

Le `.gitignore` exclut notamment :

- les secrets et fichiers `.env` locaux ;
- les environnements virtuels et dépendances installées ;
- les caches, journaux et rapports générés ;
- les données locales de l’application.

Les fichiers d’exemple des variables d’environnement sont versionnés sans valeur confidentielle.