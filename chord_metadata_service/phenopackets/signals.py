from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.apps import apps


# TODO move to separate utils
def get_models_names(app_name):
	""" Return a list of all models names in the app """

	app_models = apps.get_app_config(app_name).get_models()
	return [model.__name__ for model in app_models]

# define what models should be indexed
index_models = ['Biosample', 'Procedure', 'PhenotypicFeature']


@receiver(post_save)
def add_to_index(sender, instance, **kwargs):
	if sender.__name__ in index_models:
		instance.indexing()


@receiver(post_delete)
def remove_instance(sender, instance, **kwargs):
	if sender.__name__ in index_models:
		instance.delete_from_index()


@receiver(pre_save)
def update_instance(sender, instance, *args, **kwargs):
	if sender.__name__ in index_models:
		instance.update_index()
