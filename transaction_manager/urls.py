from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin', admin.site.urls),
    path('', include("core.urls")),
    path('', include("group.urls")),
    
]

from django.conf import settings
from django.conf.urls.static import serve

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}), 
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
]