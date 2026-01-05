from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.utils.deprecation import MiddlewareMixin


class TokenAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        token_key = request.COOKIES.get("auth_token")
        if token_key:
            try:
                token = Token.objects.select_related("user").get(key=token_key)
                request.user = token.user
            except Token.DoesNotExist:
                request.user = AnonymousUser()
        return None
