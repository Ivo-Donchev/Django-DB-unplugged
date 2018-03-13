from decimal import Decimal

from django.db import models

from .query import (
    InvoiceRowQuerySet,
    InvoiceQuerySet,
    VisitorToPartyQuerySet,
    PartyQuerySet,
    ClubQueryset,
)


class Club(models.Model):
    objects = ClubQueryset.as_manager()

    name = models.CharField(max_length=255)

    @property
    def first_party(self):
        return self.parties.first()

    @property
    def first_party_income(self):
        if hasattr(self, '_first_party_income'):
            return self._first_party_income

        return self.first_party.total_party_income

    @property
    def first_party_name(self):
        if hasattr(self, '_first_party_name'):
            return self._first_party_name

        return self.first_party.name

    @property
    def last_party(self):
        return self.parties.last()

    @property
    def last_party_name(self):
        if hasattr(self, '_last_party_name'):
            return self._last_party_name

        return self.last_party.name

    @property
    def last_party_income(self):
        if hasattr(self, '_last_party_income'):
            return self._last_party_income

        return self.first_party.total_party_income

    @property
    def average_income_per_party(self):
        if hasattr(self, '_average_income_per_party'):
            return self._average_income_per_party

        return self.total_incomes / self.parties_count

    @property
    def parties_count(self):
        if hasattr(self, '_parties_count'):
            return self._parties_count

        return self.parties.count()

    @property
    def total_incomes(self):
        if hasattr(self, '_total_incomes'):
            return self._total_incomes

        income = Decimal(0.0)

        for party in self.parties.all():
            income += party.total_party_income

        return round(income, 2)


class Visitor(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()


class Party(models.Model):
    objects = PartyQuerySet.as_manager()

    name = models.CharField(max_length=255)
    club = models.ForeignKey(Club, related_name='parties')
    visitors = models.ManyToManyField(Visitor, related_name='parties', through='VisitorToParty')

    def __str__(self):
        return self.name


    @property
    def invoices_count(self):
        if hasattr(self, '_invoices_count'):
            return self._invoices_count

        count = 0

        for visitortoparty_item in self.visitortoparty_set.all():
            if visitortoparty_item.invoice is not None:
                count += 1

        return count

    @property
    def total_party_income(self):
        if hasattr(self, '_total_party_income'):
            return self._total_party_income

        visitortoparty_set = self.visitortoparty_set.all()
        income = Decimal(0.0)

        for visitortoparty_item in visitortoparty_set:
            income += visitortoparty_item.invoice_amount

        return round(income, 2)


class VisitorToParty(models.Model):
    objects = VisitorToPartyQuerySet.as_manager()

    # Default fields of the throgh models
    visitor = models.ForeignKey(Visitor, related_name='visitortoparty_set')
    party = models.ForeignKey(Party, related_name='visitortoparty_set')

    invoice = models.OneToOneField(
        'Invoice',
        related_name='visitortoparty',
        null=True
    )

    @property
    def invoice_amount(self):
        if hasattr(self, '_invoice_amount'):
            return self._invoice_amount

        return Decimal(self.invoice.total_amount)


class Invoice(models.Model):
    objects = InvoiceQuerySet.as_manager()

    description = models.CharField(max_length=255, null=True, blank=True)
    default_tax_rate = models.DecimalField(default=0.2, decimal_places=2, max_digits=4)

    @property
    def details(self):
        if hasattr(self, '_description'):
            return self._description

        if self.description:
            return self.description

        return self.rows.first().description

    @property
    def total_amount(self):
        if hasattr(self, '_total_amount'):
            return self._total_amount

        rows = self.rows.all()
        amount = Decimal(0.0)

        for row in rows:
            amount += row.amount

        return Decimal(amount)


class InvoiceRow(models.Model):
    objects = InvoiceRowQuerySet.as_manager()

    invoice = models.ForeignKey(Invoice, related_name='rows')

    description = models.CharField(max_length=255)

    tax_rate = models.DecimalField(
        default=0.0,
        decimal_places=2,
        max_digits=4
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(decimal_places=2, max_digits=4)

    @property
    def amount_without_tax(self):
        if hasattr(self, '_amount_without_tax'):
            return self._amount_without_tax

        return Decimal(self.quantity * self.unit_price)

    @property
    def amount(self):
        if hasattr(self, '_amount'):
            return self._amount

        without_tax = self.amount_without_tax

        if self.tax_rate != 0:
            tax = Decimal(self.tax_rate)
        else:
            tax = Decimal(self.invoice.default_tax_rate)

        return Decimal(without_tax * (1 + tax))
