import random

import factory

from chord_metadata_service.mohpackets.models import Donor, Program
from chord_metadata_service.mohpackets.permissible_values import *


class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program
        django_get_or_create = ('program_id',)
        
    # default values
    program_id = factory.Sequence(lambda n: 'PROGRAM_%d' % n)

class DonorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Donor
        django_get_or_create = ('program_id',"submitter_donor_id")
    
    # default values
    submitter_donor_id = factory.Sequence(lambda n: 'DONOR_%d' % n)
    gender = factory.Faker('random_element', elements=GENDER)
    sex_at_birth = factory.Faker('random_element', elements=SEX_AT_BIRTH)
    is_deceased = factory.Faker('boolean')
    lost_to_followup_after_clinical_event_identifier = factory.Faker('random_element', elements=LOST_TO_FOLLOWUP_REASON)
    lost_to_followup_reason = factory.Faker('word')
    date_alive_after_lost_to_followup = factory.Faker('random_int')
    cause_of_death = factory.Faker('random_element', elements=CAUSE_OF_DEATH)
    date_of_birth = factory.Faker('random_int')
    date_of_death = factory.Faker('random_int')
    primary_site = factory.Faker('random_elements', elements=PRIMARY_SITE, length=random.randint(2, 5), unique=True)

    # Set the foreign key program_id using SubFactory
    program_id = factory.SubFactory(ProgramFactory)
    
