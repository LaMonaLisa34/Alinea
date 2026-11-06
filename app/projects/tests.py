from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import EditorialProject

User = get_user_model()


class EditorialProjectTests(TestCase):
    """Teste la création et la consultation des projets éditoriaux."""

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        common_fields = {
            "terms_accepted_at": now,
            "privacy_policy_accepted_at": now,
        }

        cls.user = User.objects.create_user(
            email="owner@example.com",
            name="Project Owner",
            **common_fields,
        )
        cls.other_user = User.objects.create_user(
            email="other@example.com",
            name="Other User",
            **common_fields,
        )
        cls.project = EditorialProject.objects.create(
            name="Existing Project",
            description="Existing description.",
            editorial_guidelines="Use an accessible writing style.",
            owner=cls.user,
        )

    def setUp(self):
        self.create_url = reverse("projects:create")
        self.detail_url = reverse(
            "projects:detail",
            kwargs={"pk": self.project.pk},
        )

    def project_data(self, **overrides):
        """Prépare les données d’un nouveau projet."""
        data = {
            "name": "Equine Encyclopedia",
            "description": "Reference articles about horse breeds.",
            "editorial_guidelines": "Use an encyclopedic tone.",
        }
        data.update(overrides)
        return data

    def test_authenticated_user_can_open_creation_form(self):
        """Affiche le formulaire de création à un utilisateur connecté."""
        self.client.force_login(self.user)

        response = self.client.get(self.create_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/project_create.html")
        self.assertFalse(response.context["form"].is_bound)

    def test_anonymous_user_cannot_create_project(self):
        """Exige une connexion pour afficher ou soumettre le formulaire."""
        initial_count = EditorialProject.objects.count()

        for method in ("get", "post"):
            with self.subTest(method=method):
                if method == "get":
                    response = self.client.get(self.create_url)
                else:
                    response = self.client.post(
                        self.create_url,
                        self.project_data(),
                    )

                self.assertRedirects(
                    response,
                    f"{reverse('accounts:account')}?next={self.create_url}",
                    fetch_redirect_response=False,
                )

        self.assertEqual(EditorialProject.objects.count(), initial_count)

    def test_valid_creation_saves_project_and_redirects(self):
        """Enregistre les champs saisis et redirige vers le projet créé."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            self.project_data(),
            follow=True,
        )

        project = EditorialProject.objects.get(name="Equine Encyclopedia")
        self.assertEqual(project.owner_id, self.user.pk)
        self.assertEqual(
            project.description,
            "Reference articles about horse breeds.",
        )
        self.assertEqual(
            project.editorial_guidelines,
            "Use an encyclopedic tone.",
        )
        self.assertIsNotNone(project.created_at)

        self.assertRedirects(
            response,
            reverse("projects:detail", kwargs={"pk": project.pk}),
        )
        self.assertContains(response, "Votre projet éditorial a été créé.")

    def test_owner_cannot_be_selected_through_post_data(self):
        """Ignore toute tentative d’attribuer le projet à un autre compte."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            self.project_data(
                owner=self.other_user.pk,
                owner_id=self.other_user.pk,
            ),
        )

        self.assertEqual(response.status_code, 302)
        project = EditorialProject.objects.get(name="Equine Encyclopedia")
        self.assertEqual(project.owner_id, self.user.pk)

    def test_invalid_name_prevents_creation_and_preserves_values(self):
        """Refuse un nom invalide et conserve les autres champs saisis."""
        self.client.force_login(self.user)
        initial_count = EditorialProject.objects.count()

        for name in ("", "   ", "A" * 151):
            with self.subTest(name=name):
                response = self.client.post(
                    self.create_url,
                    self.project_data(name=name),
                )

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(
                    response,
                    "projects/project_create.html",
                )

                form = response.context["form"]
                self.assertIn("name", form.errors)
                self.assertEqual(
                    form["description"].value(),
                    "Reference articles about horse breeds.",
                )
                self.assertEqual(
                    form["editorial_guidelines"].value(),
                    "Use an encyclopedic tone.",
                )
                self.assertEqual(
                    EditorialProject.objects.count(),
                    initial_count,
                )

    def test_optional_fields_can_be_empty(self):
        """Autorise la création avec uniquement un nom."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.create_url,
            {"name": "Minimal Project"},
        )

        self.assertEqual(response.status_code, 302)
        project = EditorialProject.objects.get(name="Minimal Project")
        self.assertEqual(project.owner_id, self.user.pk)
        self.assertFalse(project.description)
        self.assertFalse(project.editorial_guidelines)

    def test_owner_can_view_project(self):
        """Affiche les informations du projet à son propriétaire."""
        self.client.force_login(self.user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects/project_overview.html")
        self.assertEqual(response.context["project"], self.project)
        self.assertContains(response, self.project.name)
        self.assertContains(response, self.project.description)
        self.assertContains(response, self.project.editorial_guidelines)

    def test_other_user_cannot_view_project(self):
        """Refuse l’accès direct au projet d’un autre propriétaire."""
        self.client.force_login(self.other_user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_cannot_view_project(self):
        """Redirige un visiteur vers la connexion avant toute consultation."""
        response = self.client.get(self.detail_url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:account')}?next={self.detail_url}",
            fetch_redirect_response=False,
        )
