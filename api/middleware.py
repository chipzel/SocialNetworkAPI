from django.utils.timezone import now

from .models import User


def set_last_request_middleware(get_response):

    def middleware(request):
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.id).update(last_request_time=now())
        return get_response(request)

    return middleware
