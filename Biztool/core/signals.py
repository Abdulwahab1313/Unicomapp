from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Wallet, BusinessProfile

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=User)
def create_business_profile(sender, instance, created, **kwargs):
    if created:
        BusinessProfile.objects.create(user=instance)
