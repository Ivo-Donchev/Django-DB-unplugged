from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.db.models import (
    When,
    Case,
    Count,
    Avg,
    Sum,
    Subquery,
    OuterRef,
    F,
    ExpressionWrapper,
    Value,
)


class InvoiceRowQuerySet(QuerySet):
    def collect(self):
        private_fields = {
        }

        return self.annotate(**private_fields)


class InvoiceQuerySet(QuerySet):
    def collect(self):
        private_fields = {
        }

        return self.annotate(**private_fields)


class VisitorToPartyQuerySet(QuerySet):
    def collect(self):
        private_fields = {
        }

        return self.annotate(**private_fields)



class PartyQuerySet(QuerySet):
    def collect(self):
        private_fields = {
        }

        return self.annotate(**private_fields)


class ClubQueryset(QuerySet):
    def collect(self):
        private_fields = {
        }


        return self.annotate(**private_fields)
