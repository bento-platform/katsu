import logging

from django.core.exceptions import ObjectDoesNotExist
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
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)

logger = logging.getLogger(__name__)
"""
    This module contains the SIGNALS for the MoH Models.
    Due to the change to include UUID in each models, the UUID and FK have to be either provided
    upon ingest or in katsu before saving the object
    The pre_save signal should check this saving process before saving to the database
    to ensure the the FK is properly link:
    - If there is no donor_uuid, need to find the Donor and link it
    - If donor_uuid exists, continue

    Author: Son Chau
"""


# helper function
def set_foreign_key(sender, instance, target_model, submitter_id_field, uuid_id_field):
    if not getattr(instance, uuid_id_field) and getattr(
        instance, submitter_id_field
    ):  # and getattr(instance, submitter_id_field)
        try:
            related_object = target_model.objects.get(
                **{
                    submitter_id_field: getattr(instance, submitter_id_field),
                    "program_id": instance.program_id,
                }
            )
            setattr(instance, uuid_id_field, related_object.uuid)
        except ObjectDoesNotExist as e:
            logger.error(
                f"Error setting foreign key for {sender.__name__} instance: {e}"
            )


@receiver(pre_save, sender=Biomarker)
def create_biomarker_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")


@receiver(pre_save, sender=Comorbidity)
def create_comorbidity_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")


@receiver(pre_save, sender=Exposure)
def create_exposure_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")


@receiver(pre_save, sender=PrimaryDiagnosis)
def create_primary_diagnosis_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")


@receiver(pre_save, sender=Specimen)
def create_specimen_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        PrimaryDiagnosis,
        "submitter_primary_diagnosis_id",
        "primary_diagnosis_uuid_id",
    )


@receiver(pre_save, sender=SampleRegistration)
def create_sample_registration_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        Specimen,
        "submitter_specimen_id",
        "specimen_uuid_id",
    )


@receiver(pre_save, sender=Treatment)
def create_treatment_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        PrimaryDiagnosis,
        "submitter_primary_diagnosis_id",
        "primary_diagnosis_uuid_id",
    )


@receiver(pre_save, sender=Chemotherapy)
def create_chemotherapy_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        Treatment,
        "submitter_treatment_id",
        "treatment_uuid_id",
    )


@receiver(pre_save, sender=HormoneTherapy)
def create_hormone_therapy_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        Treatment,
        "submitter_treatment_id",
        "treatment_uuid_id",
    )


@receiver(pre_save, sender=Radiation)
def create_radiation_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        Treatment,
        "submitter_treatment_id",
        "treatment_uuid_id",
    )


@receiver(pre_save, sender=Immunotherapy)
def create_immunotherapy_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        Treatment,
        "submitter_treatment_id",
        "treatment_uuid_id",
    )


@receiver(pre_save, sender=Surgery)
def create_surgery_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        Treatment,
        "submitter_treatment_id",
        "treatment_uuid_id",
    )


@receiver(pre_save, sender=FollowUp)
def create_follow_up_foreign_key(sender, instance, **kwargs):
    set_foreign_key(sender, instance, Donor, "submitter_donor_id", "donor_uuid_id")
    set_foreign_key(
        sender,
        instance,
        Treatment,
        "submitter_treatment_id",
        "treatment_uuid_id",
    )
    set_foreign_key(
        sender,
        instance,
        PrimaryDiagnosis,
        "submitter_primary_diagnosis_id",
        "primary_diagnosis_uuid_id",
    )
