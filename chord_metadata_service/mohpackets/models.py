from django.db import models

"""
    This module contains the models for the Marathon of Hope app.
    
    The schema are defined in the MOHCCN Clinical Data Model V1: Data Standards Sub-Committee (DSC)
    Model Schema (Google): https://docs.google.com/spreadsheets/d/1pChl2DQiynU0OdueDHW7saJiLliv31GutgNbW8XSfUk/edit#gid=0
    Model Schema (PDF): https://www.marathonofhopecancercentres.ca/docs/default-source/policies-and-guidelines/mohccn-clinical-data-model_v1_endorsed6oct-2022.pdf?Status=Master&sfvrsn=7f6bd159_7
    ER Diagram: https://www.marathonofhopecancercentres.ca/docs/default-source/policies-and-guidelines/mohccn_data_standard_er_diagram_endorsed6oct22.pdf?Status=Master&sfvrsn=dd57a75e_5
    
    NOTES: Permissible values are not enforced in the model.  
    They are checked in the serializer and ingest process.
"""


class Program(models.Model):
    program_id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Program ID: {self.program_id}"


class Donor(models.Model):
    submitter_donor_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    is_deceased = models.BooleanField()
    cause_of_death = models.CharField(max_length=255)
    date_of_birth = models.CharField(max_length=32, null=False, blank=False)
    date_of_death = models.CharField(max_length=32)
    primary_site = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"Donor ID: {self.submitter_donor_id}"


class PrimaryDiagnosis(models.Model):
    submitter_primary_diagnosis_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    date_of_diagnosis = models.CharField(max_length=32, null=False, blank=False)
    cancer_type_code = models.CharField(max_length=64, null=False, blank=False)
    basis_of_diagnosis = models.CharField(max_length=128, null=False, blank=False)
    lymph_nodes_examined_status = models.CharField(
        max_length=128, null=False, blank=False
    )
    lymph_nodes_examined_method = models.CharField(max_length=64)
    number_lymph_nodes_positive = models.IntegerField(blank=True, null=True)
    clinical_tumour_staging_system = models.CharField(max_length=128)
    clinical_t_category = models.CharField(max_length=64)
    clinical_n_category = models.CharField(max_length=64)
    clinical_m_category = models.CharField(max_length=64)
    clinical_stage_group = models.CharField(max_length=64)

    def __str__(self):
        return f"PrimaryDiagnosis ID: {self.submitter_primary_diagnosis_id}"


class Specimen(models.Model):
    submitter_specimen_id = models.CharField(max_length=64, primary_key=True)
    program_id = models.ForeignKey(
        Program, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_donor_id = models.ForeignKey(
        Donor, on_delete=models.CASCADE, null=False, blank=False
    )
    submitter_primary_diagnosis_id = models.ForeignKey(
        PrimaryDiagnosis, on_delete=models.CASCADE, null=False, blank=False
    )
    pathological_tumour_staging_system = models.CharField(max_length=255)
    pathological_t_category = models.CharField(max_length=64)
    pathological_n_category = models.CharField(max_length=64)
    pathological_m_category = models.CharField(max_length=64)
    pathological_stage_group = models.CharField(max_length=64)
    specimen_collection_date = models.CharField(max_length=32, null=False, blank=False)
    specimen_storage = models.CharField(max_length=64, null=False, blank=False)
    tumour_histological_type = models.CharField(max_length=128)
    specimen_anatomic_location = models.CharField(max_length=32)
    reference_pathology_confirmed_diagnosis = models.CharField(max_length=32)
    reference_pathology_confirmed_tumour_presence = models.CharField(max_length=32)
    tumour_grading_system = models.CharField(max_length=128)
    tumour_grade = models.CharField(max_length=64)
    percent_tumour_cells_range = models.CharField(max_length=64)
    percent_tumour_cells_measurement_method = models.CharField(max_length=64)

    def __str__(self):
        return f"Specimen ID: {self.submitter_specimen_id}"
