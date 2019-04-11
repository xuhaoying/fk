"""
WSGI 入口
大部分工作 werkzeug 已经做好了，
只需要在获取请求和返回响应之间，把逻辑交由框架去处理即可
"""

from werkzeug.wrappers import Request

# WSGI 调度框架入口
def wsgi_app(app, environ, start_response):
    """
    第一个参数 app 应用
    第二个参数 environ 服务器传递过来的请求
    第三个参数 start_response  响应载体，连同响应结果一同传回给服务器即可
    """

    # 解析请求头
    request = Request(environ)

    # 把请求传给框架的路由进行处理， 并获取处理结果
    response = app.dispatch_request(request)

    # 返回给服务器
    return response(environ, start_response)

