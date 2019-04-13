from sylfk import SYLFk, simple_template
from sylfk.session import session
from sylfk.view import Controller

from core.base_view import BaseView, SessionView


class Index(SessionView):
    def get(self, request):
        user = session.get(request, 'user')

        return simple_template("index.html", user=user, message="实验楼，你好")


class Login(BaseView):
    def get(self, request):
        return simple_template("login.html")

    def post(self, request):
        user = request.form['user']

        session.push(request, 'user', user)

        return '登录成功，<a href="/">返回</a>'


class Logout(SessionView):
    def get(self, request):
        session.pop(request, 'user')

        return '登出成功，<a href="/">返回</a>'


syl_url_map = [
    {
        'url': '/',
        'view': Index,
        'endpoint': 'index'
    },
    {
        'url': '/login',
        'view': Login,
        'endpoint': 'test'
    },
    {
        'url': '/logout',
        'view': Logout,
        'endpoint': 'logout'
    }
]

app = SYLFk()

index_controller = Controller('index', syl_url_map)
app.load_controller(index_controller)

app.run(port=10000)
