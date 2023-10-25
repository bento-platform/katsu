from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    HormoneTherapy,
    Immunotherapy,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)


@receiver(pre_save, sender=Biomarker)
def create_biomarker_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Comorbidity)
def create_comorbidity_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Exposure)
def create_exposure_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=PrimaryDiagnosis)
def create_primary_diagnosis_foreign_key(sender, instance, **kwargs):
    print("========================pre save signal==================================")
    if not instance.donor_uuid_id:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid_id = donor.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Specimen)
def create_specimen_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            pd = PrimaryDiagnosis.objects.get(
                submitter_primary_diagnosis_id=instance.submitter_primary_diagnosis_id
            )
            instance.primary_diagnosis_uuid = pd.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=SampleRegistration)
def create_sample_registration_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            specimen = Specimen.objects.get(
                submitter_specimen_id=instance.submitter_specimen_id
            )
            instance.specimen_uuid = specimen.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Treatment)
def create_treatment_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            pd = PrimaryDiagnosis.objects.get(
                submitter_primary_diagnosis_id=instance.submitter_primary_diagnosis_id
            )
            instance.primary_diagnosis_uuid = pd.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Chemotherapy)
def create_chemotherapy_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            treatment = Treatment.objects.get(
                submitter_treatment_id=instance.submitter_treatment_id
            )
            instance.treatment_uuid = treatment.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=HormoneTherapy)
def create_hormone_therapy_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            treatment = Treatment.objects.get(
                submitter_treatment_id=instance.submitter_treatment_id
            )
            instance.treatment_uuid = treatment.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Radiation)
def create_radiation_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            treatment = Treatment.objects.get(
                submitter_treatment_id=instance.submitter_treatment_id
            )
            instance.treatment_uuid = treatment.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Immunotherapy)
def create_immunotherapy_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            treatment = Treatment.objects.get(
                submitter_treatment_id=instance.submitter_treatment_id
            )
            instance.treatment_uuid = treatment.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=Surgery)
def create_surgery_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            treatment = Treatment.objects.get(
                submitter_treatment_id=instance.submitter_treatment_id
            )
            instance.treatment_uuid = treatment.uuid
        except Donor.DoesNotExist:
            pass


@receiver(pre_save, sender=FollowUp)
def create_follow_up_foreign_key(sender, instance, **kwargs):
    if not instance.donor_uuid:
        try:
            donor = Donor.objects.get(submitter_donor_id=instance.submitter_donor_id)
            instance.donor_uuid = donor.uuid
            treatment = Treatment.objects.get(
                submitter_treatment_id=instance.submitter_treatment_id
            )
            instance.treatment_uuid = treatment.uuid
            pd = PrimaryDiagnosis.objects.get(
                submitter_primary_diagnosis_id=instance.submitter_primary_diagnosis_id
            )
            instance.primary_diagnosis_uuid = pd.uuid
        except Donor.DoesNotExist:
            pass
