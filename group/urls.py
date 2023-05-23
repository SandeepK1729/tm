from django.urls        import path, include
from .                  import views

urlpatterns = [
    path('groups', views.groups_view, name = "groups"),
    path('group/<int:id>', views.group_view, name = "group"),

]
