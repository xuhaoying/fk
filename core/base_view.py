from fk.view import View
from fk.session import AuthSession, session

class BaseView(View):
    # 定义支持的请求方法，默认支持 GET 和 POST 方法
    methods = ['GET', 'POST']

    # POST 请求处理函数
    def post(self, request, *args, **options):
        pass
    
    # GET 请求处理函数
    def get(self, request, *args, **options):
        pass

    # 视图处理函数调度入口
    def dispath_request(self, request, *args, **options):
        # 定义请求方法与处理函数的映射
        methods_meta = {
            'GET': self.get,
            'POST': self.post,
        }

        # 判断该视图是否支持所请求的方法， 如果支持则返回对应的处理函数的结果，否则返回错误提示
        if request.method in methods_meta:
            return methods_meta[request.method](request, *args, **options)
        else:
            return '<h1>Unknow or unsupported require method.</h1>'


# 登录验证类
class AuthLogin(AuthSession):
    # 如果没有验证通过，则返回一个链接点击到登录页面
    @staticmethod
    def auth_fail_callback(request, *args, **options):
        return '<a href="/login">登录</a>'
    
    # 验证逻辑，如果 user 这个键不在会话当中，则验证失败，反之则成功
    @staticmethod
    def auth_logic(request, *args, **options):
        if 'user' in session.map(request):
            return True
        return False


# 会话视图基类
class SessionView(BaseView):
    # 验证类装饰器
    @AuthLogin.auth_session
    def dispatch_request(self, request, *args, **kwargs):
        # 结合装饰器内部的逻辑，调用继承的子类的 dispatch_request 方法
        return super(SessionView, self).dispatch_request(
                request, *args, **options)





















