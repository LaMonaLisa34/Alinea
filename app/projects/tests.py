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

    def test_project_form_is_prefilled(self):
        """Préremplit le formulaire avec les informations actuelles du projet."""
        self.client.force_login(self.user)

        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, 200)

        form = response.context["form"]
        self.assertFalse(form.is_bound)
        self.assertEqual(form.instance.pk, self.project.pk)
        self.assertEqual(form["name"].value(), self.project.name)
        self.assertEqual(form["description"].value(), self.project.description)
        self.assertEqual(
            form["editorial_guidelines"].value(),
            self.project.editorial_guidelines,
        )

    def test_owner_can_update_project(self):
        """Enregistre les modifications sans créer de nouveau projet."""
        self.client.force_login(self.user)
        initial_count = EditorialProject.objects.count()
        data = self.project_data()

        response = self.client.post(
            self.detail_url,
            data,
            follow=True,
        )

        self.assertRedirects(response, self.detail_url)
        self.project.refresh_from_db()

        self.assertEqual(self.project.name, data["name"])
        self.assertEqual(self.project.description, data["description"])
        self.assertEqual(
            self.project.editorial_guidelines,
            data["editorial_guidelines"],
        )
        self.assertEqual(self.project.owner_id, self.user.pk)
        self.assertEqual(EditorialProject.objects.count(), initial_count)
        self.assertContains(
            response,
            "Les modifications du projet ont été enregistrées.",
        )

    def test_invalid_name_prevents_update_and_preserves_values(self):
        """Affiche les erreurs sans enregistrer les modifications invalides."""
        self.client.force_login(self.user)
        original_values = {
            "name": self.project.name,
            "description": self.project.description,
            "editorial_guidelines": self.project.editorial_guidelines,
        }

        for name in ("", "   ", "A" * 151):
            with self.subTest(name=name):
                data = self.project_data(name=name)

                response = self.client.post(self.detail_url, data)

                self.assertEqual(response.status_code, 200)
                form = response.context["form"]
                self.assertIn("name", form.errors)
                self.assertEqual(
                    form["description"].value(),
                    data["description"],
                )
                self.assertEqual(
                    form["editorial_guidelines"].value(),
                    data["editorial_guidelines"],
                )

                self.project.refresh_from_db()
                for field, value in original_values.items():
                    self.assertEqual(getattr(self.project, field), value)

    def test_owner_can_clear_optional_fields(self):
        """Permet de retirer la description et les consignes générales."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.detail_url,
            self.project_data(
                description="",
                editorial_guidelines="",
            ),
        )

        self.assertRedirects(
            response,
            self.detail_url,
            fetch_redirect_response=False,
        )

        self.project.refresh_from_db()
        self.assertFalse(self.project.description)
        self.assertFalse(self.project.editorial_guidelines)

    def test_other_user_cannot_update_project(self):
        """Refuse une modification soumise par un autre utilisateur."""
        self.client.force_login(self.other_user)
        original_values = {
            "name": self.project.name,
            "description": self.project.description,
            "editorial_guidelines": self.project.editorial_guidelines,
        }

        response = self.client.post(
            self.detail_url,
            self.project_data(),
        )

        self.assertEqual(response.status_code, 404)
        self.project.refresh_from_db()

        for field, value in original_values.items():
            self.assertEqual(getattr(self.project, field), value)
        self.assertEqual(self.project.owner_id, self.user.pk)

    def test_anonymous_user_cannot_update_project(self):
        """Exige une connexion avant toute modification."""
        original_name = self.project.name

        response = self.client.post(
            self.detail_url,
            self.project_data(),
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:account')}?next={self.detail_url}",
            fetch_redirect_response=False,
        )

        self.project.refresh_from_db()
        self.assertEqual(self.project.name, original_name)

    def test_update_cannot_change_project_owner(self):
        """Ignore les champs de propriété ajoutés à la requête."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.detail_url,
            self.project_data(
                owner=self.other_user.pk,
                owner_id=self.other_user.pk,
            ),
        )

        self.assertRedirects(
            response,
            self.detail_url,
            fetch_redirect_response=False,
        )

        self.project.refresh_from_db()
        self.assertEqual(self.project.owner_id, self.user.pk)
        self.assertEqual(self.project.name, "Equine Encyclopedia")


class ProjectDeleteTests(TestCase):
    """Teste la suppression des projets éditoriaux."""

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
            name="Project to Delete",
            description="This project will be deleted.",
            editorial_guidelines="Guidelines for deletion test.",
            owner=cls.user,
        )

    def setUp(self):
        self.delete_url = reverse(
            "projects:delete",
            kwargs={"pk": self.project.pk},
        )
        self.dashboard_url = reverse("dashboard:index")

    def test_authenticated_owner_can_delete_project(self):
        """Le propriétaire peut supprimer son projet."""
        self.client.force_login(self.user)
        project_id = self.project.pk

        response = self.client.post(self.delete_url)

        self.assertRedirects(
            response,
            self.dashboard_url,
            fetch_redirect_response=False,
        )

        # Vérifier que le projet a été supprimé
        self.assertFalse(EditorialProject.objects.filter(pk=project_id).exists())

    def test_other_user_cannot_delete_project(self):
        """Un autre utilisateur ne peut pas supprimer le projet."""
        self.client.force_login(self.other_user)
        project_id = self.project.pk

        response = self.client.post(self.delete_url)

        # Doit retourner 404
        self.assertEqual(response.status_code, 404)

        # Vérifier que le projet existe toujours
        self.assertTrue(EditorialProject.objects.filter(pk=project_id).exists())

    def test_anonymous_user_cannot_delete_project(self):
        """Exige une connexion pour supprimer un projet."""
        project_id = self.project.pk

        response = self.client.post(self.delete_url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:account')}?next={self.delete_url}",
            fetch_redirect_response=False,
        )

        # Vérifier que le projet existe toujours
        self.assertTrue(EditorialProject.objects.filter(pk=project_id).exists())

    def test_delete_requires_post_method(self):
        """La suppression ne fonctionne qu'avec POST."""
        self.client.force_login(self.user)
        project_id = self.project.pk

        # GET ne doit pas fonctionner
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 405)

        # Vérifier que le projet existe toujours
        self.assertTrue(EditorialProject.objects.filter(pk=project_id).exists())

    def test_delete_project_shows_success_message(self):
        """Affiche un message de succès après suppression."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.delete_url,
            follow=True,
        )

        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].level_tag, "success")
        self.assertIn("supprimé", messages[0].message.lower())
