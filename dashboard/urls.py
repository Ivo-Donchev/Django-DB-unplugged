from django.conf.urls import url
from .views import (
    ClubListApi,
    InvoiceRowListApi,
)

urlpatters = [
    url(
        regex=r'^list/club$',
        view=ClubListApi.as_view(),
        name='club-list'
    ),
    url(
        regex=r'^list/invoice-row$',
        view=InvoiceRowListApi.as_view(),
        name='invoice-row-list'
    ),
]
