from fk import Fk, simple_template
from fk.session import session
from fk.view import Controller

from core.base_view import BaseView, SessionView


# 首页视图
class Index(SessionView):
    def get(self, request):
        # 获取当前会话中的 user 值
        user = session.get(request, 'user')
        # 把 user 的值用模板引擎置换到页面中并返回
        return simple_template(
            'index.html', user=user, message="Hello world!")


# 登录视图
class Login(BaseView):
    def get(self, request):
        return simple_template('login.html')

    def post(self, request):
        # 从 POST 请求中获取 user 参数的值
        user = request.form.get('user')

        # 把 user 存放到当前会话中
        session.push(request, 'user', user)

        # 返回登录成功提示和首页链接
        return '登录成功， <a href="/">返回</a>'


# 登出视图
class Logout(SessionView):
    def get(self, request):
        # 从当前会话中删除 user
        session.pop(request, 'user')
        # 返回登出成功提示和首页链接
        return '登出成功， <a href="/">返回</a>'


class Test(Index):
    def post(self, request):
        return "这是一个 POST 请求"


app = Fk()

#  URL 和 处理函数 的分离
fk_url_map = [
    {
        'url': '/',
        'view': Index,
        'endpoint': 'index',
    },
    {
        'url': '/login',
        'view': Login,
        'endpoint': 'login',
    },
    {
        'url': '/logout',
        'view': Logout,
        'endpoint': 'logout',
    },
]

index_controller = Controller('index', fk_url_map)
app.load_controller(index_controller)


# @app.route('/index', methods=['GET'])
# def index():
#     return "<h1>路由测试</h1>"

# @app.route('/test/js')
# def test_js():
#     return '<script src="/static/test.js"></script>'




app.run(port=8888)