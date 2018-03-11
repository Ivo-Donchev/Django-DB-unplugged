from django.shortcuts import render
from django.views import View

from rest_framework.generics import ListAPIView
from rest_framework import serializers

from .models import Club


class DashboardListView(View):
    pass

class DashboardListApi(ListAPIView):
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
        return DashboardListApi.Serializer
