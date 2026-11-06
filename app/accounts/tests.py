from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class AccountTests(TestCase):
    """Teste les parcours d’authentification et leurs cas de refus."""

    @classmethod
    def setUpTestData(cls):
        """Crée un compte de référence dans la base de test."""
        cls.password = "Nuage!47-Foret?92"
        now = timezone.now()
        cls.user = User.objects.create_user(
            email="existing@example.com",
            password=cls.password,
            name="Existing User",
            terms_accepted_at=now,
            privacy_policy_accepted_at=now,
        )

    def setUp(self):
        """Résout l’URL du formulaire commun avant chaque test."""
        self.account_url = reverse("accounts:account")

    def registration_data(self, **overrides):
        """Construit les données d’inscription, avec remplacement des valeurs ciblées."""
        data = {
            "action": "register",
            "register-name": "New User",
            "register-email": "new@example.com",
            "register-password1": self.password,
            "register-password2": self.password,
            "register-accept_terms": "on",
            "register-acknowledge_privacy_policy": "on",
        }
        data.update(overrides)
        return data

    def login_data(self, **overrides):
        """Construit les données de connexion avec les préfixes du formulaire."""
        # AuthenticationForm conserve le nom « username » pour son champ
        # d’identification, même lorsque le modèle utilise une adresse e-mail.
        data = {
            "action": "login",
            "login-username": self.user.email,
            "login-password": self.password,
        }
        data.update(overrides)
        return data

    def test_account_page_displays_selected_form(self):
        """Affiche le formulaire correspondant au mode demandé dans l’URL."""
        for mode, expected in (("login", False), ("register", True)):
            with self.subTest(mode=mode):
                response = self.client.get(self.account_url, {"mode": mode})

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "accounts/account.html")
                self.assertEqual(response.context["is_registration"], expected)

    def test_valid_registration_creates_account(self):
        """Enregistre le compte et propose la connexion sans ouvrir de session."""
        response = self.client.post(
            self.account_url,
            self.registration_data(),
        )

        self.assertRedirects(
            response,
            f"{self.account_url}#connexion",
            fetch_redirect_response=False,
        )

        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.name, "New User")

        # Contrôle le stockage haché et la correspondance avec le mot de passe saisi.
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))

        self.assertIsNotNone(user.terms_accepted_at)
        self.assertIsNotNone(user.privacy_policy_accepted_at)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_duplicate_email_is_rejected_regardless_of_case(self):
        """Refuse une adresse déjà enregistrée, quelle que soit sa casse."""
        for email in ("existing@example.com", "EXISTING@example.com"):
            with self.subTest(email=email):
                response = self.client.post(
                    self.account_url,
                    self.registration_data(**{"register-email": email}),
                )

                self.assertEqual(response.status_code, 200)
                self.assertIn("email", response.context["form"].errors)
                self.assertEqual(User.objects.count(), 1)

    def test_invalid_password_is_rejected(self):
        """Refuse les mots de passe courts, courants ou entièrement numériques."""
        cases = (
            ("short", "X7!q"),
            ("common", "password"),
            ("numeric", "927461830572"),
        )

        for label, password in cases:
            with self.subTest(case=label):
                response = self.client.post(
                    self.account_url,
                    self.registration_data(
                        **{
                            "register-password1": password,
                            "register-password2": password,
                        }
                    ),
                )

                self.assertEqual(response.status_code, 200)
                self.assertIn("password2", response.context["form"].errors)
                self.assertEqual(User.objects.count(), 1)

    def test_different_passwords_are_rejected(self):
        """Refuse l’inscription lorsque la confirmation du mot de passe diffère."""
        response = self.client.post(
            self.account_url,
            self.registration_data(**{"register-password2": "Autre!83-Mot?54"}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("password2", response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_required_acknowledgements_cannot_be_omitted(self):
        """Refuse l’inscription si l’une des deux cases obligatoires est absente."""
        for field in ("accept_terms", "acknowledge_privacy_policy"):
            with self.subTest(field=field):
                data = self.registration_data()

                # Une case non cochée n’est pas transmise dans la requête HTML.
                data.pop(f"register-{field}")
                response = self.client.post(self.account_url, data)

                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.assertEqual(User.objects.count(), 1)

    def test_failed_registration_preserves_non_sensitive_values(self):
        """Conserve le nom et l’e-mail après erreur sans réafficher les mots de passe."""
        response = self.client.post(
            self.account_url,
            self.registration_data(**{"register-password2": "Different!74"}),
        )

        form = response.context["form"]
        self.assertTrue(response.context["is_registration"])
        self.assertEqual(form["name"].value(), "New User")
        self.assertEqual(form["email"].value(), "new@example.com")

        # Inspecte la réponse HTML, et pas seulement les données du formulaire.
        self.assertNotContains(response, f'value="{self.password}"')
        self.assertNotContains(response, 'value="Different!74"')

        def test_valid_login_opens_session(self):
            """Ouvre une session et redirige vers l’espace de rédaction."""
            response = self.client.post(self.account_url, self.login_data())

            self.assertRedirects(
                response,
                reverse("dashboard:index"),
                fetch_redirect_response=False,
            )
            self.assertEqual(
                self.client.session[SESSION_KEY],
                str(self.user.pk),
            )

    def test_invalid_login_does_not_open_session(self):
        """Affiche une erreur générale lorsque le mot de passe est incorrect."""
        response = self.client.post(
            self.account_url,
            self.login_data(**{"login-password": "Wrong!Password?81"}),
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_deleted_user_cannot_log_in(self):
        """Refuse la connexion d’un compte supprimé logiquement."""
        self.user.deleted_at = timezone.now()
        self.user.save(update_fields=["deleted_at"])

        response = self.client.post(self.account_url, self.login_data())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_post_logout_closes_session(self):
        """Ferme la session sur une requête POST et redirige vers l’accueil."""
        # Initialise une session pour tester uniquement la déconnexion.
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(
            response,
            reverse("home"),
            fetch_redirect_response=False,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_get_logout_does_not_close_session(self):
        """Refuse la déconnexion par GET et conserve la session existante."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:logout"))

        self.assertEqual(response.status_code, 405)
        self.assertIn(SESSION_KEY, self.client.session)

    def test_forms_reject_post_without_csrf_token(self):
        """Refuse les soumissions sans jeton CSRF pour les deux formulaires."""
        # Active explicitement le contrôle CSRF, désactivé par le client standard.
        csrf_client = Client(enforce_csrf_checks=True)

        for data in (self.login_data(), self.registration_data()):
            with self.subTest(action=data["action"]):
                response = csrf_client.post(self.account_url, data)

                self.assertEqual(response.status_code, 403)

        # Les requêtes refusées ne doivent ni créer de compte ni ouvrir de session.
        self.assertEqual(User.objects.count(), 1)
        self.assertNotIn(SESSION_KEY, csrf_client.session)


class AccountAdminTests(TestCase):
    """Teste les accès à l’administration et la modification des comptes."""

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        common_fields = {
            "terms_accepted_at": now,
            "privacy_policy_accepted_at": now,
        }

        cls.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="Admin!47-Foret?92",
            name="Administrator",
            **common_fields,
        )
        cls.regular_user = User.objects.create_user(
            email="reader@example.com",
            password="Reader!83-Nuage?54",
            name="Reader",
            **common_fields,
        )

    def setUp(self):
        # Construit les routes depuis les métadonnées du modèle personnalisé.
        self.admin_base = f"admin:{User._meta.app_label}_{User._meta.model_name}"
        self.list_url = reverse(f"{self.admin_base}_changelist")
        self.change_url = reverse(
            f"{self.admin_base}_change",
            args=[self.regular_user.pk],
        )

    def test_anonymous_visitor_is_redirected_to_admin_login(self):
        """Redirige un visiteur non connecté vers la connexion administrative."""
        response = self.client.get(self.list_url)

        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={self.list_url}",
            fetch_redirect_response=False,
        )

    def test_regular_user_cannot_access_user_management(self):
        """Refuse l’accès administratif à un compte utilisateur ordinaire."""
        self.client.force_login(self.regular_user)

        response = self.client.get(self.list_url)

        self.assertRedirects(
            response,
            f"{reverse('admin:login')}?next={self.list_url}",
            fetch_redirect_response=False,
        )

    def test_staff_without_permissions_cannot_list_users(self):
        """Le statut staff seul ne donne pas accès à la gestion des comptes."""
        self.regular_user.is_staff = True
        self.regular_user.save(update_fields=["is_staff"])
        self.client.force_login(self.regular_user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    def test_superuser_can_list_and_search_users(self):
        """Permet la consultation et la recherche des comptes par e-mail."""
        self.client.force_login(self.admin_user)

        response = self.client.get(
            self.list_url,
            {"q": self.regular_user.email},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["cl"].queryset),
            [self.regular_user],
        )

    def test_superuser_can_open_user_forms(self):
        """Affiche les formulaires de création et de modification personnalisés."""
        self.client.force_login(self.admin_user)

        for url in (
            reverse(f"{self.admin_base}_add"),
            self.change_url,
        ):
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)

    def user_change_data(self, **overrides):
        """Prépare une modification en conservant les données obligatoires."""
        user = self.regular_user
        data = {
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "terms_accepted_at_0": "2026-11-05",
            "terms_accepted_at_1": "10:00:00",
            "privacy_policy_accepted_at_0": "2026-11-05",
            "privacy_policy_accepted_at_1": "10:00:00",
            "_save": "Enregistrer",
        }
        data.update(overrides)
        return data

    def test_profile_update_preserves_password(self):
        """La modification du profil ne remplace pas le mot de passe haché."""
        self.client.force_login(self.admin_user)
        original_password = self.regular_user.password

        response = self.client.post(
            self.change_url,
            self.user_change_data(name="Updated Reader"),
        )

        self.assertRedirects(
            response,
            self.list_url,
            fetch_redirect_response=False,
        )
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.name, "Updated Reader")
        self.assertEqual(self.regular_user.password, original_password)

    def test_duplicate_email_is_rejected_on_update(self):
        """Refuse de remplacer l’e-mail par celui d’un autre compte."""
        self.client.force_login(self.admin_user)

        response = self.client.post(
            self.change_url,
            self.user_change_data(email=self.admin_user.email.upper()),
        )

        self.assertEqual(response.status_code, 200)
        form = response.context["adminform"].form
        self.assertIn("email", form.errors)

        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, "reader@example.com")


class ProfileTests(TestCase):
    """Teste l’accès privé et la modification des informations personnelles."""

    @classmethod
    def setUpTestData(cls):
        cls.password = "Profil!47-Foret?92"
        now = timezone.now()
        common_fields = {
            "terms_accepted_at": now,
            "privacy_policy_accepted_at": now,
        }
        cls.user = User.objects.create_user(
            email="profile@example.com",
            password=cls.password,
            name="Profile User",
            **common_fields,
        )
        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password=cls.password,
            name="Other User",
            **common_fields,
        )

    def setUp(self):
        self.url = reverse("accounts:profile")

    def test_anonymous_visitor_cannot_access_profile(self):
        """Redirige vers la connexion sans modifier les informations."""
        response = self.client.get(self.url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:account')}?next={self.url}",
            fetch_redirect_response=False,
        )

    def test_authenticated_user_sees_own_information(self):
        """Affiche les données du compte connecté."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"]["email"].value(),
            self.user.email,
        )

    def test_update_affects_only_authenticated_user(self):
        """Ignore les identifiants et les privilèges ajoutés à la requête."""
        self.client.force_login(self.user)

        response = self.client.post(
            self.url,
            {
                "name": "Updated User",
                "email": "updated@example.com",
                "current_password": self.password,
                "id": self.other_user.pk,
                "is_superuser": "on",
                "is_staff": "on",
            },
        )

        self.assertRedirects(response, self.url, fetch_redirect_response=False)
        self.user.refresh_from_db()
        self.other_user.refresh_from_db()

        self.assertEqual(self.user.name, "Updated User")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.is_staff)
        self.assertEqual(self.other_user.email, "other@example.com")
        self.assertEqual(self.other_user.name, "Other User")

        # Confirme la persistance et la connexion avec la nouvelle adresse.
        self.client.logout()
        self.assertTrue(
            self.client.login(
                username="updated@example.com",
                password=self.password,
            )
        )
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_invalid_updates_are_rejected(self):
        """Refuse les valeurs invalides sans enregistrer de modification."""
        self.client.force_login(self.user)
        cases = (
            ("email", "invalid-email"),
            ("email", "OTHER@example.com"),
            ("name", ""),
            ("current_password", "Incorrect!73"),
        )

        for field, value in cases:
            with self.subTest(field=field, value=value):
                data = {
                    "name": self.user.name,
                    "email": self.user.email,
                    "current_password": self.password,
                }
                data[field] = value

                response = self.client.post(self.url, data)

                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.user.refresh_from_db()
                self.assertEqual(self.user.email, "profile@example.com")
                self.assertEqual(self.user.name, "Profile User")

    def test_logout_prevents_profile_access_and_update(self):
        """Exige une nouvelle connexion après la fermeture de session."""
        self.client.force_login(self.user)
        self.client.post(reverse("accounts:logout"))

        for method in ("get", "post"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(
                    self.url,
                    {
                        "name": "Unauthorized Change",
                        "email": "changed@example.com",
                        "current_password": self.password,
                    },
                )
                self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "profile@example.com")
        self.assertEqual(self.user.name, "Profile User")


class DeleteAccountTests(TestCase):
    """Teste la suppression du compte et la perte des accès associés."""

    @classmethod
    def setUpTestData(cls):
        cls.password = "Suppression!47-Foret?92"
        now = timezone.now()
        common_fields = {
            "terms_accepted_at": now,
            "privacy_policy_accepted_at": now,
        }
        cls.user = User.objects.create_user(
            email="delete@example.com",
            password=cls.password,
            name="Delete User",
            **common_fields,
        )
        cls.other_user = User.objects.create_user(
            email="other@example.com",
            password=cls.password,
            name="Other User",
            **common_fields,
        )

    def setUp(self):
        self.url = reverse("accounts:delete_account")

    def test_valid_confirmation_deletes_only_current_user(self):
        """Supprime le compte connecté et conserve les autres comptes."""
        self.client.force_login(self.user)
        user_id = self.user.pk

        response = self.client.post(
            self.url,
            {
                "current_password": self.password,
                "confirm_deletion": "on",
                # Un identifiant transmis ne doit pas choisir le compte supprimé.
                "user_id": self.other_user.pk,
            },
        )

        self.assertRedirects(
            response,
            reverse("home"),
            fetch_redirect_response=False,
        )
        self.assertFalse(User.objects.filter(pk=user_id).exists())
        self.assertTrue(User.objects.filter(pk=self.other_user.pk).exists())
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_invalid_confirmation_preserves_account(self):
        """Exige le bon mot de passe et une confirmation explicite."""
        self.client.force_login(self.user)
        cases = (
            (
                {
                    "current_password": "Incorrect!73",
                    "confirm_deletion": "on",
                },
                "current_password",
            ),
            (
                {"current_password": self.password},
                "confirm_deletion",
            ),
        )

        for data, field in cases:
            with self.subTest(field=field):
                response = self.client.post(self.url, data)

                self.assertEqual(response.status_code, 200)
                self.assertIn(field, response.context["form"].errors)
                self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
                self.assertIn(SESSION_KEY, self.client.session)

    def test_get_does_not_delete_account(self):
        """Affiche la confirmation sans déclencher de suppression."""
        self.client.force_login(self.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/delete_account.html")
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_anonymous_user_cannot_delete_account(self):
        """Refuse la suppression sans session authentifiée."""
        response = self.client.post(
            self.url,
            {
                "current_password": self.password,
                "confirm_deletion": "on",
            },
        )

        self.assertRedirects(
            response,
            f"{reverse('accounts:account')}?next={self.url}",
            fetch_redirect_response=False,
        )
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())

    def test_deleted_account_cannot_log_in_or_use_another_session(self):
        """Refuse la reconnexion et l’accès depuis une session déjà ouverte."""
        self.client.force_login(self.user)
        other_session = Client()
        other_session.force_login(self.user)
        email = self.user.email

        self.client.post(
            self.url,
            {
                "current_password": self.password,
                "confirm_deletion": "on",
            },
        )

        self.assertFalse(self.client.login(username=email, password=self.password))

        profile_url = reverse("accounts:profile")
        response = other_session.get(profile_url)

        self.assertRedirects(
            response,
            f"{reverse('accounts:account')}?next={profile_url}",
            fetch_redirect_response=False,
        )

    def test_deletion_requires_csrf_token(self):
        """Refuse une demande sans jeton CSRF valide."""
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        response = csrf_client.post(
            self.url,
            {
                "current_password": self.password,
                "confirm_deletion": "on",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.user.pk).exists())
