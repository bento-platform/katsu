from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.patients.indices import (
    build_individual_index,
    remove_individual_index
)


@receiver(post_save, sender=Individual)
def index_individual(sender, instance, **kwargs):
    build_individual_index(instance)
    print(f'index_individual_signal {instance.id}')


@receiver(post_delete, sender=Individual)
def remove_individual(sender, instance, **kwargs):
    remove_individual_index(instance)
    print(f'remove_individual_signal {instance.id}')
