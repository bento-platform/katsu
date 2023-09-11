import logging
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Gene
from . import models as m
from django.utils import timezone

from typing import Optional

logger = logging.getLogger("mcode_ingest")
logger.setLevel(logging.INFO)


def _logger_message(created, obj):
    if created:
        logger.info(f"New {obj.__class__.__name__} {obj.id} created")
    else:
        logger.info(f"Existing {obj.__class__.__name__} {obj.id} retrieved")


def ingest_mcodepacket(mcodepacket_data, dataset_id, idx: Optional[int] = None):
    """ Ingests a single mcodepacket in mcode app and patients' metadata into patients app."""

    new_mcodepacket = {"id": mcodepacket_data["id"]}
    subject = mcodepacket_data["subject"]
    genomics_report_data = mcodepacket_data.get("genomics_report", None)
    cancer_condition_data = mcodepacket_data.get("cancer_condition", None)
    cancer_related_procedures = mcodepacket_data.get("cancer_related_procedures", None)
    medication_statement_data = mcodepacket_data.get("medication_statement", None)
    date_of_death_data = mcodepacket_data.get("date_of_death", None)
    cancer_disease_status_data = mcodepacket_data.get("cancer_disease_status", None)
    tumor_marker_data = mcodepacket_data.get("tumor_marker", None)

    # get and create Patient
    if subject:
        subject, s_created = m.Individual.objects.get_or_create(
            id=subject["id"],
            defaults={
                "alternate_ids": subject.get("alternate_ids", None),
                "date_of_birth": subject.get("date_of_birth", None),
                "sex": subject.get("sex", None),
                "karyotypic_sex": subject.get("karyotypic_sex", ""),
                "taxonomy": subject.get("taxonomy", None),
                "active": subject.get("active", False),
                "deceased": subject.get("deceased", False),
                "comorbid_condition": subject.get("comorbid_condition", None),
                "ecog_performance_status": subject.get("ecog_performance_status", None),
                "karnofsky": subject.get("karnofsky", None),
                "race": subject.get("race", ""),
                "ethnicity": subject.get("ethnicity", ""),
                "extra_properties": subject.get("extra_properties", None),
            }
        )
        _logger_message(s_created, subject)
        new_mcodepacket["subject"] = subject.id

    if genomics_report_data:
        new_genomics_report = {}
        # Genetic Variant
        if "genetic_variant" in genomics_report_data and genomics_report_data["genetic_variant"]:
            # Create or get Gene
            genes_studied = []
            if "gene_studied" in genomics_report_data["genetic_variant"]:
                for gene_item in genomics_report_data["genetic_variant"]["gene_studied"]:
                    gene, g_created = Gene.objects.get_or_create(
                        id=gene_item["id"],
                        defaults={
                            "alternate_ids": gene_item.get(
                                "alternate_ids", []
                            ),
                            "symbol": gene_item["symbol"],
                            "extra_properties": gene_item.get(
                                "extra_properties", None
                            )
                        }
                    )
                    genes_studied.append(gene)
            # Create or get Genetic variant
            genetic_variant, gv_created = m.CancerGeneticVariant.objects.get_or_create(
                id=genomics_report_data["genetic_variant"]["id"],
                defaults={
                    "data_value": genomics_report_data["genetic_variant"].get("data_value", None),
                    "method": genomics_report_data["genetic_variant"].get("method", None),
                    "amino_acid_change": genomics_report_data["genetic_variant"].get("amino_acid_change", None),
                    "amino_acid_change_type": genomics_report_data["genetic_variant"].get(
                        "amino_acid_change_type", None
                    ),
                    "cytogenetic_location": genomics_report_data["genetic_variant"].get("cytogenetic_location", None),
                    "cytogenetic_nomenclature": genomics_report_data["genetic_variant"].get(
                        "cytogenetic_nomenclature", None
                    ),
                    "genomic_dna_change": genomics_report_data["genetic_variant"].get("genomic_dna_change", None),
                    "genomic_source_class": genomics_report_data["genetic_variant"].get("genomic_source_class", None),
                    "variation_code": genomics_report_data["genetic_variant"].get("variation_code", None),
                    "extra_properties": genomics_report_data["genetic_variant"].get("extra_properties", None)
                }
            )
            if genes_studied:
                genetic_variant.gene_studied.set(genes_studied)

            new_genomics_report["genetic_variant"] = genetic_variant

        # Genomic Region Studied
        if "genomic_region_studied" in genomics_report_data and genomics_report_data["genomic_region_studied"]:
            genomic_region_studied, grs_created = m.GenomicRegionStudied.objects.get_or_create(
                id=genomics_report_data["genomic_region_studied"]["id"],
                defaults={
                    "dna_ranges_examined": genomics_report_data["genomic_region_studied"].get(
                        "dna_ranges_examined", None
                    ),
                    "dna_region_description": genomics_report_data["genomic_region_studied"].get(
                        "dna_region_description", []
                    ),
                    "gene_mutation": genomics_report_data["genomic_region_studied"].get("gene_mutation", None),
                    "gene_studied": genomics_report_data["genomic_region_studied"].get("gene_studied", None),
                    "genomic_reference_sequence_id": genomics_report_data["genomic_region_studied"].get(
                        "genomic_reference_sequence_id", None
                    ),
                    "genomic_region_coordinate_system": genomics_report_data["genomic_region_studied"].get(
                        "genomic_region_coordinate_system", None
                    ),
                    "extra_properties": genomics_report_data["genomic_region_studied"].get(
                        "extra_properties", None
                    )
                }
            )
            new_genomics_report["genomic_region_studied"] = genomic_region_studied

        # Genetic Specimen
        genetic_specimens = []
        if "genetic_specimen" in genomics_report_data and genomics_report_data["genetic_specimen"]:
            for specimen in genomics_report_data["genetic_specimen"]:
                genetic_specimen, gs_created = m.GeneticSpecimen.objects.get_or_create(
                    id=specimen["id"],
                    defaults={
                        "specimen_type": specimen["specimen_type"],
                        "collection_body": specimen.get("collection_body", None),
                        "laterality": specimen.get("laterality", None),
                        "extra_properties": specimen.get("extra_properties", None),
                    }
                )
                genetic_specimens.append(genetic_specimen)

        genomics_report, gr_created = m.GenomicsReport.objects.get_or_create(
            id=genomics_report_data["id"],
            defaults={
                "code": genomics_report_data["code"],
                "performing_organization_name": genomics_report_data.get("performing_organization_name", None),
                "issued": genomics_report_data.get("issued", None),
                "genetic_variant": new_genomics_report.get("genetic_variant", None),
                "genomic_region_studied": new_genomics_report.get("genomic_region_studied", None),
                "extra_properties": genomics_report_data.get("extra_properties", None),
            }
        )
        if genetic_specimens:
            genomics_report.genetic_specimen.set(genetic_specimens)

        new_mcodepacket["genomics_report"] = genomics_report

    else:
        pass

    # get and create CancerCondition
    cancer_conditions = []
    if cancer_condition_data:
        cc = cancer_condition_data
        cancer_condition, cc_created = m.CancerCondition.objects.get_or_create(
            id=cc["id"],
            defaults={
                "code": cc["code"],
                "condition_type": cc["condition_type"],
                "clinical_status": cc.get("clinical_status", None),
                "verification_status": cc.get("verification_status", None),
                "date_of_diagnosis": cc.get("date_of_diagnosis", None),
                "body_site": cc.get("body_site", None),
                "laterality": cc.get("laterality", None),
                "histology_morphology_behavior": cc.get("histology_morphology_behavior", None),
                "extra_properties": cc.get("extra_properties", None)
            }
        )
        _logger_message(cc_created, cancer_condition)
        cancer_conditions.append(cancer_condition.id)
        new_mcodepacket["cancer_condition"] = cancer_condition
        if "tnm_staging" in cc:
            for tnms in cc["tnm_staging"]:
                tnm_staging, tnms_created = m.TNMStaging.objects.get_or_create(
                    id=tnms["id"],
                    defaults={
                        "cancer_condition": cancer_condition,
                        "stage_group": tnms["stage_group"],
                        "tnm_type": tnms["tnm_type"],
                        "primary_tumor_category": tnms.get("primary_tumor_category", None),
                        "regional_nodes_category": tnms.get("regional_nodes_category", None),
                        "distant_metastases_category": tnms.get("distant_metastases_category", None),
                        "extra_properties": tnms.get("extra_properties", None)
                    }
                )
                _logger_message(tnms_created, tnm_staging)

    # get and create Cancer Related Procedure
    crprocedures = []
    if cancer_related_procedures:
        for crp in cancer_related_procedures:
            cancer_related_procedure, crp_created = m.CancerRelatedProcedure.objects.get_or_create(
                id=crp["id"],
                defaults={
                    "code": crp["code"],
                    "procedure_type": crp["procedure_type"],
                    "body_site": crp.get("body_site", None),
                    "laterality": crp.get("laterality", None),
                    "treatment_intent": crp.get("treatment_intent", None),
                    "reason_code": crp.get("reason_code", None),
                    "extra_properties": crp.get("extra_properties", None)
                }
            )
            _logger_message(crp_created, cancer_related_procedure)
            crprocedures.append(cancer_related_procedure.id)
            if "reason_reference" in crp:
                related_cancer_conditions = []
                for rr_id in crp["reason_reference"]:
                    condition = m.CancerCondition.objects.get(id=rr_id)
                    related_cancer_conditions.append(condition)
                cancer_related_procedure.reason_reference.set(related_cancer_conditions)

    # get and create MedicationStatements
    medication_statements = []
    if medication_statement_data:
        for ms in medication_statement_data:
            medication_statement, ms_created = m.MedicationStatement.objects.get_or_create(
                id=ms["id"],
                defaults={
                    "medication_code": ms["medication_code"],
                    "termination_reason": ms.get("termination_reason", None),
                    "treatment_intent": ms.get("treatment_intent", None),
                    "start_date": ms.get("start_date", None),
                    "end_date": ms.get("end_date", None),
                    "extra_properties": ms.get("extra_properties", None)
                }
            )
            _logger_message(ms_created, medication_statement)
            medication_statements.append(medication_statement.id)

    # get date of death
    if date_of_death_data:
        new_mcodepacket["date_of_death"] = date_of_death_data

    # get cancer disease status
    if cancer_disease_status_data:
        new_mcodepacket["cancer_disease_status"] = cancer_disease_status_data

    # get tumor marker
    tumor_markers = []
    if tumor_marker_data:
        for tm in tumor_marker_data:
            tumor_marker, tm_created = m.LabsVital.objects.get_or_create(
                id=tm["id"],
                defaults={
                    "tumor_marker_code": tm["tumor_marker_code"],
                    "tumor_marker_data_value": tm.get("tumor_marker_data_value", None),
                    "individual": m.Individual.objects.get(id=tm["individual"]),
                    "extra_properties": tm.get("extra_properties", None)
                }
            )
            _logger_message(tm_created, tumor_marker)
            tumor_markers.append(tumor_marker.id)

    mcodepacket = m.MCodePacket(
        id=new_mcodepacket["id"],
        subject=Individual.objects.get(id=new_mcodepacket["subject"]),
        genomics_report=new_mcodepacket.get("genomics_report", None),
        cancer_condition=new_mcodepacket.get("cancer_condition", None),
        date_of_death=new_mcodepacket.get("date_of_death", ""),
        cancer_disease_status=new_mcodepacket.get("cancer_disease_status", None),
        extra_properties=mcodepacket_data.get("extra_properties", None),
        dataset_id=dataset_id,
        updated=timezone.now()
    )
    mcodepacket.save()
    logger.info(f"New Mcodepacket {mcodepacket.id} created (idx={idx})")
    if crprocedures:
        mcodepacket.cancer_related_procedures.set(crprocedures)
    if medication_statements:
        mcodepacket.medication_statement.set(medication_statements)
    if tumor_markers:
        mcodepacket.tumor_marker.set(tumor_markers)

    return mcodepacket
