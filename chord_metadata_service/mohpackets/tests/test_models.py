from django.test import TestCase

from chord_metadata_service.mohpackets.models import (
    Program,
    Donor
)

from chord_metadata_service.mohpackets.serializers import (
    DonorSerializer
)


class DonorTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor_values = {
            "submitter_donor_id": "DONOR_1",
            "program_id": self.program,
            "is_deceased": True,
            "cause_of_death": "Died of cancer",
            "date_of_birth": "1975-08",
            "date_of_death": "2009-08",
            "primary_site": [
                "Adrenal gland",
                "Other and ill-defined sites in lip, oral cavity and pharynx",
            ]
        }
        self.donor = Donor.objects.create(**self.donor_values)
        # self.serializer = DonorSerializer(instance=self.donor)

    def test_donor_creation(self):
        self.assertIsInstance(self.donor, Donor)
        self.assertEqual(self.donor.submitter_donor_id, "DONOR_1")
        self.assertEqual(self.donor.program_id, self.program)
        self.assertTrue(self.donor.is_deceased)
        self.assertEqual(self.donor.cause_of_death, "Died of cancer")
        self.assertEqual(self.donor.date_of_birth, "1975-08")
        self.assertEqual(self.donor.date_of_death, "2009-08")
        self.assertEqual(self.donor.primary_site, [
            "Adrenal gland",
            "Other and ill-defined sites in lip, oral cavity and pharynx"
        ])

    def test_invalid_is_deceased(self):
        self.donor_values["is_deceased"] = "foo"
        self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
        self.assertFalse(self.serializer.is_valid())

    def test_invalid_cause_of_death(self):
        self.donor_values["cause_of_death"] = "foo"
        self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
        self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_date_of_death(self):
        self.donor_values["date_of_death"] = "foo"
        self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
        self.assertFalse(self.serializer.is_valid())
        
    def test_invalid_date_of_birth(self):
        self.donor_values["date_of_birth"] = "foo"
        self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
        self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_primary_site(self):
        self.donor_values["primary_site"] = "foo"
        self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
        self.assertFalse(self.serializer.is_valid())

        self.donor_values["primary_site"] = ["foo"]
        self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
        self.assertFalse(self.serializer.is_valid())
