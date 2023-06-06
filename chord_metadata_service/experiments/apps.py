from django.apps import AppConfig


class ExperimentsConfig(AppConfig):
    name = 'chord_metadata_service.experiments'

    def ready(self) -> None:
        import chord_metadata_service.experiments.signals  # noqa: F401
