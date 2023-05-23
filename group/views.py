from django.shortcuts               import render, HttpResponse
from django.contrib.auth.decorators import login_required

from .models                        import Group
from .decorators                    import group_member_login_required

@login_required
def groups_view(request):
    return render(request, "pages/groups.html")

@login_required
@group_member_login_required
def group_view(request, group):
    return render(request, "pages/group.html", {
        'group' : group,
    })