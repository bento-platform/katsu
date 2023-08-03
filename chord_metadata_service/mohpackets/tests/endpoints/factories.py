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
    cause_of_death = factory.Maybe(
        'is_deceased',
        yes_declaration=factory.Faker('random_element', elements=CAUSE_OF_DEATH),
        no_declaration=None,
    )
    date_of_birth = factory.Faker('random_int')
    date_of_death = factory.Maybe(
        'is_deceased',
        yes_declaration=factory.Faker('random_int', min=date_of_birth),
        no_declaration=None,
    )
    primary_site = factory.Faker('random_elements', elements=PRIMARY_SITE, length=random.randint(1, 5), unique=True)

    # set foregin key
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

    # Set the foreign keys
    program_id = factory.SelfAttribute('submitter_donor_id.program_id')
    submitter_donor_id = factory.SubFactory(DonorFactory)
    
    @factory.post_generation
    def set_clinical_event_identifier(self, create, extracted, **kwargs):
        donor = self.submitter_donor_id
        if not donor.is_deceased:
            donor.lost_to_followup_after_clinical_event_identifier = self.submitter_primary_diagnosis_id
            donor.lost_to_followup_reason = random.choice(LOST_TO_FOLLOWUP_REASON)
            donor.date_alive_after_lost_to_followup = random.randint(1000, 5000)
            donor.save()
            
class SpecimenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Specimen
        django_get_or_create = ("submitter_specimen_id",)

    # default values
    submitter_specimen_id = factory.Sequence(lambda n: 'SPECIMEN_%d' % n)
    pathological_tumour_staging_system = factory.Faker('random_element', elements=TUMOUR_STAGING_SYSTEM)
    pathological_t_category = factory.Faker('random_element', elements=T_CATEGORY)
    pathological_n_category = factory.Faker('random_element', elements=N_CATEGORY)
    pathological_m_category = factory.Faker('random_element', elements=M_CATEGORY)
    pathological_stage_group = factory.Faker('random_element', elements=STAGE_GROUP)
    specimen_collection_date = factory.Faker('random_int')
    specimen_storage = factory.Faker('random_element', elements=STORAGE)
    specimen_processing = factory.Faker('random_element', elements=SPECIMEN_PROCESSING)
    tumour_histological_type = factory.Faker('word')
    specimen_anatomic_location = factory.Faker('word')
    specimen_laterality = factory.Faker('random_element', elements=SPECIMEN_LATERALITY)
    reference_pathology_confirmed_diagnosis = factory.Faker('random_element', elements=CONFIRMED_DIAGNOSIS_TUMOUR)
    reference_pathology_confirmed_tumour_presence = factory.Faker('random_element', elements=CONFIRMED_DIAGNOSIS_TUMOUR)
    tumour_grading_system = factory.Faker('random_element', elements=TUMOUR_GRADING_SYSTEM)
    tumour_grade = factory.Faker('random_element', elements=TUMOUR_GRADE)
    percent_tumour_cells_range = factory.Faker('random_element', elements=PERCENT_CELLS_RANGE)
    percent_tumour_cells_measurement_method = factory.Faker('random_element', elements=CELLS_MEASURE_METHOD)

    # set foregin keys
    program_id = factory.SelfAttribute('submitter_primary_diagnosis_id.program_id')
    submitter_donor_id = factory.SelfAttribute('submitter_primary_diagnosis_id.submitter_donor_id')
    submitter_primary_diagnosis_id = factory.SubFactory(PrimaryDiagnosisFactory)
    
class SampleRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SampleRegistration
        django_get_or_create = ("submitter_sample_id",)

    # default values
    submitter_sample_id = factory.Sequence(lambda n: 'SAMPLE_%d' % n)
    specimen_tissue_source = factory.Faker('random_element', elements=SPECIMEN_TISSUE_SOURCE)
    tumour_normal_designation = factory.Faker('random_element', elements=["Normal", "Tumour"])
    specimen_type = factory.Faker('random_element', elements=SPECIMEN_TYPE)
    sample_type = factory.Faker('random_element', elements=SAMPLE_TYPE)

    # set foregin keys
    program_id = factory.SelfAttribute('submitter_specimen_id.program_id')
    submitter_donor_id = factory.SelfAttribute('submitter_specimen_id.submitter_donor_id')
    submitter_specimen_id = factory.SubFactory(SpecimenFactory)