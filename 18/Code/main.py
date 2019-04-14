from sylfk import SYLFk, simple_template, redirect, render_json,render_file
from sylfk.session import session
from sylfk.view import Controller
from sylfk import exceptions

from core.base_view import BaseView, SessionView
from core.database import dbconn

class Index(SessionView):
    def get(self, request):
        user = session.get(request, 'user')
        print('Index get user >> ', user)
        return simple_template("index.html", user=user, message="实验楼，你好")


class Login(BaseView):
    def get(self, request):
        return simple_template("login.html")

    def post(self, request):
        user = request.form['user']
        session.push(request, 'user', user)
        return redirect('/')


class Logout(SessionView):
    def get(self, request):
        session.pop(request, 'user')
        return redirect('/')

class API(BaseView):
    def get(self, request):
        data = {
            'name': 'shiyanlou_001',
            'company': '实验楼',
            'department': '课程部'
        }

        return render_json(data)

class Download(BaseView):
    def get(self, request):
        return render_file("/etc/shadow")

class Register(BaseView):
    def get(self, request):
        return simple_template("layout.html", title="注册", message="输入注册用户名")

    def post(self, request):
        ret = dbconn.insert('INSERT INTO user(f_name) VALUES(%(user)s)', request.form)

        if ret.suc:
            return redirect("/login")
        else:
            return render_json(ret.to_dict())

class Login(BaseView):
    def get(self, request):
        state = request.args.get('state', "1")

        return simple_template("layout.html", title="登录", message="输入登陆用户名" if state == "1" else "用户名错误或不存在，重新输入")

    def post(self, request):
        ret = dbconn.execute('''SELECT * FROM user WHERE f_name = %(user)s''', request.form)

        if ret.rows == 1:
            user = ret.get_first()['f_name']

            session.push(request, 'user', user)

            return redirect("/")
        return redirect("/login?state=0")

@exceptions.reload(404)
def test_reload():
    return '<h1>测试重载 404 异常</h1>'

syl_url_map = [
    {
        'url': '/',
        'view': Index,
        'endpoint': 'index'
    },
    {
        'url': '/register',
        'view': Register,
        'endpoint': 'register'
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
    },
    {
        'url': '/api',
        'view': API,
        'endpoint': 'api'
    },
    {
        'url': '/download',
        'view': Download,
        'endpoint': 'download'
    }
]

app = SYLFk()

index_controller = Controller('index', syl_url_map)
app.load_controller(index_controller)

app.run()

