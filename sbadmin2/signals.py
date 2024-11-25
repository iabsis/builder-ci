from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Permission
from django.dispatch import receiver

@receiver(user_signed_up)
def add_default_permissions(sender, request, user, **kwargs):
    """
    Ajoute des permissions par défaut aux nouveaux utilisateurs.
    """
    # Permissions à attribuer
    permissions = ['view_build', 'view_buildrequest']

    # Récupérer les permissions correspondantes
    for codename in permissions:
        try:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.add(permission)
        except Permission.DoesNotExist:
            print(f"Permission {codename} introuvable.")

    user.save()