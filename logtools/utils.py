import json


REQUEST_META_FIELDS = [
    'REQUEST_METHOD',
    'PATH_INFO',
    'REMOTE_ADDR',
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


def get_request_log_data(request, log_body=False):
    request_data = {
        key.lower(): value for key, value in request.META.items()
        if key in REQUEST_META_FIELDS
    }

    params = None
    try:
        params = getattr(request, request.method).dict()

    except AttributeError:
        pass

    body = request.body if type(request.body) != bytes else request.body.decode('utf-8')
    if not params and request.method != 'GET' and request.content_type == 'application/json':
        params = json.loads(body) if request.body else {}

    if log_body:
        request_data['body'] = body

    request_data['params'] = {
        key.lower(): (str(value) if 'password' not in key else '*********')
        for key, value in params.items()
    } if params is not None else None
    request_data['token'] = request.logtools_token

    return request_data


def get_response_log_data(response):
    return {
        'url': getattr(response, 'url', None),
        'status_code': response.status_code,
        'template_name': getattr(response, 'template_name', None),
        'context_data': str(getattr(response, 'context_data', {})),
        'headers': str(response._headers),
    }
