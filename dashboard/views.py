from django.shortcuts import render
from django.views import View

from rest_framework.generics import ListAPIView
from rest_framework import serializers

from .models import (
    Club,
    Invoice,
    InvoiceRow,
    VisitorToParty,
)


class ClubListApi(ListAPIView):
    queryset = Club.objects\
        .collect()\
        .values(
            'name',
            '_parties_count',
            '_average_income_per_party',
            '_first_party_name',
            '_first_party_income',
            '_last_party_name',
            '_last_party_income'
        )[:10]

    class Serializer(serializers.Serializer):
        name = serializers.CharField()
        parties_count = serializers.IntegerField(
            source='_parties_count'
        )

        average_income_per_party = serializers.DecimalField(
            source='_average_income_per_party',
            max_digits=10,
            decimal_places=2
        )

        first_party_name = serializers.CharField(
            source='_first_party_name'
        )
        first_party_income = serializers.DecimalField(
            source='_first_party_income',
            max_digits=10,
            decimal_places=2
        )

        last_party_name = serializers.CharField(
            source='_last_party_name'
        )
        last_party_income = serializers.DecimalField(
            source='_last_party_income',
            max_digits=10,
            decimal_places=2
        )

    def get_serializer_class(self):
        return ClubListApi.Serializer


class InvoiceRowListApi(ListAPIView):
    queryset = InvoiceRow.objects.collect().values(
        'invoice__id',
        'description',
        'tax_rate',
        'quantity',
        'unit_price',
        '_amount'
    )[:50]

    class Serializer(serializers.Serializer):
        invoice = serializers.IntegerField(source='invoice__id')
        description = serializers.CharField()

        tax_rate = serializers.DecimalField(
            max_digits=10,
            decimal_places=2
        )
        quantity = serializers.IntegerField()
        unit_price = serializers.DecimalField(
            max_digits=10,
            decimal_places=2
        )
        amount = serializers.DecimalField(
            source='_amount',
            max_digits=10,
            decimal_places=2
        )

    def get_serializer_class(self):
        return InvoiceRowListApi.Serializer


class InvoiceListApi(ListAPIView):
    queryset = Invoice.objects.collect()[:30]

    class Serializer(serializers.Serializer):
        details = serializers.CharField(source='_description')
        default_tax_rate = serializers.DecimalField(
            max_digits=10,
            decimal_places=2
        )
        total_amount = serializers.DecimalField(
            source='_total_amount',
            max_digits=10,
            decimal_places=2
        )

    def get_serializer_class(self):
        return InvoiceListApi.Serializer

class VisitorToPartyListApi(ListAPIView):
    queryset = VisitorToParty.objects.collect()[:30]

    class Serializer(serializers.Serializer):
        invoice_amount = serializers.DecimalField(
            source='_invoice_amount',
            max_digits=10,
            decimal_places=2
        )

    def get_serializer_class(self):
        return VisitorToPartyListApi.Serializer
