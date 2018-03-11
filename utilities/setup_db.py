from dashboard.models import (
    Invoice,
    Club,
    InvoiceRow,
    Party,
    Visitor,
    VisitorToParty,
)


def create_clubs():
    clubs = [
        Club(name='Club {}'.format(i))
        for i in range(1, 34)
    ]
    return Club.objects.bulk_create(clubs)


def create_visitors():
    visitors = [
        Visitor(full_name='Ivaylo Donchev', age=20),
        Visitor(full_name='Pavlin Gergov', age=20),
        Visitor(full_name='Martin Angelov', age=20),
        Visitor(full_name='Krasimira Badova', age=20),
        Visitor(full_name='Alexander Nadjarian', age=20),
        Visitor(full_name='Radoslav Georgiev', age=20),
        Visitor(full_name='Dimitar Kotsev', age=20),
        Visitor(full_name='Kamen Kotsev', age=20),
        Visitor(full_name='Vasil Slavov', age=20),
        Visitor(full_name='Tony Yordanova', age=20),
        Visitor(full_name='Slavyana Monkova', age=20),
    ]

    return Visitor.objects.bulk_create(visitors)


def create_parties(clubs):
    parties = []
    for club in clubs:
        parties += [
            Party(
                name='Party {} for {}'.format(i, club.name),
                club=club
            )
            for i in range(10)
        ]

    return Party.objects.bulk_create(parties)


def create_invoices_with_rows(parties, visitors):
    invoices = []
    invoice_rows = []
    for party in parties:
        for visitor in visitors:
            invoice = Invoice(description="Invoice for ".format(party.name))
            invoices.append(invoice)

    invoices = Invoice.objects.bulk_create(invoices)

    for invoice in invoices:
        invoice_rows += [
            InvoiceRow(
                description='Vodka',
                invoice=invoice,
                tax_rate=0.5,
                quantity=2,
                unit_price=5
            ),
            InvoiceRow(
                description='Beer',
                invoice=invoice,
                tax_rate=0.5,
                quantity=2,
                unit_price=5
            ),
            InvoiceRow(
                description='Salfetki',
                invoice=invoice,
                tax_rate=0.5,
                quantity=100,
                unit_price=0.2
            ),
        ]
    InvoiceRow.objects.bulk_create(invoice_rows)

    return invoices

def create_visitor_to_party_set():
    invoices = list(Invoice.objects.all())
    parties = list(Party.objects.all())
    visitors = list(Visitor.objects.all())

    invoice_idx = 0
    visitor_to_parties = []

    for party in parties:
        for visitor in visitors:
            visitor_to_parties.append(
                VisitorToParty(visitor=visitor, party=party, invoice=invoices[invoice_idx])
            )
            invoice_idx +=1

    visitor_to_parties


print('Creating Clubs')
clubs = create_clubs()
print('Created {} clubs'.format(Club.objects.count()))

print('----------------------------------')

print('Creating Visitors')
visitors = create_visitors()
print('Created {} visitors'.format(Visitor.objects.count()))

print('----------------------------------')

print('Creating Parties')
parties = create_parties(clubs)
print('Created {} parties'.format(Party.objects.count()))

print('----------------------------------')

print('Creating Invoices with InvoiceRows')
invoices = create_invoices_with_rows(parties, visitors)
print('Created {} invoices and {} invoice rows'.format(Invoice.objects.count(), InvoiceRow.objects.count()))

print('----------------------------------')

print('Creating Visitor to parties connections')
visitor_to_parties = create_visitor_to_party_set()
print('Created {} visitor_to_party-ies'.format(VisitorToParty.objects.count()))
