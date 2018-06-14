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
    __tax = Case(
        When(tax_rate__gt=0.0, then=F('tax_rate')),
        default=F('invoice__default_tax_rate'),
        output_field=models.DecimalField(default=Decimal(0.0))
    )
    _amount_without_tax = ExpressionWrapper(
        expression=F('quantity') * F('unit_price'),
        output_field=models.DecimalField()
    )
    _amount = ExpressionWrapper(
        expression=_amount_without_tax * (1 + __tax),
        output_field=models.DecimalField(default=Decimal(0.0))
    )

    def collect(self):
        private_fields = {
            '_amount_without_tax': self.__class__._amount_without_tax,
            '_amount': self.__class__._amount
        }

        return self.annotate(**private_fields)


class InvoiceQuerySet(QuerySet):
    @classmethod
    def _first_row_description_qs(self):
        from .models import InvoiceRow

        queryset = InvoiceRow.objects \
            .filter(invoice__id=OuterRef('id')) \
            .values_list('description')[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.CharField()
        )

    @classmethod
    def _description(self):
        return Coalesce(
            'description',
            self._first_row_description_qs(),
            default='',
            output_field=models.CharField()
        )

    @classmethod
    def _total_amount(self):
        from .models import InvoiceRow

        queryset = InvoiceRow.objects \
            .filter(invoice__id=OuterRef('id')) \
            .values('invoice__id') \
            .values_list(Sum(InvoiceRowQuerySet._amount))[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.IntegerField()
        )

    def collect(self):
        private_fields = {
            '_description': self._description(),
            '_total_amount': self._total_amount()
        }

        return self.annotate(**private_fields)


class VisitorToPartyQuerySet(QuerySet):
    @classmethod
    def _invoice_amount(self):
        from .models import InvoiceRow

        queryset = InvoiceRow.objects \
            .filter(invoice__id=OuterRef('invoice__id')) \
            .values('invoice__id') \
            .values_list(Sum(InvoiceRowQuerySet._amount))[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.IntegerField()
        )

    def collect(self):
        private_fields = {
            '_invoice_amount': self._invoice_amount(),
        }

        return self.annotate(**private_fields)


class PartyQuerySet(QuerySet):
    @classmethod
    def _invoices_count(self):
        from .models import VisitorToParty

        queryset = VisitorToParty.objects \
            .filter(invoice__id__isnull=False, party__id=OuterRef('id')) \
            .values('party__id') \
            .values_list(Count('id'))[:1]

        return Coalesce(
            Subquery(
                queryset=queryset,
                output_field=models.IntegerField()
            ),
            Value(0)
        )

    @classmethod
    def _total_party_income(self):
        from .models import VisitorToParty

        queryset = VisitorToParty.objects \
            .filter(party__id=OuterRef('id')) \
            .values('party__id') \
            .values_list(Sum(VisitorToPartyQuerySet._invoice_amount()))[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.DecimalField()
        )

    def collect(self):
        private_fields = {
            '_invoices_count': self._invoices_count(),
            '_total_party_income': self._total_party_income()
        }

        return self.annotate(**private_fields)


class ClubQueryset(QuerySet):
    @classmethod
    def _first_party_name(self):
        from .models import Party

        queryset = Party.objects \
            .filter(club__id=OuterRef('id')) \
            .order_by('id') \
            .values_list('name')[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.CharField()
        )

    @classmethod
    def _first_party_income(self):
        from .models import Party

        queryset = Party.objects \
            .filter(club__id=OuterRef('id')) \
            .order_by('id') \
            .values('club__id') \
            .values_list(PartyQuerySet._total_party_income())[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.DecimalField()
        )

    @classmethod
    def _last_party_name(self):
        from .models import Party

        queryset = Party.objects.filter(club__id=OuterRef('id')).order_by('-id').values_list('name')[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.CharField()
        )

    @classmethod
    def _last_party_income(self):
        from .models import Party

        queryset = Party.objects \
            .filter(club__id=OuterRef('id')) \
            .order_by('-id') \
            .values('club__id') \
            .values_list(PartyQuerySet._total_party_income())[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.DecimalField()
        )

    @classmethod
    def _average_income_per_party(self):
        from .models import Party

        queryset = Party.objects \
            .filter(club__id=OuterRef('id')) \
            .values('club__id') \
            .values_list(Avg(PartyQuerySet._total_party_income()))[:1]

        return Subquery(
            queryset=queryset,
            output_field=models.DecimalField()
        )

    @classmethod
    def _parties_count(self):
        from .models import Party

        queryset = Party.objects \
            .filter(club__id=OuterRef('id')) \
            .values('club__id') \
            .values_list(Count('id'))

        return Coalesce(
            Subquery(
                queryset=queryset
            ),
            Value(0)
        )

    @classmethod
    def _total_incomes(self):
        from .models import Party

        queryset = Party.objects \
            .filter(club__id=OuterRef('id')) \
            .values('club__id') \
            .values_list(Sum(PartyQuerySet._total_party_income()))[:1]

        return Coalesce(
            Subquery(
                queryset=queryset
            ),
            Value(0)
        )

    def collect(self):
        private_fields = {
            '_first_party_name': self._first_party_name(),
            '_first_party_income': self._first_party_income(),
            '_last_party_name': self._last_party_name(),
            '_last_party_income': self._last_party_income(),
            '_average_income_per_party': self._average_income_per_party(),
            '_parties_count': self._parties_count(),
            '_total_incomes': self._total_incomes()
        }

        return self.annotate(**private_fields)
