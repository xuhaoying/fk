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
        
    
