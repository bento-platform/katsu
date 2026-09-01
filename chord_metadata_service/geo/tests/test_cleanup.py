from chord_metadata_service.cleanup import run_all_cleanup
from chord_metadata_service.logger import logger
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.phenopackets.tests.constants import valid_biosample_1

from ..cleanup import clean_geolocations
from ..models import GeoLocation
from .constants import GeoLocationTestCase


class GeoCleanupTestCase(GeoLocationTestCase):
    async def test_basic_geo_clean_up(self):
        self.assertEqual(await GeoLocation.objects.acount(), 3)
        # no locations referred to by top-level elements; this should remove them all:
        self.assertEqual(await clean_geolocations(logger), 3)
        self.assertEqual(await GeoLocation.objects.acount(), 0)

    async def test_partial_referenced_geo_clean_up(self):
        individual, _ = await pm.Individual.objects.aget_or_create(id="patient:1", sex="FEMALE")
        biosample_1 = await pm.Biosample.objects.acreate(location_collected=self.loc_1, **valid_biosample_1(individual))

        # one kept behind since biosample above refers to it
        self.assertEqual(await clean_geolocations(logger), 2)
        await biosample_1.location_collected.arefresh_from_db()  # make sure it still exists (i.e., this doesn't raise)

        # remove one individual + one biosample + one location == 3 total removals
        self.assertEqual(await run_all_cleanup(logger), 3)

        self.assertEqual(await pm.Individual.objects.acount(), 0)
        self.assertEqual(await pm.Biosample.objects.acount(), 0)
        self.assertEqual(await GeoLocation.objects.acount(), 0)
