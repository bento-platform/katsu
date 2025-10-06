from bento_lib.responses import errors
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from chord_metadata_service.authz.middleware import authz_middleware

__all__ = [
    "bad_request",
    "not_found",
]


def bad_request(request: Request, *errs):
    authz_middleware.mark_authz_done(request)  # may have already been done
    return Response(errors.bad_request_error(*errs), status=status.HTTP_400_BAD_REQUEST)


def not_found(request: Request, *errs):
    authz_middleware.mark_authz_done(request)  # may have already been done
    return Response(errors.not_found_error(*errs), status=status.HTTP_404_NOT_FOUND)
