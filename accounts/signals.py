from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Ensure every user has a Profile (also covers users created via
    register endpoint and the admin). Existing users created before this
    signal are handled by a data migration and the get_or_create accessor."""
    if created:
        Profile.objects.get_or_create(user=instance)
