import factory

from chord_metadata_service.mohpackets.models import Program


class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program
        django_get_or_create = ('program_id',)
        
    # default values
    program_id = factory.Sequence(lambda n: 'PROGRAM_%d' % n)