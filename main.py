from fk import Fk, simple_template, redirect, render_json, render_file
from fk.session import session
from fk.view import Controller

from core.base_view import BaseView, SessionView


# 首页视图
class Index(SessionView):
    def get(self, request):
        # 获取当前会话中的 user 值
        user = session.get(request, 'user')
        print('Index get user >> ', user)
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
        # return '登录成功， <a href="/">返回</a>'
        return redirect("/")


# 登出视图
class Logout(SessionView):
    def get(self, request):
        # 从当前会话中删除 user
        session.pop(request, 'user')
        # 返回登出成功提示和首页链接
        # return '登出成功， <a href="/">返回</a>'
        return redirect("/")


class API(BaseView):
    def get(self, request):
        data = {
            "name": "001",
            "age": 11,
            "address": "Unknown"
        }
        return render_json(data)


class Download(BaseView):
    def get(self, request):
        return render_file("main.py")


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
    {
        'url': '/api',
        'view': API,
        'endpoint': 'api',
    },
    {
        'url': '/download',
        'view': Download,
        'endpoint': 'download',
    },
]


app = Fk()

index_controller = Controller('index', fk_url_map)
app.load_controller(index_controller)



app.run(port=9993)