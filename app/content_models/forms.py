from decimal import Decimal

from django import forms
from django.db import transaction
from django.core.validators import URLValidator

from .models import BlockParameter, ContentBlock, ContentTemplate


class ContentTemplateForm(forms.ModelForm):
    """Valide le nom et la description d’un modèle de rédaction."""

    class Meta:
        model = ContentTemplate
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Exemple : fiche de race"},
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Décrivez l’objectif de ce modèle.",
                    "rows": 3,
                },
            ),
        }


class ContentBlockForm(forms.ModelForm):
    """Valide un bloc et les paramètres compatibles avec son type."""

    class Meta:
        model = ContentBlock
        fields = ("name", "instruction")
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Exemple : introduction"},
            ),
            "instruction": forms.Textarea(
                attrs={
                    "placeholder": "Précisez ce que l’IA doit rédiger.",
                    "rows": 3,
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Le type provient de l’instance autorisée par la vue, jamais du POST.
        parameter_fields = self._build_parameter_fields(self.instance.block_type)
        self.parameter_names = tuple(parameter_fields)
        self.fields.update(parameter_fields)

        if self.instance.pk:
            # all() réutilise le préchargement des paramètres effectué par les vues.
            stored_parameters = {
                parameter.name: parameter.value
                for parameter in self.instance.parameters.all()
            }
            for name in self.parameter_names:
                if name not in stored_parameters:
                    continue
                value = stored_parameters[name]
                if isinstance(self.fields[name], forms.BooleanField):
                    value = value.lower() in ("true", "1", "yes")
                if name == "longueur_cible" and value not in ("court", "moyen", "long"):
                    # Convertir les anciens objectifs numériques en catégories de longueur.
                    try:
                        word_count = int(value)
                    except (TypeError, ValueError):
                        value = self.fields[name].initial
                    else:
                        value = (
                            "court"
                            if word_count <= 150
                            else "moyen"
                            if word_count <= 500
                            else "long"
                        )
                self.initial[name] = value

    @staticmethod
    def _build_parameter_fields(block_type):
        """Construit les champs de configuration propres au type de bloc."""
        if block_type == ContentBlock.BlockType.TEXT:
            return {
                "longueur_cible": forms.ChoiceField(
                    label="Longueur du texte",
                    choices=(("court", "Court"), ("moyen", "Moyen"), ("long", "Long")),
                    initial="moyen",
                ),
                "structure": forms.ChoiceField(
                    label="Structure du texte",
                    choices=(
                        ("simple", "Texte simple"),
                        ("h2", "Plusieurs sections avec des titres H2"),
                        ("h2_h3", "Sections H2 avec des sous-titres H3"),
                    ),
                    initial="simple",
                    help_text="Un seul bloc peut contenir plusieurs sections.",
                ),
                "gras": forms.BooleanField(
                    label="Mettre les mots et expressions importants en gras",
                    required=False,
                    help_text="La mise en valeur reste ponctuelle, sans appliquer le gras à tout le texte.",
                ),
                "italique": forms.BooleanField(
                    label="Mettre certains mots ou expressions en italique",
                    required=False,
                    help_text="Les consignes peuvent préciser les termes ou expressions concernés.",
                ),
            }

        if block_type == ContentBlock.BlockType.NUMBER:
            return {
                "mode_valeur": forms.ChoiceField(
                    label="Résultat attendu",
                    choices=(
                        ("unique", "Une valeur unique"),
                        ("plage", "Une plage de valeurs (minimum et maximum)"),
                    ),
                    initial="unique",
                    help_text="Exemple de plage attendue : 150 à 165 cm.",
                ),
                "format": forms.ChoiceField(
                    label="Format du nombre",
                    choices=(
                        ("entier", "Nombre entier"),
                        ("decimal", "Nombre décimal"),
                    ),
                    initial="entier",
                ),
                "unite": forms.CharField(
                    label="Unité",
                    required=False,
                    max_length=40,
                    widget=forms.TextInput(
                        attrs={"placeholder": "Exemple : cm, kg, années"},
                    ),
                ),
                "minimum": forms.DecimalField(
                    label="Valeur minimale autorisée",
                    required=False,
                    max_digits=20,
                    decimal_places=8,
                    help_text="Limite autorisée ; ce champ ne renseigne pas le résultat.",
                ),
                "maximum": forms.DecimalField(
                    label="Valeur maximale autorisée",
                    required=False,
                    max_digits=20,
                    decimal_places=8,
                    help_text="En mode plage, les deux bornes doivent respecter ces limites.",
                ),
                "gras": forms.BooleanField(
                    label="Afficher le résultat en gras",
                    required=False,
                ),
            }

        if block_type == ContentBlock.BlockType.LIST:
            return {
                "nombre_minimum": forms.IntegerField(
                    label="Nombre minimal d’éléments",
                    required=False,
                    min_value=1,
                ),
                "nombre_maximum": forms.IntegerField(
                    label="Nombre maximal d’éléments",
                    required=False,
                    min_value=1,
                ),
                "presentation": forms.ChoiceField(
                    label="Présentation de la liste",
                    choices=(
                        ("puces", "Liste à puces"),
                        ("numerotee", "Liste numérotée"),
                    ),
                    initial="puces",
                ),
                "gras": forms.BooleanField(
                    label="Afficher les éléments en gras",
                    required=False,
                ),
            }

        if block_type == ContentBlock.BlockType.BOOLEAN:
            return {
                "presentation": forms.ChoiceField(
                    label="Présentation du résultat",
                    choices=(
                        ("oui_non", "Oui / Non"),
                        ("vrai_faux", "Vrai / Faux"),
                    ),
                    initial="oui_non",
                    help_text="Le contenu reste un booléen ; ce choix définit son affichage.",
                ),
                "gras": forms.BooleanField(
                    label="Afficher le résultat en gras",
                    required=False,
                ),
            }

        if block_type == ContentBlock.BlockType.MULTIPLE_CHOICE:
            return {
                "options": forms.CharField(
                    label="Réponses autorisées",
                    max_length=10000,
                    widget=forms.Textarea(
                        attrs={
                            "rows": 4,
                            "placeholder": "Dressage\nAttelage\nRandonnée",
                        }
                    ),
                    help_text="Une réponse par ligne.",
                ),
                "selection": forms.ChoiceField(
                    label="Nombre de réponses possibles",
                    choices=(
                        ("unique", "Une seule réponse"),
                        ("multiple", "Plusieurs réponses"),
                    ),
                    initial="multiple",
                ),
                "gras": forms.BooleanField(
                    label="Afficher les réponses en gras", required=False
                ),
            }

        if block_type == ContentBlock.BlockType.SEO:
            return {
                "inclure_titre": forms.BooleanField(
                    label="Générer un titre SEO", required=False, initial=True
                ),
                "inclure_description": forms.BooleanField(
                    label="Générer une méta-description", required=False, initial=True
                ),
                "inclure_slug": forms.BooleanField(
                    label="Générer un slug", required=False, initial=True
                ),
            }

        if block_type == ContentBlock.BlockType.TITLE:
            return {
                "niveau": forms.ChoiceField(
                    label="Niveau du titre",
                    choices=tuple((f"h{level}", f"H{level}") for level in range(1, 7)),
                    initial="h2",
                    help_text="Définit la place du titre dans la hiérarchie du document.",
                ),
            }

        if block_type == ContentBlock.BlockType.TABLE:
            return {
                "colonnes": forms.CharField(
                    label="Colonnes du tableau",
                    max_length=10000,
                    widget=forms.Textarea(
                        attrs={"rows": 3, "placeholder": "Race\nOrigine\nTaille"}
                    ),
                    help_text="Un nom de colonne par ligne, dans l’ordre souhaité.",
                ),
                "nombre_minimum": forms.IntegerField(
                    label="Nombre minimal de lignes", required=False, min_value=1
                ),
                "nombre_maximum": forms.IntegerField(
                    label="Nombre maximal de lignes", required=False, min_value=1
                ),
            }

        if block_type == ContentBlock.BlockType.URL:
            return {
                "url_imposee": forms.URLField(
                    label="Lien à utiliser, si vous le connaissez",
                    required=False,
                    max_length=2048,
                    assume_scheme="https",
                    validators=[URLValidator(schemes=["http", "https"])],
                    help_text="Facultatif. Sinon, l’URL devra être identifiée à partir des sources.",
                ),
                "libelle_lien": forms.CharField(
                    label="Texte du lien",
                    required=False,
                    max_length=150,
                    widget=forms.TextInput(
                        attrs={"placeholder": "Exemple : stud-book officiel"}
                    ),
                ),
                "nouvel_onglet": forms.BooleanField(
                    label="Ouvrir dans un nouvel onglet", required=False, initial=True
                ),
            }

        if block_type == ContentBlock.BlockType.DATE:
            return {
                "precision": forms.ChoiceField(
                    label="Précision attendue",
                    choices=(
                        ("jour", "Date complète"),
                        ("mois", "Mois et année"),
                        ("annee", "Année uniquement"),
                    ),
                    initial="jour",
                    help_text="Permet de conserver une année sans inventer de jour ni de mois.",
                ),
                "presentation": forms.ChoiceField(
                    label="Présentation de la date",
                    choices=(
                        ("fr", "Française : 22/11/2026 ou 11/2026"),
                        ("iso", "ISO : 2026-11-22 ou 2026-11"),
                    ),
                    initial="fr",
                    help_text="Pour une année seule, les deux présentations donnent 2026.",
                ),
                "gras": forms.BooleanField(
                    label="Afficher la date en gras", required=False
                ),
            }

        return {}

    def clean(self):
        """Contrôle les contraintes et la cohérence des paramètres du bloc."""
        cleaned_data = super().clean()
        block_type = self.instance.block_type

        if block_type == ContentBlock.BlockType.NUMBER:
            self._validate_bounds(cleaned_data, "minimum", "maximum")

            if cleaned_data.get("format") == "entier":
                for name in ("minimum", "maximum"):
                    value = cleaned_data.get(name)
                    if value is not None and value != value.to_integral_value():
                        self.add_error(
                            name,
                            "Saisissez une valeur entière pour ce format.",
                        )

        elif block_type in (ContentBlock.BlockType.LIST, ContentBlock.BlockType.TABLE):
            self._validate_bounds(
                cleaned_data,
                "nombre_minimum",
                "nombre_maximum",
            )

        elif block_type == ContentBlock.BlockType.MULTIPLE_CHOICE:
            self._validate_lines(cleaned_data, "options", minimum_count=2)

        elif block_type == ContentBlock.BlockType.SEO:
            if not any(
                cleaned_data.get(name)
                for name in ("inclure_titre", "inclure_description", "inclure_slug")
            ):
                self.add_error(None, "Sélectionnez au moins un élément SEO à générer.")

        # Le tableau possède des bornes de lignes et une liste de colonnes à valider.
        if block_type == ContentBlock.BlockType.TABLE:
            self._validate_lines(cleaned_data, "colonnes", minimum_count=1)

        return cleaned_data

    def _validate_lines(self, cleaned_data, name, minimum_count):
        """Normalise une liste de libellés et refuse les entrées ambiguës."""
        if name not in cleaned_data:
            return
        lines = [
            line.strip() for line in cleaned_data[name].splitlines() if line.strip()
        ]
        if len(lines) < minimum_count:
            self.add_error(
                name, f"Renseignez au moins {minimum_count} entrée(s), une par ligne."
            )
        elif len(lines) > 100:
            self.add_error(name, "La liste ne peut pas dépasser 100 entrées.")
        elif any(len(line) > 150 for line in lines):
            self.add_error(
                name, "Chaque libellé doit contenir au maximum 150 caractères."
            )
        elif len({line.casefold() for line in lines}) != len(lines):
            self.add_error(name, "Chaque libellé doit être unique.")
        else:
            cleaned_data[name] = "\n".join(lines)

    def _validate_bounds(self, cleaned_data, minimum_name, maximum_name):
        """Vérifie l’ordre des bornes lorsque les deux valeurs sont renseignées."""
        minimum = cleaned_data.get(minimum_name)
        maximum = cleaned_data.get(maximum_name)
        if minimum is not None and maximum is not None and minimum > maximum:
            self.add_error(
                maximum_name,
                "Le maximum doit être supérieur ou égal au minimum.",
            )

    def _save_m2m(self):
        """Persiste les paramètres avec les relations gérées par le ModelForm."""
        # Ce point d’extension couvre save() et save(commit=False) suivi de save_m2m().
        super()._save_m2m()
        with transaction.atomic():
            for name in self.parameter_names:
                value = self.cleaned_data[name]

                # Une valeur facultative effacée retire le paramètre correspondant.
                if value is None or value == "":
                    self.instance.parameters.filter(name=name).delete()
                    continue

                if isinstance(value, bool):
                    serialized_value = "true" if value else "false"
                elif isinstance(value, Decimal):
                    serialized_value = format(value, "f")
                else:
                    serialized_value = str(value)

                BlockParameter.objects.update_or_create(
                    content_block=self.instance,
                    name=name,
                    defaults={"value": serialized_value},
                )

            # Invalider les paramètres préchargés après leur modification.
            if hasattr(self.instance, "_prefetched_objects_cache"):
                self.instance._prefetched_objects_cache.pop("parameters", None)

    def save(self, commit=True):
        """Enregistre le bloc et ses paramètres dans une même transaction."""
        with transaction.atomic():
            return super().save(commit=commit)
