from django.http import HttpResponseForbidden
from functools import wraps

def organizer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_organizer:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper