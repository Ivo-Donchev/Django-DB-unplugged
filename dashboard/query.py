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

    def collect(self):
        private_fields = {
            '_amount_without_tax': self.__class__._amount_without_tax,
            '_amount': self.__class__._amount
        }

        return self.annotate(**private_fields)


class InvoiceQuerySet(QuerySet):

    __first_row_description_qs = lambda cls: Subquery(
        cls.objects.filter(invoice__id=OuterRef('id'))
                    .values_list('description')[:1],
        output_field=models.CharField()
    )
    _description = lambda cls: Coalesce(
        'description',
        InvoiceQuerySet.__first_row_description_qs(cls),
        default='',
        output_field=models.CharField()
    )

    _row_amount = InvoiceRowQuerySet._amount
    _total_amount = lambda cls : Subquery(
        cls.objects.values('invoice__id')
                   .annotate(asd=Sum(InvoiceQuerySet._row_amount))
                   .filter(invoice__id=OuterRef('id'))
                   .values_list('asd')[:1],
        output_field=models.IntegerField()
    )

    def collect(self):
        from .models import InvoiceRow

        private_fields = {
            '_description': self.__class__._description(InvoiceRow),
            '_total_amount': self.__class__._total_amount(InvoiceRow)
        }

        return self.annotate(**private_fields)


class VisitorToPartyQuerySet(QuerySet):
    _row_amount = InvoiceRowQuerySet._amount
    _invoice_amount = lambda cls: Subquery(
        cls.objects.values('invoice__id')
                   .annotate(asd=Sum(VisitorToPartyQuerySet._row_amount))
                   .filter(invoice__id=OuterRef('invoice__id'))
                   .values_list('asd')[:1],
        output_field=models.IntegerField()
    )

    def collect(self):
        from .models import InvoiceRow

        private_fields = {
            '_invoice_amount': self.__class__._invoice_amount(InvoiceRow),
        }

        return self.annotate(**private_fields)


class PartyQuerySet(QuerySet):
    _invoices_count = lambda cls: Subquery(
        cls.objects.filter(invoice__id__isnull=False,
                           party__id=OuterRef('id'))
                   .values('party__id')
                   .annotate(asd=Count('id'))
                   .values_list('asd')[:1],
        output_field=models.IntegerField()
    )
    _invoice_amount = VisitorToPartyQuerySet._invoice_amount

    _total_party_income = lambda cls, invoice_row_cls: Subquery(
        cls.objects.filter(party__id=OuterRef('id'))
                    .values('party__id')
                    .annotate(asd=Sum(PartyQuerySet._invoice_amount(invoice_row_cls)))
                    .values_list('asd')[:1],
        output_field=models.DecimalField()
    )

    def collect(self):
        from .models import VisitorToParty, InvoiceRow

        private_fields = {
            '_invoices_count': self.__class__._invoices_count(VisitorToParty),
            '_total_party_income': self.__class__._total_party_income(VisitorToParty, InvoiceRow)
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
