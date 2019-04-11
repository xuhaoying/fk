
from werkzeug.serving import run_simple
from werkzeug.wrappers import Response
from fk.wsgi_adapter import wsgi_app

# 框架
class Fk(object):
    
    # 实例化方法
    def __init__(self):
        self.host = '127.0.0.1'  # 默认主机
        self.port = 23333  # 默认端口

    # 路由
    def dispatch_request(self):
        status = 200  # HTTP状态码200， 表示请求成功

        # 定义响应头的 Server 属性
        headers = {
            'Server': 'Framework'
        }

        # 返回 WSGI 规定的响应体给 WSGI 模块
        return Response('<h1>Hello, Framework!</h1>',
                    content_type='text/html',
                    headers=headers, status=status)

    # 启动入口
    def run(self, host=None, port=None, **options):
        # 如果有参数传入且值不为空，则赋值
        for key, value in options:
            if value is not None:
                self.__setattr__(key, value)

        # 如果 host 不为None， 则按传入的host设置主机
        if host:
            self.host = host

        # 如果 port 不为None， 则按传入的host设置端口
        if port:
            self.port = port

        # 把框架本身和其他几个配置参数传给 werkzeug 里的 run_simple
        run_simple(hostname=self.host, port=self.port,
                application=self, **options)

    # 框架被 WSGI 调用入口的方法
    def __call__(self):
        return wsgi_app(self, environ, start_response)
