from fk import Fk

app = Fk()

@app.route('/index', methods=['GET'])
def index():
    return "<h1>路由测试</h1>"

@app.route('/test/js')
def test_js():
    return '<script src="/static/test.js"></script>'

app.run(port=9999)