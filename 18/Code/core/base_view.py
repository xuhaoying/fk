from sylfk.view import View
from sylfk.session import AuthSession, session
from sylfk import redirect

class BaseView(View):
    methods = ['GET, POST']

    def post(self, request, *args, **options):
        pass

    def get(self, request, *args, **options):
        pass

    def dispatch_request(self, request, *args, **options):
        methods_meta = {
            'GET': self.get,
            'POST': self.post,
        }

        if request.method in methods_meta:
            return methods_meta[request.method](request, *args, **options)
        else:
            return '<h1>Unknown or unsupported require method</h1>'

class AuthLogin(AuthSession):

    @staticmethod
    def auth_fail_callback(request, *args, **options):
        return redirect("/login")

    @staticmethod
    def auth_logic(request, *args, **options):
        if 'user' in session.map(request):
            return True
        return False


class SessionView(BaseView):

    @AuthLogin.auth_session
    def dispatch_request(self, request, *args, **options):
        return super(SessionView, self).dispatch_request(request, *args, **options)
