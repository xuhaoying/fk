# 视图基类
class View(object):
    # 支持的请求方法
    methods = None

    # 请求处理函数映射
    methods_meta = None

    # 视图处理函数调度入口
    def dispath_request(self, request, *args, **option):
        raise NotImplementedError

    # 生成视图处理函数， 参数 name 就是节点名
    @classmethod
    def get_func(cls, name):
        # 定义处理函数
        def func(*args, **kwargs):
            # 在处理函数内部实例化视图对象
            obj = func.view_class()
            # 通过视图对象调用处理函数调度入口，返回视图处理结果
            return obj.dispath_request(*args, **kwargs)

        # 为处理函数绑定属性
        func.view_class = cls
        func.__name__ = name
        func.__doc__ = cls.__doc__
        func.__module__ = cls.__module__
        func.methods = cls.methods

        # 返回这个处理函数
        return func
    

# 控制器类
class Controller(object):
    def __init__(self, name, url_map):
        # 控制器名字， 生成节点时用到， 为了区分不同控制器下同名的视图对象
        self.name = name  
        # 存放映射关系， 一个元素为 dict 的 list
        self.url_map = url_map 
    
    def __name__(self):
        # 返回控制器名字
        return self.name