# from django.shortcuts import render
# from django.utils.deprecation import MiddlewareMixin

# class Custom404Middleware(MiddlewareMixin):
#     def process_response(self, request, response):
#         if response.status_code == 404:
#             return render(request, '404.html', status=404)
#         return response




# class Custom403Middleware(MiddlewareMixin):
#     def process_response(self, request, response):
#         if response.status_code == 403:
#             return render(request, '403.html', status=403)
#         return response


# class Custom500Middleware(MiddlewareMixin):
#     def process_response(self, request, response):
#         if response.status_code == 500:
#             return render(request, '500.html', status=500)
#         return response


