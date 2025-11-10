from django.test import SimpleTestCase

from chord_metadata_service.phenopackets.utils import time_element_to_str


class PhenopacketUtilsTest(SimpleTestCase):
    def test_time_element_to_str(self):
        subtests = [
            ({"age": {"iso8601duration": "P40Y"}}, "P40Y"),
            ({"age_range": {"start": {"iso8601duration": "P30Y"}, "end": {"iso8601duration": "P33Y"}}}, "P30Y - P33Y"),
            ({"gestational_age": {"weeks": 5}}, "5 weeks"),
            ({"gestational_age": {"weeks": 5, "days": 2}}, "5 weeks 2 days"),
            ({"ontology_class": {"label": "adolescent", "id": "PATO:0001189"}}, "adolescent (PATO:0001189)"),
            (
                {"interval": {"start": "2020-03-15T13:00:00Z", "end": "2020-03-25T09:00:00Z"}},
                "2020-03-15T13:00:00Z - 2020-03-25T09:00:00Z",
            ),
            ({"timestamp": "2020-03-15T13:00:00Z"}, "2020-03-15T13:00:00Z"),
            ({"bad": "asdf"}, None),
        ]

        for params in subtests:
            with self.subTest(params=params):
                if params[1] is None:
                    self.assertIsNone(time_element_to_str(params[0]))
                else:
                    self.assertEqual(time_element_to_str(params[0]), params[1])

    # TODO: test other utilities
