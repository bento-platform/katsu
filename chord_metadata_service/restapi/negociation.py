from rest_framework.negotiation import DefaultContentNegotiation

# Django Rest Framework provides a default content negociation strategy that
# picks the desired renderer based on the accept-type content of the request or
# a format parameter found in the url (either using `format=` or a file suffix
# in the url such as `.json`)
# To be able to use a format argument passed in the content of the request body
# we need to override the content negociation class


class FormatInPostContentNegotiation(DefaultContentNegotiation):

    def select_renderer(self, request, renderers, format_suffix):
        """
        Select renderer based on the `format` parameter from the (POST) request.
        If not found, default to the default negociation strategy.
        """
        format_param = request.data.get("format", None)
        renderer = next((r for r in renderers if r.format == format_param), None)
        if renderer:
            return (renderer, renderer.media_type)

        return super(FormatInPostContentNegotiation, self).select_renderer(request, renderers, format_suffix)
