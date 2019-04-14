import pymysql


# 数据库返回结果对象
class DBResult(object):
    suc = False  # 执行结果是否成功
    result = None  # 执行结果，通常是查询结果集， 一个 list 嵌套 dict 的结构
    error = None  # 异常信息
    rows = None  # 影响行数

    def index_of(self, index):
        """返回结果集合中指定位置的一条数据"""
        # 判断是否执行成功，index 是否为整型，index 是否在有效范围内
        if self.suc and isinstance(index, int) \
            and self.rows > index >= -self.rows:
            return self.result[index]
        return None

    def get_first(self):
        """返回结果集合中的第一条数据"""
        return self.index_of(0)
    
    def get_last(self):
        """返回结果集合中的最后一条数据"""
        return self.index_of(-1)

    @staticmethod
    def handler(func):
        """异常捕获装饰器"""
        def decorator(*args, **options):
            # 实例化
            ret = DBResult()

            # 捕获异常
            try:
                # 为 DBResult 对象的 rows 和 result 成员赋值
                ret.rows, ret.result = func(*args, **options)
                # 修改执行状态为 True 表示执行成功
                ret.suc = True
            except Exception as e:
                # 如果捕获到异常，将异常放进 DBResult 对象的 error 属性中
                ret.error = e
            
            return ret
    
        return decorator

    def to_dict(self):
        return {
            'suc': self.suc,
            'result': self.result,
            'error': self.error,
            'rows': self.rows,
        }
        

# 数据库模块
class BaseDB(object):
    def __init__(self, user, password, database='',
                host='127.0.0.1', port=3306, charset='utf8',
                cursor_class=pymysql.cursors.DictCursor):
        self.user = user  # 连接用户
        self.password = password  # 连接用户密码
        self.database = database  # 选择的数据库
        self.host = host  # 主机名，默认为127.0.0.1
        self.port = port  # 端口号， 默认为 3306
        self.charset = charset  # 数据库编码，默认为 utf8
        # 数据库游标类型，默认为 DictCursor,返回的每一行数据集都是个字典
        self.cursor_class = cursor_class  
        self.conn = self.connect()  # 数据库连接对象

    # 建立连接
    def connect(self):
        # 返回一个数据库连接对象
        return pymysql.connect(
            host=self.host, port=self.port, user=self.user, 
            password=self.password, db=self.database,
            charset=self.charset, cursorclass=self.cursor_class)

    # 断开连接
    def close(self):
       self.conn.close()

    # SQL 语句执行方法, 增，删，改，查
    @DBResult.handler
    def execute(self, sql, params=None):
        # 获取数据库连接对象上下文
        with self.conn as cursor:
            # 如果参数不为空并且是 Dict 类型时， 把 SQL 语句与参数一起传入 execute 中调用，反之直接调用 execute
            # 执行语句并获取影响条目数量
            rows = cursor.execute(sql, params) if params and isinstance(params, dict) else cursor.execute(sql)

            # 获取执行结果
            result = cursor.fetchall()

        # 返回影响条目数量和执行结果
        return rows, result

    # 插入数据并获取最近插入的数据标识，也就是主键索引 ID 字段
    def insert(self, sql, params=None):
        # 获取 SQL 语句执行之后的 DBResult 对象
        ret = self.execute(sql, params)
        # 为 DBResult 对象的 result 属性重新赋值为插入数据的 ID
        ret.result = self.conn.insert_id()
        # 返回 DBResult 对象 
        return ret

    # 存储过程调用
    @DBResult.handler
    def process(self, func, params=None):
        # 获取数据库连接对象上下文
        with self.conn as cursor:
            # 如果参数不为空并且是 Dict 类型时， 把 存储过程名 与参数一起传入 callproc 中调用，反之直接调用 callproc
            # 执行语句并获取影响条目数量
            rows = cursor.callproc(func, params) if params and isinstance(params, dict) else cursor.callproc(func)
            # 获取执行结果
            result = cursor.fetchall()
        # 返回影响条目数量和执行结果
        return rows, result

    # 创建数据库
    def create_db(self, db_name, db_charset='utf8'):
       return self.execute('CREATE DATABASE {} DEFAULT CHARACTER SET {}'.format(db_name, db_charset))
    
    # 删除数据库
    def drop_db(self, db_name):
        return self.execute('DROP DATABASE {}'.format(db_name))

    # 选择数据库
    @DBResult.handler
    def choose_db(self, db_name):
        # 调用 PyMysql 的 select_db 方法选择数据库
        self.conn.select_db(db_name)
        # 正确执行的话没有影响条数和执行结果，返回空值
        return None, None



