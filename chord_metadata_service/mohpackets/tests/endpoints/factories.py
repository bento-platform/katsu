import random

import factory
from django.db.models.signals import post_save

from chord_metadata_service.mohpackets.models import *
from chord_metadata_service.mohpackets.permissible_values import *


class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program
        django_get_or_create = ('program_id',)
        
    # default values
    program_id = factory.Sequence(lambda n: 'PROGRAM_%d' % n)


    # @factory.post_generation
    # def set_lost_to_followup_identifier(self, create, extracted, **kwargs):
    #     if not create:
    #         return
    #     if extracted:
    #         # If identifier is passed during creation, use it
    #         self.lost_to_followup_after_clinical_event_identifier = extracted
    #     else:
    #         # If identifier is not passed, create one
    #         DonorFactory(
    #             lost_to_followup_after_clinical_event_identifier=self
    #         )
    

class DonorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Donor
        django_get_or_create = ("submitter_donor_id",)
    
    # default values
    submitter_donor_id = factory.Sequence(lambda n: 'DONOR_%d' % n)
    gender = factory.Faker('random_element', elements=GENDER)
    sex_at_birth = factory.Faker('random_element', elements=SEX_AT_BIRTH)
    is_deceased = factory.Faker('boolean')
    lost_to_followup_reason = None
    lost_to_followup_after_clinical_event_identifier = None
    date_alive_after_lost_to_followup = None
    cause_of_death = None
    date_of_birth = factory.Faker('random_int')
    date_of_death = factory.Faker('random_int')
    primary_site = factory.Faker('random_elements', elements=PRIMARY_SITE, length=random.randint(1, 5), unique=True)
    program_id = factory.SubFactory(ProgramFactory)

    @factory.lazy_attribute
    def cause_of_death(self):
        if self.is_deceased:
            return factory.Faker('random_element', elements=CAUSE_OF_DEATH)



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
    program_id = factory.SelfAttribute('submitter_donor_id.program_id')
    submitter_donor_id = factory.SubFactory(DonorFactory)
    
    # @factory.post_generation
    # def set_clinical_event_identifier(self, create, extracted, **kwargs):
    #     donor = self.submitter_donor_id
    #     if not donor.is_deceased:
    #         donor.lost_to_followup_after_clinical_event_identifier = self.submitter_primary_diagnosis_id
    #         donor.lost_to_followup_reason = random.choice(LOST_TO_FOLLOWUP_REASON)
    #         donor.date_alive_after_lost_to_followup = factory.Faker('random_int')
    #         donor.save()