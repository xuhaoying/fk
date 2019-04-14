from fk.dbconnector import BaseDB

db_user = 'root'  # 连接用户名
db_password = '123456' # 连接密码
db_database = 'test'  # 数据库库名

# 捕获异常，首次连接数据库不存在，抛出数据库不存在的异常
# 捕获后到 except 语句块中进行数据库的初始化
try:
    # 获取数据库连接对象，如果数据库不存在，抛出异常
    dbconn = BaseDB(db_user, db_password, db_database)
except Exception as e:
    # 捕获异常的代码
    code, _ = e.args

    # 如果异常代码为 1049 也就是数据库不存在异常，在开始创建，
    # 反之为未知错误，输出信息呢并退出程序
    if code == 1049:
        # 创建数据库表语句
        cretae_table = '''
        CREATE TABLE user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            f_name VARCHAR(50) UNIQUE
        ) CHARSET=UTF8
        '''
        # 获取一个没有指定数据库的连接对象
        dbconn = BaseDB(db_user, db_password)
        # 创建数据库，返回一个 DBResult 对象
        ret = dbconn.create_db(db_database)
        
        # 如果创建成功，切换到该数据库中，然后开始创建数据表
        if ret.suc:
            ret = dbconn.choose_db(db_database)
            # 如果切换成功，开始创建数据表
            if ret.suc:
                ret = dbconn.execute(cretae_table)
        # 如果以上步骤有任何一步出错，删除数据库回退到创建数据库之前的状态
        if not ret.suc:
            dbconn.drop_db(db_database)
            print(ret.error.args)
            exit()
    else:
        # 输出错误信息并推出
        print(e)
        exit()