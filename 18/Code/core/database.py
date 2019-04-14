from sylfk.dbconnector import BaseDB

db_user = 'root'
db_passowrd = ''
db_database = "shiyanlou"

try:
    dbconn = BaseDB(db_user, db_passowrd, db_database)
except Exception as e:
    code, _ = e.args

    if code == 1049:
        create_table = \
'''CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    f_name VARCHAR(50) UNIQUE
) CHARSET=utf8'''

        dbconn = BaseDB(db_user, db_passowrd)

        ret = dbconn.create_db(db_database)

        if ret.suc:
            ret = dbconn.choose_db(db_database)

            if ret.suc:
                ret = dbconn.execute(create_table)

        if not ret.suc:
            dbconn.drop_db(db_database)

            print(ret.error.args)
            exit()
    else:
        print(e)
        exit()
