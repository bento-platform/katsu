class PreflightRequestMiddleware:
    """
    Middleware to handle CORS preflight requests that request access for custom headers
    beginning with one of {'X-CANDIG-LOCAL-', 'X-CANDIG-DAC-', 'X-CANDIG-FED-', 'X-CANDIG-EXT-'}.

    Although this project uses django-cors-headers package, this middleware is still necessary
    since django-cors-headers allows you to specify EXACT names for custom headers, but not
    regular expressions. So, django-cors-headers cannot allow access for all custom headers
    that begin with {'X-CANDIG-LOCAL-', 'X-CANDIG-DAC-', 'X-CANDIG-FED-', 'X-CANDIG-EXT-'}.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Checks that the request is a valid CORS preflight request
        if request.method == 'OPTIONS' and 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META and \
            'HTTP_ACCESS_CONTROL_REQUEST_HEADERS' in request.META and \
                response.has_header('ACCESS-CONTROL-ALLOW-HEADERS'):
            access_control_request_headers = request.headers['ACCESS-CONTROL-REQUEST-HEADERS'].split(',')
            headers_to_add = []
            for header in access_control_request_headers:
                header_all_caps = header.upper()
                if header_all_caps.startswith(('X-CANDIG-LOCAL-', 'X-CANDIG-DAC-', 'X-CANDIG-FED-', 'X-CANDIG-EXT-')):
                    headers_to_add.append(header)

            access_control_allow_headers = response['ACCESS-CONTROL-ALLOW-HEADERS']
            if len(access_control_allow_headers) == 0:
                response['ACCESS-CONTROL-ALLOW-HEADERS'] = ', '.join(headers_to_add)
            else:
                response['ACCESS-CONTROL-ALLOW-HEADERS'] = \
                    access_control_allow_headers + ', ' + ', '.join(headers_to_add)

        return response
