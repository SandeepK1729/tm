from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin', admin.site.urls),
    path('', include("core.urls")),
    path('', include("group.urls")),
]


from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(
                settings.MEDIA_URL,
                document_root = settings.MEDIA_ROOT
            )

urlpatterns += static(
                settings.STATIC_URL,
                document_root = settings.STATIC_ROOT
            )

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')), # include debug toolbar urls
    ]