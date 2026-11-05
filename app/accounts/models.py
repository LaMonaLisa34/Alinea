from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Gère la création des utilisateurs et des superutilisateurs."""

    def create_user(self, email, password=None, **extra_fields):
        """Crée un utilisateur et enregistre son mot de passe sous forme hachée."""
        if not email:
            raise ValueError("Une adresse e-mail est obligatoire.")

        # Uniformise la casse de l’adresse avant son enregistrement.
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)

        # Délègue le hachage du mot de passe au mécanisme de Django.
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crée un utilisateur disposant des privilèges d’administration."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Refuse une configuration incompatible avec le statut de superutilisateur.
        if extra_fields["is_staff"] is not True:
            raise ValueError("Un superutilisateur doit avoir is_staff=True.")
        if extra_fields["is_superuser"] is not True:
            raise ValueError("Un superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Représente un compte Alinea identifié par son adresse e-mail.

    AbstractBaseUser fournit notamment le mot de passe et la dernière connexion.
    PermissionsMixin ajoute les groupes, les permissions et le statut de
    superutilisateur.
    """

    # Identité et rôle applicatif.
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=30, default="user")

    # Dates de création et de dernière modification du compte.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Dates d’acceptation des conditions et de la politique de confidentialité.
    terms_accepted_at = models.DateTimeField()
    privacy_policy_accepted_at = models.DateTimeField()

    # La suppression logique conserve l’enregistrement en base.
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Autorise l’accès à l’administration, sous réserve des permissions.
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # Utilise l’adresse e-mail comme identifiant d’authentification.
    USERNAME_FIELD = "email"

    # Champs supplémentaires demandés par la commande createsuperuser.
    # La validation du formulaire d’inscription est définie séparément.
    REQUIRED_FIELDS = [
        "name",
        "terms_accepted_at",
        "privacy_policy_accepted_at",
    ]

    class Meta:
        db_table = "users"

    @property
    def is_active(self):
        """Indique si le compte est actif selon son état de suppression."""
        return self.deleted_at is None
