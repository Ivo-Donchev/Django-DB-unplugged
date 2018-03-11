from django.shortcuts import render
from django.views import View

from rest_framework.generics import ListAPIView
from rest_framework import serializers

from .models import Club


class DashboardListView(View):
    pass

class DashboardListApi(ListAPIView):
    queryset = Club.objects.all()[:10]

    class Serializer(serializers.Serializer):
        name = serializers.CharField()
        parties_count = serializers.IntegerField()

        average_income_per_party = serializers.DecimalField(
            max_digits=10,
            decimal_places=2
        )

        first_party_name = serializers.CharField(source='first_party.name')
        first_party_income = serializers.DecimalField(
            source='first_party.total_party_income',
            max_digits=10,
            decimal_places=2
        )

        last_party_name = serializers.CharField(source='first_party.name')
        last_party_income = serializers.DecimalField(
            source='last_party.total_party_income',
            max_digits=10,
            decimal_places=2
        )

    def get_serializer_class(self):
        return DashboardListApi.Serializer
