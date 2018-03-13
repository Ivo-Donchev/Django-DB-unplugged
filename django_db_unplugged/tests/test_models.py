from django.test import TestCase

from dashboard.models import (
    Club,
    Party,
    Invoice,
    Visitor,
    InvoiceRow,
    VisitorToParty,
)


class InvoiceRowTests(TestCase):
    def setUp(self):
        self.invoice = Invoice.objects.create(description='asdf')

    def test_amount_without_tax(self):
        created_invoice_row = InvoiceRow.objects.create(
            description='Vodka',
            invoice=self.invoice,
            tax_rate=0.5,
            quantity=2,
            unit_price=5
        )
        invoice_row = InvoiceRow.objects.get(id=created_invoice_row.id)
        self.assertEqual(10.0, invoice_row.amount_without_tax)

        invoice_row = InvoiceRow.objects.collect().get(id=created_invoice_row.id)
        self.assertEqual(10.0, invoice_row.amount_without_tax)

    def test_amount(self):
        created_invoice_row = InvoiceRow.objects.create(
            description='Vodka',
            invoice=self.invoice,
            tax_rate=0.2,
            quantity=2,
            unit_price=5
        )
        invoice_row = InvoiceRow.objects.get(id=created_invoice_row.id)
        self.assertEqual(12.0, invoice_row.amount)

        invoice_row = InvoiceRow.objects.collect().get(id=created_invoice_row.id)
        self.assertEqual(12.0, invoice_row.amount)

    def test_amount_with_invoices_tax(self):
        invoice = Invoice.objects.create(
            description='asdf',
            default_tax_rate=0.8
        )
        created_invoice_row = InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice,
            tax_rate=0.0,
            quantity=2,
            unit_price=5
        )
        invoice_row = InvoiceRow.objects.get(id=created_invoice_row.id)
        self.assertEqual(18.0, invoice_row.amount)

        invoice_row = InvoiceRow.objects.collect().get(
            id=created_invoice_row.id
        )
        self.assertEqual(18.0, invoice_row.amount)


class InvoiceTests(TestCase):
    def test_details_from_description(self):
        created_invoice = Invoice.objects.create(description='asdf')

        invoice = Invoice.objects.get(id=created_invoice.id)
        self.assertEqual('asdf', invoice.details)

        invoice = Invoice.objects.collect().get(id=created_invoice.id)
        self.assertEqual('asdf', invoice.details)

    def test_details_from_item(self):
        created_invoice = Invoice.objects.create(description=None)
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=created_invoice,
            tax_rate=0.0,
            quantity=2,
            unit_price=5
        )

        invoice = Invoice.objects.get(id=created_invoice.id)
        self.assertEqual('Vodka', invoice.details)

        invoice = Invoice.objects.collect().get(id=created_invoice.id)
        self.assertEqual('Vodka', invoice.details)

    def test_amount(self):
        created_invoice = Invoice.objects.create(description=None)

        for _ in range(5):
            InvoiceRow.objects.create(
                description='Vodka',
                invoice=created_invoice,
                tax_rate=0.2,
                quantity=2,
                unit_price=5
            )

        invoice = Invoice.objects.get(id=created_invoice.id)
        self.assertEqual(60, invoice.total_amount)

        invoice = Invoice.objects.collect().get(id=created_invoice.id)
        self.assertEqual(60, invoice.total_amount)

    def test_amount_with_tax_rate_from_invoice(self):
        created_invoice = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )

        for _ in range(5):
            InvoiceRow.objects.create(
                description='Vodka',
                invoice=created_invoice,
                tax_rate=0.0,
                quantity=2,
                unit_price=5
            )

        invoice = Invoice.objects.get(id=created_invoice.id)
        self.assertEqual(75, invoice.total_amount)

        invoice = Invoice.objects.collect().get(id=created_invoice.id)
        self.assertEqual(75, invoice.total_amount)


class VisitorToPartyTests(TestCase):
    def test_amount(self):
        club = Club.objects.create(name='Versai')
        created_invoice = Invoice.objects.create(description=None)
        created_v2p = VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=created_invoice,
            party=Party.objects.create(
                name='Boro',
                club=club
            )
        )

        for _ in range(5):
            InvoiceRow.objects.create(
                description='Vodka',
                invoice=created_invoice,
                tax_rate=0.2,
                quantity=2,
                unit_price=5
            )

        v2p = VisitorToParty.objects.get(id=created_v2p.id)
        self.assertEqual(60, v2p.invoice_amount)

        v2p = VisitorToParty.objects.collect().get(id=created_v2p.id)
        self.assertEqual(60, v2p.invoice_amount)

    def test_amount_with_tax_rate_from_invoice(self):
        club = Club.objects.create(name='Versai')
        created_invoice = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        created_v2p = VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=created_invoice,
            party=Party.objects.create(
                name='Boro',
                club=club,
            )
        )

        for _ in range(5):
            InvoiceRow.objects.create(
                description='Vodka',
                invoice=created_invoice,
                tax_rate=0.0,
                quantity=2,
                unit_price=5
            )

        v2p = VisitorToParty.objects.get(id=created_v2p.id)
        self.assertEqual(75, v2p.invoice_amount)

        v2p = VisitorToParty.objects.collect().get(id=created_v2p.id)
        self.assertEqual(75, v2p.invoice_amount)


class PartyTests(TestCase):
    def test_invoices_count_if_no_invoices_exists(self):
        club = Club.objects.create(name='Versai')
        created_party=Party.objects.create(
            name='Boro',
            club=club,
        )
        party = Party.objects.get(id=created_party.id)
        self.assertEqual(0, party.invoices_count)

        party = Party.objects.collect().get(id=created_party.id)
        self.assertEqual(0, party.invoices_count)

    def test_invoices_count(self):
        club = Club.objects.create(name='Versai')
        created_party=Party.objects.create(
            name='Boro',
            club=club,
        )
        invoice1 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice1,
            party=created_party
        )
        invoice2 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice2,
            party=created_party
        )

        party = Party.objects.get(id=created_party.id)
        self.assertEqual(2, party.invoices_count)

        party = Party.objects.collect().get(id=created_party.id)
        self.assertEqual(2, party.invoices_count)


    def test_total_party_income(self):
        club = Club.objects.create(name='Versai')
        created_party=Party.objects.create(
            name='Boro',
            club=club,
        )
        invoice1 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice1,
            tax_rate=0.5,
            quantity=2,
            unit_price=5
        )

        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice1,
            party=created_party
        )
        invoice2 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice2,
            tax_rate=0.5,
            quantity=2,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice2,
            party=created_party
        )

        party = Party.objects.get(id=created_party.id)
        self.assertEqual(30, party.total_party_income)

        party = Party.objects.collect().get(id=created_party.id)
        self.assertEqual(30, party.total_party_income)


class ClubTests(TestCase):
    def test_first_and_last_party_names_and_incomes(self):
        created_club = Club.objects.create(name='Versai')
        party1 = Party.objects.create(
            name='Boro',
            club=created_club,
        )
        invoice1 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice1,
            tax_rate=0.5,
            quantity=4,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice1,
            party=party1
        )

        party2 = Party.objects.create(
            name='Boro',
            club=created_club,
        )
        invoice2 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice2,
            tax_rate=0.5,
            quantity=2,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice2,
            party=party2
        )

        party3 = Party.objects.create(
            name='Boro i Madmatik',
            club=created_club,
        )
        invoice3 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice3,
            tax_rate=0.5,
            quantity=1,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice3,
            party=party3
        )

        club = Club.objects.get(id=created_club.id)
        self.assertEqual('Boro', club.first_party_name)
        self.assertEqual('Boro i Madmatik', club.last_party_name)
        self.assertEqual(30, club.first_party_income)
        self.assertEqual(7.5, club.last_party_income)

        club = Club.objects.collect().get(id=created_club.id)
        self.assertEqual('Boro', club.first_party_name)
        self.assertEqual('Boro i Madmatik', club.last_party_name)
        self.assertEqual(30, club.first_party_income)
        self.assertEqual(7.5, club.last_party_income)

    def test_parties_count_if_no_parties_exists(self):
        created_club = Club.objects.create(name='Versai')

        club = Club.objects.get(id=created_club.id)
        self.assertEqual(0, club.parties_count)

        club = Club.objects.collect().get(id=created_club.id)
        self.assertEqual(0, club.parties_count)

    def test_parties_count(self):
        created_club = Club.objects.create(name='Versai')
        Party.objects.create(
            name='Boro',
            club=created_club,
        )

        club = Club.objects.get(id=created_club.id)
        self.assertEqual(1, club.parties_count)

        club = Club.objects.collect().get(id=created_club.id)
        self.assertEqual(1, club.parties_count)

    def test_average_income_per_party(self):
        created_club = Club.objects.create(name='Versai')
        party1 = Party.objects.create(
            name='Boro',
            club=created_club,
        )
        invoice1 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice1,
            tax_rate=0.5,
            quantity=4,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice1,
            party=party1
        )

        party2 = Party.objects.create(
            name='Boro',
            club=created_club,
        )
        invoice2 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice2,
            tax_rate=0.5,
            quantity=2,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice2,
            party=party2
        )

        party3 = Party.objects.create(
            name='Boro i Madmatik',
            club=created_club,
        )
        invoice3 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice3,
            tax_rate=0.5,
            quantity=1,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice3,
            party=party3
        )

        expected_value = (30 + 15 + 7.5) / 3
        club = Club.objects.get(id=created_club.id)
        self.assertEqual(expected_value, club.average_income_per_party)

        club = Club.objects.collect().get(id=created_club.id)
        self.assertEqual(expected_value, club.average_income_per_party)

    def test_total_incomes(self):
        created_club = Club.objects.create(name='Versai')
        party1 = Party.objects.create(
            name='Boro',
            club=created_club,
        )
        invoice1 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice1,
            tax_rate=0.5,
            quantity=4,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice1,
            party=party1
        )

        party2 = Party.objects.create(
            name='Boro',
            club=created_club,
        )
        invoice2 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice2,
            tax_rate=0.5,
            quantity=2,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice2,
            party=party2
        )

        party3 = Party.objects.create(
            name='Boro i Madmatik',
            club=created_club,
        )
        invoice3 = Invoice.objects.create(
            description=None,
            default_tax_rate=0.5
        )
        InvoiceRow.objects.create(
            description='Vodka',
            invoice=invoice3,
            tax_rate=0.5,
            quantity=1,
            unit_price=5
        )
        VisitorToParty.objects.create(
            visitor=Visitor.objects.create(full_name='Ivo', age=20),
            invoice=invoice3,
            party=party3
        )

        expected_value = (30 + 15 + 7.5)
        club = Club.objects.get(id=created_club.id)
        self.assertEqual(expected_value, club.total_incomes)

        club = Club.objects.collect().get(id=created_club.id)
        self.assertEqual(expected_value, club.total_incomes)
