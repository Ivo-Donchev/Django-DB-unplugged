from django.conf.urls import url, include
from django.contrib import admin
import debug_toolbar

from dashboard.urls import urlpatters as dashboard_patterns

urlpatterns = [
    url(r'^__debug__/', include(debug_toolbar.urls)),
    url(r'^admin/', admin.site.urls),
    url(
        regex=r'^dashboard/',
        view = include(
            arg=dashboard_patterns,
            namespace='dashboard'
        ),
    )
]
