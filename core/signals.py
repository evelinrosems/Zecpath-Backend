from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, Employer, Candidate, UserRole


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:

        if instance.role == UserRole.EMPLOYER:
            Employer.objects.get_or_create(
                user=instance,
                defaults={
                    "company_name": f"{instance.name}'s Company"
                }
            )

        elif instance.role == UserRole.CANDIDATE:
            Candidate.objects.get_or_create(
                user=instance,
                defaults={
                    "phone": instance.phone
                }
            )