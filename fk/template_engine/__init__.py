import os
import re


# 定义模版标记，采用与主流模版引擎 Jinja2 相同的标记
pattern = r'{{(.*?)}}'

def parse_args(obj):
    """
    解析模板

    用正则匹配出所有的模版标记的解析函数，
    如果有找到标记则返回，反之返回一个空的 tuple
    """
    # 获取匹配对象
    comp = re.compile(pattern)
    # 查找所有匹配的结果
    ret = comp.findall(obj)
    # 如果匹配结果不为空，返回它，为空则返回一个空的 tuple
    return ret if ret else ()

def replace_template(app, path, **options):
    """
    读取模版文件内容，再找出所有的标记进行内容替换
    """
    # 默认返回内容，当找不到本地模板文件时返回
    content = '<h1>Not Found Template</h1>'

    # 获取模板文件本地路径
    path = os.path.join(app.template_folder, path)

    # 如果路径存在， 则开始解析置换
    if os.path.exists(path):
        # 获取模板文件内容
        with open(path, 'rb') as f:
            content = f.read().decode()
        
        # 解析出所有的标记
        args = parse_args(content)

        # 如果置换内容不为空，开始置换
        if options:
            # 遍历所有置换数据，开始置换
            for arg in args:
                # 从标记中获取键
                key = arg.strip()
                # 如果键存在于置换数据中，则进行数据替换，反之替换为空
                content = content.replace("{{%s}}" % arg, str(options.get(key, '')))
    
    # 返回模板内容
    return content