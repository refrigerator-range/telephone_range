from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from telephone_range import settings

urlpatterns = [
    path('Oort/', include('Oort.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
