import random

import factory

from chord_metadata_service.mohpackets.models import *
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
        django_get_or_create = ("submitter_donor_id",)
    
    # default values
    submitter_donor_id = factory.Sequence(lambda n: 'DONOR_%d' % n)
    gender = factory.Faker('random_element', elements=GENDER)
    sex_at_birth = factory.Faker('random_element', elements=SEX_AT_BIRTH)
    is_deceased = factory.Faker('boolean')
    lost_to_followup_reason = factory.Faker('random_element', elements=LOST_TO_FOLLOWUP_REASON)
    lost_to_followup_after_clinical_event_identifier = factory.Faker('uuid4') 
    date_alive_after_lost_to_followup = factory.Faker('random_int')
    cause_of_death = factory.Faker('random_element', elements=CAUSE_OF_DEATH)
    date_of_birth = factory.Faker('random_int')
    date_of_death = factory.Faker('random_int')
    primary_site = factory.Faker('random_elements', elements=PRIMARY_SITE, length=random.randint(1, 5), unique=True)

    # Set the foreign key
    program_id = factory.SubFactory(ProgramFactory)
    
class PrimaryDiagnosisFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PrimaryDiagnosis
        django_get_or_create = ("submitter_primary_diagnosis_id",)
    
    # Default values
    submitter_primary_diagnosis_id = factory.Sequence(lambda n: 'DIAG_%d' % n)
    date_of_diagnosis = factory.Faker('date', pattern='%Y-%m')
    cancer_type_code = factory.Faker('uuid4')
    basis_of_diagnosis = factory.Faker('random_element', elements=BASIS_OF_DIAGNOSIS)
    laterality = factory.Faker('random_element', elements=PRIMARY_DIAGNOSIS_LATERALITY)
    lymph_nodes_examined_status = factory.Faker('random_element', elements=LYMPH_NODE_STATUS)
    lymph_nodes_examined_method = factory.Faker('random_element', elements=LYMPH_NODE_METHOD)
    number_lymph_nodes_positive = factory.Faker('pyint', min_value=0, max_value=50)
    clinical_tumour_staging_system = factory.Faker('random_element', elements=TUMOUR_STAGING_SYSTEM)
    clinical_t_category = factory.Faker('random_element', elements=T_CATEGORY)
    clinical_n_category = factory.Faker('random_element', elements=N_CATEGORY)
    clinical_m_category = factory.Faker('random_element', elements=M_CATEGORY)
    clinical_stage_group = factory.Faker('random_element', elements=STAGE_GROUP)

    # Set the foreign key
    program_id = factory.SubFactory(ProgramFactory)
    submitter_donor_id = factory.SubFactory(DonorFactory)