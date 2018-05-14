import logging
import uuid

from django.core.exceptions import PermissionDenied
from django.http import Http404

from .utils import get_request_log_data, get_response_log_data


class LoggingMiddleware(object):
    request_url_blacklist = []
    request_meta_fields = [
        'REQUEST_METHOD',
        'PATH_INFO',
        'SERVER_NAME',
        'SERVER_PROTOCOL',
        'SERVER_PORT',
        'CONTENT_TYPE',
        'CONTENT_LENGTH',
        'HTTP_HOST',
        'HTTP_CONNECTION',
        'HTTP_CACHE_CONTROL',
        'HTTP_USER_AGENT',
        'HTTP_ACCEPT',
        'HTTP_ACCEPT_ENCODING',
        'HTTP_ACCEPT_LANGUAGE',
        'HTTP_COOKIE',
        'CSRF_COOKIE',
    ]
    request_logger = logging.getLogger('logtools.request')
    response_logger = logging.getLogger('logtools.response')
    exception_logger = logging.getLogger('logtools.exception')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_log_data = {}
        if not hasattr(request, 'logtools_token'):
            request.logtools_token = str(uuid.uuid4())

        if request.path not in self.request_url_blacklist:
            request.request_str = '{} {}'.format(request.method, request.path)
            # Requests only logged to path not specified in self.request_url_blacklist
            message = 'Request: ' + request.request_str

            log_data = self.get_log_data(request)
            log_data['request'] = request_log_data = get_request_log_data(request)

            self.request_logger.info(message, extra=log_data)

        response = self.get_response(request)

        if request.path not in self.request_url_blacklist:
            # Responses only logged for paths not specified in self.request_url_blacklist
            message = 'Response: {} => {} {}'.format(
                request.request_str, response.status_code, response.reason_phrase)

            log_data = self.get_log_data(request)
            log_data['request'] = request_log_data
            log_data['response'] = get_response_log_data(response)

            self.response_logger.info(message, extra=log_data)

        return response

    def process_exception(self, request, exception):
        request.exception = exception

        exc_str = (': ' + str(exception)) if str(exception) else ''
        log_data = self.get_log_data(request)
        log_data['request'] = get_request_log_data(request)
        if isinstance(exception, PermissionDenied):
            self.exception_logger.warn(
                'Permission Denied{}'.format(exc_str),
                extra=log_data,
                exc_info=exception)

        elif isinstance(exception, Http404):
            if len(exception.args) and type(exception.args[0]) == dict:
                exc_str = ': ' + exception.args[0]['path']
            self.exception_logger.warn(
                'Not Found{}'.format(exc_str),
                extra=log_data,
                exc_info=exception)

        else:
            self.exception_logger.error(
                'Exception' + exc_str,
                extra=log_data,
                exc_info=exception)

        raise exception

    def get_log_data(self, request):
        return {}
