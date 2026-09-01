from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """A management command which clears the site-wide cache."""

    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write("Cleared cache.")
