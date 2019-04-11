"""
异常处理
"""

# 异常处理基类
class FkException(Exception):
    def __init__(self, code='', message='Error'):
        self.code = code  # 异常编号
        self.message = message  # 异常信息

    def __str__(self):
        return self.message  # 当作为字符串使用时，返回异常信息
    

# 节点已存在异常
class EndpointExistsError(FkException):
    def __init__(self, message='Endpoint exists'):
        super(EndpointExistsError, self).__init__(message)


# URL 已存在异常
class URLExistsError(FkException):
    def __init__(self, message='URL exists'):
        super(URLExistsError, self).__init__(message)

