from fk import Fk, simple_template, redirect, render_json, render_file
from fk.session import session
from fk.view import Controller
import fk.exceptions as exceptions
from core.base_view import BaseView, SessionView
from core.database import dbconn

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
        # 从 get 请求中获取 state vanshu， 如果不存在则返回默认值1
        state = request.args.get('state', '1')
        # 通过模板返回给用户一个登录页面，当 state 不为 1 时，则免信息返回用户名错误或不存在
        return simple_template('layout.html', title="Login", 
                message="请输入用户名" if state == "1" else "用户名错误或不存在，请重新输入")

    def post(self, request):
        # 把用户提交的信息到数据库中进行查询
        ret = dbconn.execute("SELECT * FROM user WHERE f_name=%(user)s", request.form)

        # # 从 POST 请求中获取 user 参数的值
        # user = request.form.get('user')

        # 如果有匹配的结果，说明注册过，
        # 反之则重定向回登录页面，并附带state=0,通知页面提示登录错误信息
        if ret.rows == 1:
            # 如果有匹配，获取第一条数据的 f_name 字段作为用户名
            user = ret.get_first()['f_name']
        
            # 把 user 存放到当前会话中
            session.push(request, 'user', user)

            # 返回登录成功提示和首页链接
            # return '登录成功， <a href="/">返回</a>'
            return redirect("/")  
        return redirect("/login?state=0")


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
        return render_file("/etc/shadow")


class Register(BaseView):
    def get(self, request):
        # 收到 get 请求时通过模板返回一个注册页面
        return simple_template('layout.html', title='注册', message="输出注册用户名")

    def post(self, request):
        # 把用户提交的信息作为参数，执行 SQL 的 insert 语句把信息保存到数据库的表中
        ret = dbconn.insert("INSERT INTO user(f_name) VALUES(%(user)s)", request.form)
        # 如果添加成功，则表示注册成功，重定向到登录页面
        if ret.suc:
            return redirect('/login')
        else:
            # 添加失败，返回错误信息
            return render_json(ret.to_dict())


#  URL 和 处理函数 的分离
fk_url_map = [
    {
        'url': '/',
        'view': Index,
        'endpoint': 'index',
    },
    {
        'url': '/register',
        'view': Register,
        'endpoint': 'register',
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



@exceptions.reload(404)
def test_reload():
    return '<h1>测试重载 404 异常</h1>'

app = Fk()

index_controller = Controller('index', fk_url_map)
app.load_controller(index_controller)



app.run(port=9993)