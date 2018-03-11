from decimal import Decimal

from django.db import models
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet
from django.db.models import (
    Case,
    Count,
    When,
    Q,
    Sum,
    Subquery,
    OuterRef,
    F,
    ExpressionWrapper,
    Value,
)


class InvoiceRowQuerySet(QuerySet):
    def collect(self):
        __tax = Coalesce(
            'tax_rate',
            'invoice__default_tax_rate',
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

        private_fields = {
            '_amount_without_tax': _amount_without_tax,
            '_amount': _amount
        }

        return self.annotate(**private_fields)


class InvoiceQuerySet(QuerySet):
    def collect(self):
        from .models import InvoiceRow
        __rows_grouped_by_invoice = InvoiceRow.objects.collect()\
                                                      .annotate(group_by_clause=Count('invoice__id'))\
                                                      .filter(invoice__id=OuterRef('id'))

        __first_row_description_qs = Subquery(
            __rows_grouped_by_invoice.values_list('description')[:1]
        )

        _description = Coalesce(
            'description',
            __first_row_description_qs,
            default=''
        )
        _total_amount = Subquery(
            __rows_grouped_by_invoice.values_list(Sum('total'))[:1]
        )

        private_fields = {
            '_description': _description,
            '_total_amount': _total_amount
        }

        return self.annotate(**private_fields)


class VisitorToPartyQuerySet(QuerySet):
    def collect(self):
        from .models import InvoiceRow
        __rows_grouped_by_invoice = InvoiceRow.objects.collect()\
                                                      .filter(invoice__id=OuterRef('invoice__id'))\
                                                      .annotate(group_by_clause=Count('invoice__id'))

        _invoice_amount = Subquery(
            __rows_grouped_by_invoice.values_list('_amount')[:1]
        )

        private_fields = {
            '_invoice_amount': _invoice_amount,
        }

        return self.annotate(**private_fields)


class PartyQuerySet(QuerySet):
    def collect(self):
        from .models import VisitorToParty
        __visitortoparty_set_grouped = VisitorToParty.objects.collect()\
                                                             .filter(invoice__isnull=False,
                                                                     party__id=OuterRef('id'))\
                                                             .annotate(counts=Count('party__id'))

        _invoices_count = Subquery(
            __visitortoparty_set_grouped.values_list('counts')[:1],
            output_field=models.IntegerField()
        )
        _total_party_income = Subquery(
            __visitortoparty_set_grouped.values_list(Sum('_invoice_amount'))[:1],
            output_field=models.PositiveIntegerField()
        )

        private_fields = {
            '_invoices_count': _invoices_count,  # TODO: This is not correct
            '_total_party_income': _total_party_income  # TODO: Test it
        }

        return self.annotate(**private_fields)

class ClubQueryset(QuerySet):
    def collect(self):
        from .models import Party
        __parties = Party.objects.annotate(group_by_clause=Count('club__id'))\
                                 .filter(club__id=OuterRef('id'))
        _first_party_name = Subquery(
            Party.objects.filter(club__id=OuterRef('id'))\
                         .order_by('id')\
                         .values_list('name')[:1],
            output_field=models.CharField()
        )
        _first_party_income = Subquery(
            Party.objects.filter(club__id=OuterRef('id'))\
                        .collect()\
                        .order_by('id')\
                        .values_list('_total_party_income')[:1]
        )

        _last_party_name = Subquery(
            Party.objects.filter(club__id=OuterRef('id'))\
                         .order_by('-id')\
                         .values_list('name')[:1],
            output_field=models.CharField()
        )
        _last_party_income = Subquery(
            Party.objects.filter(club__id=OuterRef('id'))\
                         .collect()\
                         .order_by('-id')\
                         .values_list('_total_party_income')[:1]
        )

        _total_incomes = Subquery(
            __parties.collect().values_list(Sum('_total_party_income'))[:1],
            output_field=models.DecimalField()
        )
        _parties_count = Subquery(
            __parties.values_list('group_by_clause')[:1],
            output_field=models.DecimalField()
        )
        _average_income_per_party = ExpressionWrapper(
            _total_incomes / _parties_count,
            output_field = models.DecimalField()
        )

        private_fields = {
            '_parties_count': _parties_count,
            '_total_incomes': _total_incomes,
            '_average_income_per_party': _average_income_per_party,
            '_first_party_name': _first_party_name,
            '_first_party_income': _first_party_income,
            '_last_party_name': _last_party_name,
            '_last_party_income': _last_party_income,
        }

        return  self.annotate(**private_fields)
