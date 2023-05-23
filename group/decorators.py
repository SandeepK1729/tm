from functools import wraps
from django.shortcuts import redirect

from .models        import Group

def group_member_login_required(func, REDIRECT_URL = 'home'):
    @wraps(func)
    def wrap(request, id, *args, **kwargs):
        group = Group.objects.get(id = id)

        if group is not None and request.user in group.get_members:
            return func(request, group, *args, **kwargs)

        return redirect(REDIRECT_URL)
    return wrap
    

