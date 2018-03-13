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
    __first_row_description_qs = lambda *, InvoiceRow: Subquery(
        InvoiceRow.objects.filter(invoice__id=OuterRef('id'))
                          .values_list('description')[:1],
        output_field=models.CharField()
    )

    _description = lambda *, InvoiceRow: Coalesce(
        'description',
        InvoiceQuerySet.__first_row_description_qs(InvoiceRow=InvoiceRow),
        default='',
        output_field=models.CharField()
    )
    _total_amount = lambda *, InvoiceRow: Subquery(
        InvoiceRow.objects.values('invoice__id')
                          .annotate(asd=Sum(InvoiceRowQuerySet._amount))
                          .filter(invoice__id=OuterRef('id'))
                          .values_list('asd')[:1],
        output_field=models.IntegerField()
    )

    def collect(self):
        from .models import InvoiceRow

        private_fields = {
            '_description': self.__class__._description(InvoiceRow=InvoiceRow),
            '_total_amount': self.__class__._total_amount(InvoiceRow=InvoiceRow)
        }

        return self.annotate(**private_fields)


class VisitorToPartyQuerySet(QuerySet):
    _invoice_amount = lambda *, InvoiceRow: Subquery(
        InvoiceRow.objects.values('invoice__id')
                          .annotate(asd=Sum(InvoiceRowQuerySet._amount))
                          .filter(invoice__id=OuterRef('invoice__id'))
                          .values_list('asd')[:1],
        output_field=models.IntegerField()
    )

    def collect(self):
        from .models import InvoiceRow

        private_fields = {
            '_invoice_amount': self.__class__._invoice_amount(InvoiceRow=InvoiceRow),
        }

        return self.annotate(**private_fields)



class PartyQuerySet(QuerySet):
    _invoices_count = lambda *, VisitorToParty: Coalesce(
        Subquery(
            VisitorToParty.objects.filter(invoice__id__isnull=False, party__id=OuterRef('id'))
                                  .values('party__id')
                                  .annotate(asd=Count('id'))
                                  .values_list('asd')[:1],
            output_field=models.IntegerField()
        ),
        Value(0)
    )

    _total_party_income = lambda *, VisitorToParty, InvoiceRow: Subquery(
        VisitorToParty.objects.filter(party__id=OuterRef('id'))
                              .values('party__id')
                              .annotate(asd=Sum(VisitorToPartyQuerySet._invoice_amount(InvoiceRow=InvoiceRow)))
                              .values_list('asd')[:1],
        output_field=models.DecimalField()
    )

    def collect(self):
        from .models import VisitorToParty, InvoiceRow

        private_fields = {
            '_invoices_count': self.__class__._invoices_count(
                VisitorToParty=VisitorToParty
            ),
            '_total_party_income': self.__class__._total_party_income(
                VisitorToParty=VisitorToParty,
                InvoiceRow=InvoiceRow
            )
        }

        return self.annotate(**private_fields)


class ClubQueryset(QuerySet):
    _first_party_name = lambda *, Party: Subquery(
        Party.objects.filter(club__id=OuterRef('id'))
                     .order_by('id')
                     .values_list('name')[:1],
        output_field=models.CharField()
    )
    _first_party_income = lambda *, Party, VisitorToParty, InvoiceRow: Subquery(
        Party.objects.filter(club__id=OuterRef('id'))
                     .order_by('id')
                     .values('club__id')
                     .values_list(PartyQuerySet._total_party_income(
                         InvoiceRow=InvoiceRow,
                         VisitorToParty=VisitorToParty
                      ))[:1],
        output_field=models.DecimalField()
    )
    _last_party_name = lambda *, Party: Subquery(
        Party.objects.filter(club__id=OuterRef('id'))
                     .order_by('-id')
                     .values_list('name')[:1],
        output_field=models.CharField()
    )
    _last_party_income = lambda *, Party, VisitorToParty, InvoiceRow: Subquery(
        Party.objects.filter(club__id=OuterRef('id'))
                     .order_by('-id')
                     .values('club__id')
                     .values_list(PartyQuerySet._total_party_income(
                         InvoiceRow=InvoiceRow,
                         VisitorToParty=VisitorToParty
                      ))[:1],
        output_field=models.DecimalField()
    )

    _average_income_per_party = lambda *, Party, InvoiceRow, VisitorToParty: Subquery(
        Party.objects.filter(club__id=OuterRef('id'))
                     .values('club__id')
                     .annotate(asd=Avg(PartyQuerySet._total_party_income(
                         InvoiceRow=InvoiceRow,
                         VisitorToParty=VisitorToParty
                      )))
                     .values_list('asd')[:1],
        output_field=models.DecimalField()
    )
    _parties_count = lambda *, Party: Coalesce(
        Subquery(
            Party.objects.filter(club__id=OuterRef('id'))
                         .values('club__id')
                         .values_list(Count('id'))
        ),
        Value(0)
    )
    _total_incomes = lambda *, Party, InvoiceRow, VisitorToParty: Coalesce(
        Subquery(
            Party.objects.filter(club__id=OuterRef('id'))
                         .values('club__id')
                         .annotate(asd=Sum(PartyQuerySet._total_party_income(
                             InvoiceRow=InvoiceRow,
                             VisitorToParty=VisitorToParty
                          )))
                         .values_list('asd')[:1],
        ),
        Value(0)
    )

    def collect(self):
        from .models import Party, VisitorToParty, InvoiceRow
        private_fields = {
            '_first_party_name': self.__class__._first_party_name(
                Party=Party
            ),
            '_first_party_income': self.__class__._first_party_income(
                Party=Party,
                VisitorToParty=VisitorToParty,
                InvoiceRow=InvoiceRow
            ),
            '_last_party_name': self.__class__._last_party_name(
                Party=Party
            ),
            '_last_party_income': self.__class__._last_party_income(
                Party=Party,
                VisitorToParty=VisitorToParty,
                InvoiceRow=InvoiceRow
            ),
            '_average_income_per_party': self.__class__._average_income_per_party(
                Party=Party,
                InvoiceRow=InvoiceRow,
                VisitorToParty=VisitorToParty
            ),
            '_parties_count': self.__class__._parties_count(Party=Party),
            '_total_incomes': self.__class__._total_incomes(
                Party=Party,
                InvoiceRow=InvoiceRow,
                VisitorToParty=VisitorToParty
            )
        }


        return self.annotate(**private_fields)
