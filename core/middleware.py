
class AjaxRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.is_ajax = lambda: request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        response = self.get_response(request)
        return response