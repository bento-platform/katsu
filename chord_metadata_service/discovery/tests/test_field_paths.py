from bento_lib.discovery import DiscoveryEntity
from django.test import TestCase, TransactionTestCase

from .constants import DISCOVERY_CONFIG_EXTRA_PROPERTIES, DISCOVERY_CONFIG_TEST
from ..exceptions import DiscoveryFilterRewriteException
from ..field_paths.django_field_query import get_field_django_mapping, get_field_django_mapping_and_queried_entity
from ..field_paths.normalize import normalize_field_path_true_model
from ..field_paths.resolve import resolve_filter_mapping_to_queryset_model


class TestResolveFilterMapping(TestCase):
    def test_resolve_filter_mapping(self):
        subtests: list[tuple[DiscoveryEntity, DiscoveryEntity, tuple[str, ...], bool | None, str]] = [
            # starting at the second discovery entity with the field path, mapping to the first
            ("phenopacket", "individual", ("sex",), None, "subject__sex"),
            ("phenopacket", "individual", ("phenopackets", "subject", "sex"), None, "subject__sex"),
            ("individual", "phenopacket", ("subject", "sex"), None, "sex"),
            ("individual", "phenopacket", ("subject", "phenopackets", "subject", "sex"), None, "sex"),
            ("individual", "phenopacket", ("biosamples", "sampled_tissue"), False, "biosamples__sampled_tissue"),
            (
                "experiment",
                "phenopacket",
                ("biosamples", "experiment", "extra_properties", "prop"),
                None,
                "extra_properties__prop",
            ),
            (
                "experiment",
                "phenopacket",
                ("biosamples", "experiments", "extra_properties", "prop"),
                None,
                "extra_properties__prop",
            ),
            ("individual", "biosample", ("sampled_tissue",), False, "biosamples__sampled_tissue"),
            ("individual", "biosample", ("sampled_tissue",), True, "phenopackets__biosamples__sampled_tissue"),
            ("biosample", "individual", ("sex",), False, "individual__sex"),
            ("biosample", "individual", ("sex",), True, "phenopackets__subject__sex"),
            ("biosample", "phenopacket", ("subject", "sex"), False, "individual__sex"),
            ("biosample", "phenopacket", ("subject", "sex"), True, "phenopackets__subject__sex"),
            ("biosample", "phenopacket", ("biosamples", "sampled_tissue"), None, "sampled_tissue"),
            ("biosample", "experiment", ("biosample", "extra_properties", "prop"), None, "extra_properties__prop"),
            ("experiment", "phenopacket", ("biosamples", "sampled_tissue"), None, "biosample__sampled_tissue"),
            ("experiment", "phenopacket", ("subject", "sex"), False, "biosample__individual__sex"),
            ("experiment", "phenopacket", ("subject", "sex"), True, "biosample__phenopackets__subject__sex"),
            ("experiment", "individual", ("sex",), False, "biosample__individual__sex"),
            ("experiment", "individual", ("sex",), True, "biosample__phenopackets__subject__sex"),
            (
                "experiment",
                "individual",
                ("phenopackets", "biosamples", "experiments", "experiment_type"),
                None,
                "experiment_type",
            ),
            (
                "experiment",
                "individual",
                ("biosamples", "experiments", "experiment_type"),
                None,
                "experiment_type",
            ),
            (
                "experiment",
                "individual",
                ("biosamples", "experiments", "extra_properties", "prop"),
                None,
                "extra_properties__prop",
            ),
            (
                "experiment",
                "individual",
                ("phenopackets", "biosamples", "experiments", "extra_properties", "prop"),
                None,
                "extra_properties__prop",
            ),
            ("experiment_result", "individual", ("sex",), False, "experiments__biosample__individual__sex"),
            ("experiment_result", "individual", ("sex",), True, "experiments__biosample__phenopackets__subject__sex"),
            (
                "experiment_result",
                "phenopacket",
                ("subject", "sex"),
                False,
                "experiments__biosample__individual__sex",
            ),
            (
                "experiment_result",
                "phenopacket",
                ("subject", "sex"),
                True,
                "experiments__biosample__phenopackets__subject__sex",
            ),
            (
                "experiment_result",
                "phenopacket",
                ("biosamples", "experiments", "experiment_results", "genome_assembly_id"),
                None,
                "genome_assembly_id",
            ),
            ("experiment_result", "biosample", ("sampled_tissue",), None, "experiments__biosample__sampled_tissue"),
            (
                "experiment_result",
                "biosample",
                ("experiments", "experiment_results", "genome_assembly_id"),
                None,
                "genome_assembly_id",
            ),
            (
                "experiment_result",
                "experiment",
                ("experiment_results", "genome_assembly_id"),
                None,
                "genome_assembly_id",
            ),
            (
                "individual",
                "experiment_result",
                ("genome_assembly_id",),
                False,
                "biosamples__experiments__experiment_results__genome_assembly_id",
            ),
            (
                "individual",
                "experiment_result",
                ("genome_assembly_id",),
                True,
                "phenopackets__biosamples__experiments__experiment_results__genome_assembly_id",
            ),
            (
                "phenopacket",
                "experiment_result",
                ("genome_assembly_id",),
                None,
                "biosamples__experiments__experiment_results__genome_assembly_id",
            ),
            (
                "biosample",
                "experiment_result",
                ("genome_assembly_id",),
                None,
                "experiments__experiment_results__genome_assembly_id",
            ),
            # TODO: more
        ]

        for params in subtests:
            with self.subTest(params=params):
                if params[3] is None:
                    self.assertEqual(resolve_filter_mapping_to_queryset_model(
                        params[0], params[1], params[2], False
                    ), params[4])
                    self.assertEqual(resolve_filter_mapping_to_queryset_model(
                        params[0], params[1], params[2], True
                    ), params[4])
                else:
                    self.assertEqual(resolve_filter_mapping_to_queryset_model(*params[:4]), params[4])

    def test_resolve_filter_mapping_exc(self):
        # we cannot rewrite these as invalid discovery entities
        subtests: list[tuple[DiscoveryEntity, str, tuple[str, ...]]] = [
            ("biosample", "junk", ("sex",)),
            ("experiment", "junk", ("subject", "sex")),
        ]

        for params in subtests:
            with self.subTest(params=params):
                with self.assertRaises(DiscoveryFilterRewriteException):
                    resolve_filter_mapping_to_queryset_model(*params)


class TestNormalizeFieldPath(TestCase):
    def test_normalize_field_path(self):
        subtests: list[tuple[tuple[DiscoveryEntity, tuple[str, ...]], tuple[DiscoveryEntity, tuple[str, ...]]]] = [
            (
                ("individual", ("phenopackets", "biosamples", "extra_properties", "some_prop")),
                ("biosample", ("extra_properties", "some_prop")),
            ),
            (
                ("phenopacket", ("subject", "sex")),
                ("individual", ("sex",)),
            ),
            (
                ("phenopacket", ("biosamples", "experiments", "extra_properties", "some_prop")),
                ("experiment", ("extra_properties", "some_prop")),
            ),
            (
                ("individual", ("phenopackets", "subject", "sex")),
                ("individual", ("sex",)),
            ),
            (
                ("individual", ("biosamples", "sampled_tissue")),
                ("biosample", ("sampled_tissue",)),
            ),
            (
                ("individual", ("biosamples", "individual", "biosamples", "sampled_tissue")),
                ("biosample", ("sampled_tissue",)),
            ),
            (
                ("phenopacket", ("biosamples", "sampled_tissue")),
                ("biosample", ("sampled_tissue",)),
            ),
            (
                ("phenopacket", ("biosamples", "phenopackets", "biosamples", "sampled_tissue")),
                ("biosample", ("sampled_tissue",)),
            ),
            (
                ("experiment", ("experiment_results", "genome_assembly_id")),
                ("experiment_result", ("genome_assembly_id",)),
            ),
            (
                ("phenopacket", ("biosamples", "experiments", "experiment_results", "genome_assembly_id")),
                ("experiment_result", ("genome_assembly_id",)),
            ),
            # TODO: more
        ]

        for params in subtests:
            with self.subTest(params=params):
                self.assertTupleEqual(normalize_field_path_true_model(*params[0]), params[1])


class TestModelField(TransactionTestCase):

    def test_get_model_field_basic(self):
        field, _, queried_entity = get_field_django_mapping_and_queried_entity(
            "phenopacket", DISCOVERY_CONFIG_TEST.fields["age"]
        )
        self.assertEqual(field, "subject__age_numeric")
        self.assertEqual(
            field, "subject__" + get_field_django_mapping("individual", DISCOVERY_CONFIG_TEST.fields["age"])
        )
        self.assertEqual(queried_entity, "individual")

        field = get_field_django_mapping("experiment", DISCOVERY_CONFIG_TEST.fields["extraction_protocol"])
        self.assertEqual(field, "extraction_protocol")

    def test_get_model_nested_field(self):
        field = get_field_django_mapping(
            "individual", DISCOVERY_CONFIG_EXTRA_PROPERTIES.fields["lab_test_result_value"]
        )
        self.assertEqual(field, "extra_properties__lab_test_result_value")

    def test_get_model_field_rewrite(self):
        field = get_field_django_mapping("phenopacket", DISCOVERY_CONFIG_TEST.fields["age"])
        self.assertEqual(field, "subject__age_numeric")

        # TODO

    def test_get_wrong_model(self):
        with self.assertRaises(DiscoveryFilterRewriteException):
            # noinspection PyTypeChecker
            get_field_django_mapping("junk", DISCOVERY_CONFIG_TEST.fields["age"])
