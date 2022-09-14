from drf_spectacular.extensions import OpenApiAuthenticationExtension


class BentoRemoteUserAuthenticationScheme(OpenApiAuthenticationExtension):
    """
        This class provides the custom authentication scheme for drf-spectacular
        so we can test the API with authentication and unauthorized requests
    """
    target_class = 'bento_lib.auth.django_remote_user.BentoRemoteUserAuthentication'
    name = 'BentoRemoteUserAuthentication'

    # TODO: this is a temporaty fix for the issue with the authentication scheme
    # not being picked up by drf-spectacular
    # Once we figure out how to implement BentoRemoteUserAuthentication, we can
    # fill this in
    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'api_key',
        }
