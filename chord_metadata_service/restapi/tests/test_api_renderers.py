from django.test import SimpleTestCase

from ..api_renderers import PassThruCSVRenderer, PassThruTSVManifestRenderer, PassThruXLSXRenderer


class PassThruRendererTest(SimpleTestCase):
    def test_pass_thru_renderers_return_data_unchanged(self):
        data = b"already-rendered"
        for renderer_class in (PassThruCSVRenderer, PassThruXLSXRenderer, PassThruTSVManifestRenderer):
            with self.subTest(renderer=renderer_class.__name__):
                self.assertIs(renderer_class().render(data), data)
