from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Election)
def automate_token_issuance(sender, instance, created, **kwargs):
    if created:
        instance.issue_tokens()
