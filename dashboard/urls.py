from django.conf.urls import url
from .views import (
    DashboardListView,
    DashboardListApi
)

urlpatters = [
    url(
        regex=r'^list/view$',
        view=DashboardListView.as_view(),
        name='list-view'
    ),
    url(
        regex=r'^list/api$',
        view=DashboardListApi.as_view(),
        name='list-api'
    ),
]
