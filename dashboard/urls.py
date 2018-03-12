from django.conf.urls import url
from .views import (
    DashboardListApi
)

urlpatters = [
    url(
        regex=r'^list/api$',
        view=DashboardListApi.as_view(),
        name='list-api'
    ),
]
