from rest_framework import status
from rest_framework.exceptions import APIException


# https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling


# beacon has its own error response shape
# add a custom beacon exception handler
# def beacon_error_response(message, status_code):
#     return {"meta": response_meta([], None), "error": {"errorCode": status_code, "errorMessage": message}}


class BeaconException(APIException):
    def __init__(self, message="Internal Server Error", status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload


class InvalidQuery(BeaconException):
    def __init__(self, message="Invalid query", status_code=400):
        super().__init__()
        self.message = message
        self.status_code = status_code
