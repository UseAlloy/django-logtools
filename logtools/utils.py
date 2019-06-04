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


def get_request_log_data(request):
    request_data = {
        key.lower(): value for key, value in request.META.items()
        if key in REQUEST_META_FIELDS
    }

    params = getattr(request, request.method, None).dict()
    request_data['params'] = {
        key.lower(): (str(value) if 'password' not in key else '*********')
        for key, value in params.items()
    } if params is not None else None

    body = request.body if type(request.body) != bytes else request.body.decode('utf-8')
    if body and request.content_type == 'application/json':
        body = json.loads(body)
    request_data['body'] = body

    if request.method != 'GET':
        request_data['get_params'] = dict(request.GET)

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
