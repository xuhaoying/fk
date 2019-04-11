# git@github.com:xuhaoying/fk.git
'''
创建目录结构
'''

import os

# 当前路径
root_path = os.getcwd()

# 目录列表
directory_list = [
    'dbconnector',  # 数据库连接
    'exceptions',  # 异常处理
    'helper',   # 辅助
    'route',   # 路由
    'session',   # 会话
    'template_engine',  # 模板引擎
    'view',  # 视图
    'wsgi_adapter',  # WSGI入口
]

# 子文件
children = {'name': '__init__.py', 'children': None, 'type':'file'}

# 目录结构
# dir_map = [
#     {
#     'name': 'fk',  # 本文件夹名称
#     'children': [{
#         'name':directory,
#         'type':'dir',
#         'children':[children]
#     } for directory in directory_list] + [children],
#     'type':'dir'
#     }
# ]

dir_map = [{
        'name':directory,
        'type':'dir',
        'children':[children]
    } for directory in directory_list] + [children]


# 创建文件夹及文件
def create(path, kind):
    if kind == 'dir':
        os.mkdir(path)
    else:
        open(path, 'w').close()

# 递归创建目录
def gen_project(parent_path, map_obj):
    for line in map_obj:
        path = os.path.join(parent_path, line['name'])
        create(path, line['type'])
        if line['children']:
            gen_project(path, line['children'])

def main():
    gen_project(root_path, dir_map)

if __name__ == '__main__':
    main()

