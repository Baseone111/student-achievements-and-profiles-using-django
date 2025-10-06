from django.http import HttpResponseForbidden

def admin_required(view_func):
    """Only allow staff/admin users"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseForbidden("You are not allowed to access this page")
        return view_func(request, *args, **kwargs)
    return wrapper
