from django.conf.urls import url
from .views import DashboardListView

urlpatters = [
    url(
        regex=r'^list/$',
        view=DashboardListView.as_view(),
        name='list'
    ),
]
