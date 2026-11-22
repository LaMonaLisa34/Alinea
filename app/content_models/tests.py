import re

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from projects.models import EditorialProject


class ContentModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        now = timezone.now()
        owner, other_user = [
            user_model.objects.create_user(
                email=email,
                name=name,
                terms_accepted_at=now,
                privacy_policy_accepted_at=now,
            )
            for email, name in (
                ("owner@example.com", "Propriétaire"),
                ("other@example.com", "Autre compte"),
            )
        ]
        cls.owner = owner
        cls.other_user = other_user
        cls.project = EditorialProject.objects.create(
            name="Chevaux du Monde", owner=owner
        )
        cls.other_project = EditorialProject.objects.create(
            name="Autre projet du propriétaire", owner=owner
        )

    def setUp(self):
        self.client.force_login(self.owner)
        self.url = reverse("content_models:list", args=[self.project.pk])

    def create_template(self, name, description=""):
        response = self.client.post(
            self.url, {"name": name, "description": description}
        )
        self.assertEqual(response.status_code, 302)

        listing = self.client.get(self.url)
        self.assertEqual(listing.status_code, 200)
        matches = [
            template
            for template in listing.context["templates"]
            if template.name == name
        ]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def editor_url(self, template, project=None):
        if project is None:
            project = self.project
        return reverse("content_models:editor", args=[project.pk, template.pk])

    def test_empty_list_shows_creation_form(self):
        response = self.client.get(self.url)

        self.assertContains(response, "Créez votre premier modèle")
        self.assertFalse(response.context["form"].is_bound)
        self.assertEqual(list(response.context["templates"]), [])

    def test_creation_saves_the_description_and_lists_the_model(self):
        template = self.create_template("Article de blog", "Plan de rédaction")
        response = self.client.get(self.url)

        self.assertEqual(template.description, "Plan de rédaction")
        self.assertContains(response, "Article de blog")
        self.assertContains(response, self.editor_url(template))

    def test_blank_name_is_rejected(self):
        response = self.client.post(
            self.url, {"name": "   ", "description": "Plan de rédaction"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["form"].errors)
        self.assertEqual(list(self.client.get(self.url).context["templates"]), [])

    def test_anonymous_user_is_redirected_to_login(self):
        template = self.create_template("Article de blog")
        self.client.logout()

        for url in (self.url, self.editor_url(template)):
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url),
                    f"{reverse('accounts:account')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_another_user_cannot_view_or_create_models(self):
        template = self.create_template("Article de blog")
        self.client.force_login(self.other_user)

        self.assertEqual(self.client.get(self.url).status_code, 404)
        self.assertEqual(
            self.client.post(self.url, {"name": "Modèle intrus"}).status_code,
            404,
        )
        self.assertEqual(self.client.get(self.editor_url(template)).status_code, 404)

        self.client.force_login(self.owner)
        listing = self.client.get(self.url)
        self.assertEqual(
            [model.pk for model in listing.context["templates"]], [template.pk]
        )

    def test_model_is_only_available_in_its_own_project(self):
        template = self.create_template("Article de blog")
        other_url = reverse("content_models:list", args=[self.other_project.pk])
        listing = self.client.get(other_url)

        self.assertEqual(listing.status_code, 200)
        self.assertEqual(list(listing.context["templates"]), [])
        self.assertEqual(
            self.client.get(
                self.editor_url(template, project=self.other_project)
            ).status_code,
            404,
        )

    def test_other_model_has_a_tab_in_each_editor(self):
        article = self.create_template("Article de blog")
        breed_profile = self.create_template("Fiche race")

        for active, sibling in ((article, breed_profile), (breed_profile, article)):
            with self.subTest(active=active.name, sibling=sibling.name):
                response = self.client.get(self.editor_url(active))
                self.assertEqual(response.status_code, 200)

                navigation = re.findall(
                    r"<nav\b[^>]*>.*?</nav>",
                    response.content.decode(response.charset),
                    flags=re.DOTALL,
                )
                sibling_url = re.escape(self.editor_url(sibling))
                sibling_link = rf"""<a\b[^>]*\shref\s*=\s*(["']){sibling_url}\1"""
                self.assertTrue(
                    any(re.search(sibling_link, nav) for nav in navigation),
                    f"L’onglet « {sibling.name} » a disparu de la navigation "
                    f"du modèle « {active.name} ».",
                )
