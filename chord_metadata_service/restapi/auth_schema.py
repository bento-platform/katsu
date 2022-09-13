from drf_spectacular.extensions import OpenApiAuthenticationExtension

class BentoRemoteUserAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'bento_lib.auth.django_remote_user.BentoRemoteUserAuthentication'
    name = 'BentoRemoteUserAuthentication'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'api_key',
        }
