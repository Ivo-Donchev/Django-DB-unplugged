from django.contrib import admin
from .models import (
    Club,
    Invoice,
    InvoiceRow,
    Party,
    Visitor,
    VisitorToParty
)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'default_tax_rate')


@admin.register(InvoiceRow)
class InvoiceRowAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'description', 'tax_rate', 'quantity', 'unit_price')


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'club')


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'age')


@admin.register(VisitorToParty)
class VisitorToPartyAdmin(admin.ModelAdmin):
    list_display = ('id', 'visitor', 'party')
