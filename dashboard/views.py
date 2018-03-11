from django.shortcuts import render
from django.views import View

from rest_framework.generics import ListAPIView
from rest_framework import serializers

from .models import Club


class DashboardListView(View):
    pass

class DashboardListApi(ListAPIView):
    queryset = Club.objects.all()

    class Serializer(serializers.Serializer):
        pass

    def get_serializer_class(self):
        return DashboardListApi.Serializer
