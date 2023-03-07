from django.db import models


class IndexableMixin:
    @property
    def index_id(self):
        return f"{self.__class__.__name__}|{self.__str__()}"


class BaseTimeStamp(models.Model):
    """
    Abstract django model class for tables that should have
    columns for 'created' and 'updated' timestamps.
    Use in inheritance.
    """
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Abstract prevents the creation of a BaseTimeStamp table
        abstract = True
