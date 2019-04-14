from werkzeug.wrappers import Response


content_type = 'text/html; charset=UTF-8'

ERROR_MAP = {
    '2': Response('<h1>E2 Not Found File</h1>', content_type=content_type, status=500),
    '13': Response('<h1>E13 No Read Permission</h1>', content_type=content_type, status=500),
    '401': Response('<h1>401 Unknown Or Unsupported Method</h1>', content_type=content_type, status=401),
    '404': Response('<h1>404 Source Not Found<h1>', content_type=content_type, status=404),
    '503': Response('<h1>503 Unknown Function Type</h1>', content_type=content_type, status=503)
}


class SYLFkException(Exception):
    def __init__(self, code='', message='Error'):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message


class EndpointExistsError(SYLFkException):
    def __init__(self, message='Endpoint exists'):
        super(EndpointExistsError, self).__init__(message)


class URLExistsError(SYLFkException):
    def __init__(self, message='URL exists'):
        super(URLExistsError, self).__init__(message)


class FileNotExistsError(SYLFkException):
    def __init__(self, code='2', message='File not found'):
        super(FileNotExistsError, self).__init__(code, message)


class RequireReadPermissionError(SYLFkException):
    def __init__(self, code='13', message='Require read permission'):
        super(RequireReadPermissionError, self).__init__(code, message)


class InvalidRequestMethodError(SYLFkException):
    def __init__(self, code='401', message='Unknown or unsupported request method'):
        super(InvalidRequestMethodError, self).__init__(code, message)


class PageNotFoundError(SYLFkException):
    def __init__(self, code='404', message='Source not found'):
        super(PageNotFoundError, self).__init__(code, message)


class UnknownFuncError(SYLFkException):
    def __init__(self, code='503', message='Unknown function type'):
        super(UnknownFuncError, self).__init__(code, message)


def reload(code):
    def decorator(f):
        ERROR_MAP[str(code)] = f

    return decorator


def capture(f):
    def decorator(*args, **options):
        try:
            rep = f(*args, **options)
        except SYLFkException as e:
            if e.code in ERROR_MAP and ERROR_MAP[e.code]:

                rep = ERROR_MAP[e.code]

                status = int(e.code) if int(e.code) >= 100 else 500

                return rep if isinstance(rep, Response) or rep is None else Response(rep(), content_type=content_type, status=status)
            else:
                raise e
        return rep
    return decorator

