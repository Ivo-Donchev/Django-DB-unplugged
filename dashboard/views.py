from django.shortcuts import render
from django.views import View

from rest_framework.generics import ListAPIView
from rest_framework import serializers

from .models import (
    Club,
    Party,
    Invoice,
    InvoiceRow,
    VisitorToParty,
)


class ClubListApi(ListAPIView):
    queryset = Club.objects.collect()[:10]

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Club
            fields = (
                'name',
                'total_incomes',
                'parties_count',
                'average_income_per_party',
                'first_party_name',
                'first_party_income',
                'last_party_name',
                'last_party_income',
            )

    def get_serializer_class(self):
        return ClubListApi.Serializer


class InvoiceRowListApi(ListAPIView):
    queryset = InvoiceRow.objects.collect()[:50]

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = InvoiceRow
            fields = (
                'invoice_id',
                'description',
                'tax_rate',
                'quantity',
                'unit_price',
                'amount'
            )

    def get_serializer_class(self):
        return InvoiceRowListApi.Serializer


class InvoiceListApi(ListAPIView):
    queryset = Invoice.objects.collect()[:30]

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Invoice
            fields = (
                'details',
                'default_tax_rate',
                'total_amount'
            )

    def get_serializer_class(self):
        return InvoiceListApi.Serializer


class VisitorToPartyListApi(ListAPIView):
    queryset = VisitorToParty.objects.collect()[:30]

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = VisitorToParty
            fields = (
                'invoice_amount',
            )

    def get_serializer_class(self):
        return VisitorToPartyListApi.Serializer


class PartyListApi(ListAPIView):
    queryset = Party.objects.collect()[:30]

    class Serializer(serializers.ModelSerializer):
        class Meta:
            model = Party
            fields = (
                'name',
                'total_party_income',
                'invoices_count'
            )

    def get_serializer_class(self):
        return PartyListApi.Serializer
