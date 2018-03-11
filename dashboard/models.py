from django.db import models
from decimal import Decimal


class Club(models.Model):
    name = models.CharField(max_length=255)

    @property
    def first_party(self):
        return self.parties.first()

    @property
    def last_party(self):
        return self.parties.last()

    @property
    def average_income_per_party(self):
        parties_count = self.parties.count()

        return self.total_incomes / parties_count

    @property
    def parties_count(self):
        return self.parties.count()

    @property
    def total_incomes(self):
        income = Decimal(0.0)

        for party in self.parties.all():
            income += party.total_party_income

        return round(income, 2)

class Visitor(models.Model):
    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()


class Party(models.Model):
    name = models.CharField(max_length=255)
    club = models.ForeignKey(Club, related_name='parties')
    visitors = models.ManyToManyField(Visitor, related_name='parties', through='VisitorToParty')

    def __str__(self):
        return self.name


    @property
    def invoices_count(self):
        count = 0

        for visitortoparty_item in self.visitortoparty_set.all():
            if visitortoparty_item.invoice is not None:
                count += 1

        return count

    @property
    def total_party_income(self):
        visitortoparty_set = self.visitortoparty_set.all()
        income = Decimal(0.0)

        for visitortoparty_item in visitortoparty_set:
            income += visitortoparty_item.invoice_amount

        return round(income, 2)


class VisitorToParty(models.Model):
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
        return Decimal(self.invoice.total_amount)


class Invoice(models.Model):
    description = models.CharField(max_length=255, null=True, blank=True)
    default_tax_rate = models.DecimalField(default=0.2, decimal_places=2, max_digits=4)

    @property
    def details(self):
        if self.description:
            return self.description
        return self.rows.first().description

    @property
    def total_amount(self):
        rows = self.rows.all()
        amount = Decimal(0.0)

        for row in rows:
            amount += row.amount

        return Decimal(amount)


class InvoiceRow(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='rows')

    description = models.CharField(max_length=255)

    tax_rate = models.DecimalField(default=0.0, decimal_places=2, max_digits=4) # if not set, get invoice's default
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(decimal_places=2, max_digits=4)

    @property
    def amount(self):
        without_tax = Decimal(self.quantity * self.unit_price)

        if self.tax_rate != 0:
            tax = Decimal(self.tax_rate)
        else:
            tax = Decimal(self.invoice.default_tax_rate)

        return Decimal(without_tax * (1 + tax))
