from django.conf.urls import url
from .views import (
    ClubListApi,
    PartyListApi,
    InvoiceListApi,
    InvoiceRowListApi,
    VisitorToPartyListApi,
)

urlpatters = [
    url(
        regex=r'^list/club$',
        view=ClubListApi.as_view(),
        name='club-list'
    ),
    url(
        regex=r'^list/invoice$',
        view=InvoiceListApi.as_view(),
        name='invoice-list'
    ),
    url(
        regex=r'^list/party$',
        view=PartyListApi.as_view(),
        name='party-list'
    ),
    url(
        regex=r'^list/invoice-row$',
        view=InvoiceRowListApi.as_view(),
        name='invoice-row-list'
    ),
    url(
        regex=r'^list/visitor-to-party$',
        view=VisitorToPartyListApi.as_view(),
        name='visitor-to-party-list'
    ),
]
