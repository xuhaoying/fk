import os
import json
from werkzeug.serving import run_simple
from werkzeug.wrappers import Response
from fk.wsgi_adapter import wsgi_app
import fk.exceptions as exceptions
from fk.helper import parse_static_key
from fk.route import Route
from fk.template_engine import replace_template
from fk.session import create_session_id, session


# 定义文件类型
TYPE_MAP = {
    'css':  'text/css',
    'js': 'text/js',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg'    
}


# 处理函数数据结构
class ExecFunc(object):
    def __init__(self, func, func_type, **options):
        self.func = func  # 处理函数
        self.func_type = func_type  # 函数类型
        self.options = options  # 附带的参数


# 框架
class Fk(object):
    # 类属性，模板文件本地存放目录
    template_folder = None
    
    # 实例化方法
    def __init__(self, static_folder='static', template_folder='templates', session_path='.session'):
        self.host = '127.0.0.1'  # 默认主机
        self.port = 23333  # 默认端口
        self.url_map = {}  # 存放 URL 与 Endpoint 的映射
        self.static_map = {}  # 存放 URL 与 静态资源 的映射
        self.function_map = {}  # 存放 Endpoint 与 请求处理函数 的映射
        # 静态资源本地存放路径，默认放在应用所在目录的 static 文件夹下
        self.static_folder = static_folder  
        # self.route = Route(self)  # 路由装饰器
        # 模板文件本地存放路径， 默认放在应用所在目录下的 templates 文件夹下
        self.template_folder = template_folder  
        # 为类的 template_folder 初始化，供上面的置换模板引擎调用
        Fk.template_folder = self.template_folder  
        # 会话记录默认存放在应用同目录下的 .session 文件夹中
        self.session_path = session_path

    # 路由
    @exceptions.capture
    def dispatch_request(self, request):
        # 去掉 URL 中域名部分， 即从 http://xxx.com/path/file?xx=xx 中提取 path/file
        url = '/' +'/'.join(request.url.split('/')[3:]).split('?')[0]

        # 通过 URL 寻找节点名
        if url.find(self.static_folder) == 1 and url.index(self.static_folder) == 1:
            # 如果 URL 以静态资源文件夹名开头， 则资源为静态资源， 节点定义为 static
            endpoint = 'static'
            url = url[1:]
        else:
            # 如果不以静态资源文件夹名为首， 则从 URL 与节点的映射表中获取节点
            endpoint = self.url_map.get(url, None)

        # 从请求中取出 cookie
        cookies = request.cookies

        # 如果 session_id 不在cookies中， 则通知客户端设置 cookie
        if 'session_id' not in cookies:
            headers = {
                # 定义 Set-Cookie 属性，通知客户端记录 Cookie
                # create_session_id 是生成一个无规律唯一字符串的方法
                'Set-Cookie': 'session_id=%s' % create_session_id(),
                # 定义响应报头的 Server 属性
                'Server': 'Fk 0.1'
            }
        else:
            headers = {
                # 定义响应报头，Server 参数的值表示运行的服务名，通常有 IIS， Apache，Tomcat，Nginx等，这里自定义为 Fk 0.1
                'Server': 'Fk 0.1'
            }


        # 如果节点为空， 抛出页面未找到异常
        if endpoint is None:
            raise exceptions.PageNotFoundError

        # 获取节点对应的执行函数
        exec_function = self.function_map[endpoint]

        # 判断执行函数类型
        if exec_function.func_type == 'route':
            # 路由处理
            # 判断请求方法是否支持
            if request.method in exec_function.options.get('methods'):
                # 判断路由的执行函数是否需要请求体进行内部处理
                argcount = exec_function.func.__code__.co_argcount

                if argcount > 0:
                    # 需要附带请求体进行结果处理
                    rep = exec_function.func(request)
                else:
                    # 不需要附带请求体进行结果处理
                    rep = exec_function.func()
            else:
                # 未知请求方法
                # 抛出请求方法不支持异常
                raise exceptions.InvalidRequestMethodError

        elif exec_function.func_type == 'view':
            # 视图处理逻辑
            rep = exec_function.func(request)
        
        elif exec_function.func_type == 'static':
            # 静态逻辑处理
            # 静态资源返回的是一个预先封装好的响应体， 所以直接返回
            return exec_function.func(url)
        else:
            # 未知类型处理
            # 抛出未知处理类型异常
            raise exceptions.UnknownFuncError

        # 定义 200 状态码表示响应成功
        status = 200
        # 定义响应体类型
        content_type = 'text/html'
        
        # 判断，如果返回值是 Response 类型，则直接返回
        if isinstance(rep, Response):
            return rep
        
        # 返回 WSGI 规定的响应体给 WSGI 模块
        return Response(rep,
                    content_type='{}; charset=UTF-8'.format(content_type),
                    headers=headers, status=status)

    # 启动入口
    def run(self, host=None, port=None, **options):
        # 如果有参数传入且值不为空，则赋值
        for key, value in options.items():
            if value is not None:
                self.__setattr__(key, value)

        # 如果 host 不为None， 则按传入的host设置主机
        if host:
            self.host = host

        # 如果 port 不为None， 则按传入的host设置端口
        if port:
            self.port = port

        # 映射静态资源处理函数，所有静态资源处理函数都是静态资源路由
        self.function_map['static'] = ExecFunc(
                func=self.dispatch_static, func_type='static')
        
        # 如果会话记录存放目录不存在，则创建它
        if not os.path.exists(self.session_path):
            os.mkdir(self.session_path)
        
        # 设置会话记录存放目录
        session.set_storage_path(self.session_path)
        
        # 加载本地缓存的 session 记录
        session.load_local_session()


        # 把框架本身和其他几个配置参数传给 werkzeug 里的 run_simple
        run_simple(hostname=self.host, port=self.port,
                application=self, **options)


    # 框架被 WSGI 调用入口的方法
    def __call__(self, environ, start_response):
        return wsgi_app(self, environ, start_response)

    # 添加视图规则
    def bind_view(self, url, view_class, endpoint):
        self.add_url_rule(url, func=view_class.get_func(endpoint), func_type='view')

    # 添加路由规则
    @exceptions.capture
    def add_url_rule(self, url, func, func_type, endpoint=None, **options):
        # 如果节点未命名， 使用处理函数的名字
        if endpoint is None:
            endpoint = func.__name__

        # URL 已存在， 抛出 URL 已存在异常
        if url in self.url_map:
            raise exceptions.URLExistsError 

        # 如果类型不是静态资源， 并且节点已经存在， 则抛出节点已存在异常
        if endpoint in self.function_map and func_type != 'static':
            raise exceptions.EndpointExistsError

        # 添加 URL 与 节点 映射
        self.url_map[url] = endpoint

        # 添加节点与请求处理函数映射
        self.function_map[endpoint] = ExecFunc(func, func_type, **options)
    
    # 静态资源调路由
    @exceptions.capture
    def dispatch_static(self, static_path):
        """
        静态资源 URL 的路由
        用来选匹配的 URL 并返回对应类型和文件内容封装成的响应体
        如果找不到则返回 404 状态页。
        """
        # 判断资源文件是否在静态资源规则中， 如果不存在，抛出页面未找到异常
        if os.path.exists(static_path):
            # 获取资源文件后缀
            key = parse_static_key(static_path)

            # 获取文件类型
            doc_type = TYPE_MAP.get(key, 'text/plain')

            # 获取文件内容
            with open(static_path, 'rb') as f:
                rep = f.read()

            # 封装并返回响应体
            return Response(rep, content_type=doc_type)
        else:
            # 抛出页面未找到异常
            raise exceptions.PageNotFoundError

    # 控制器加载
    def load_controller(self, controller):
        # 获取控制器名字
        name = controller.__name__()
        # 遍历控制器的 `url_map` 成员
        for rule in controller.url_map:
            # 绑定 URL 与 视图对象， 最后的节点名格式为 `控制器名` + "." + 定义的节点名
            self.bind_view(rule['url'], rule['view'], name+'.'+rule['endpoint'])


def simple_template(path, **options):
    """模板引擎接口"""
    return replace_template(Fk, path, **options)

def redirect(url, status_code=302):
    """URL 重定向方法"""
    # 定义一个响应体
    response = Response('', status=status_code)
    # 为响应体的报头中的 Location 参数与 URL 进行绑定， 通知客户端自动跳转
    response.headers['Location'] = url
    # 返回响应体
    return response


def render_json(data):
    """封装 json 数据响应包"""
    # 定义默认文件类型为纯文本
    content_type = "text/plain"

    # 如果是 Dict 或者 List 类型， 则转换为 json 格式数据
    if isinstance(data, dict) or isinstance(data, list):
        data = json.dumps(data)
        # 定义文件类型为 json 格式
        content_type = "application/json"
    
    # 返回封装完的响应体
    return Response(data, 
    content_type="%s; charset=UTF-8" % content_type,
    status=200)

@exceptions.capture
def render_file(file_path, file_name=None):
    """返回让客户端保存文件到本地的响应体"""
    # 怕段服务器是否有该文件，抛出文件不存在异常
    if os.path.exists(file_path):
        # 判断是否有读取权限，没有则抛出权限不足异常
        if not os.access(file_path, os.R_OK):
            raise exceptions.RequireReadPermissionError

        # 读取文件内容
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # 如果没有设置文件名，则以"/"分割路径，取最后一项为文件名
        if file_name is None:
            file_name = file_path.split('/')[-1]
        
        # 封装响应报头，指定为附件类型，并定义下载的文件名
        headers = {
            "Content-Disposition": "attachment; filename={}".format(file_name)
        }
        # 返回响应体
        return Response(content, headers=headers, status=200)
    
    # 如果不存在该文件，抛出文件不存在异常
    return exceptions.FileNotExistsError

