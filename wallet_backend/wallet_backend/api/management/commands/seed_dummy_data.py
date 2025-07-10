from django.core.management.base import BaseCommand
from api.models import User, Transaction, Contact
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timezone

class Command(BaseCommand):
    help = 'Seed database with dummy users, transactions, contacts, and balance'

    def handle(self, *args, **kwargs):
        # Clear existing data (optional)
        Transaction.objects.all().delete()
        Contact.objects.all().delete()
        User.objects.all().delete()

        # Create users
        users_data = [
            {"id": "1", "name": "John Doe", "phone": "+1234567890", "email": "john@example.com", "pin": "1234", "balance": Decimal('12450.75')},
            {"id": "2", "name": "Alice Johnson", "phone": "+987564321", "email": "alice@example.com", "pin": "1234", "balance": Decimal('5000.00')},
            {"id": "3", "name": "Bob Smith", "phone": "+1987654321", "email": "bob@example.com", "pin": "1234", "balance": Decimal('3000.00')},
            {"id": "4", "name": "Charlie Brown", "phone": "+1122334455", "email": "charlie@example.com", "pin": "1234", "balance": Decimal('7000.00')},
            {"id": "5", "name": "Diana Prince", "phone": "+1555666777", "email": "diana@example.com", "pin": "1234", "balance": Decimal('8000.00')},
            {"id": "6", "name": "Edward Norton", "phone": "+1999888777", "email": "edward@example.com", "pin": "1234", "balance": Decimal('6000.00')},
        ]

        users = {}
        for udata in users_data:
            user = User(
                id=udata['id'],
                name=udata['name'],
                phone=udata['phone'],
                email=udata['email'],
                balance=udata['balance'],
                is_active=True,
                is_staff=False,
            )
            user.set_password(udata['pin'])
            user.save()
            users[udata['name']] = user

        # Create transactions
        transactions_data = [
            {
                "id": 1,
                "type": "received",
                "amount": Decimal('500'),
                "sender_name": "Alice Johnson",
                "receiver_name": "John Doe",
                "date": "2024-01-15"
            },
            {
                "id": 2,
                "type": "sent",
                "amount": Decimal('250'),
                "sender_name": "John Doe",
                "receiver_name": "Bob Smith",
                "date": "2024-01-14"
            },
            {
                "id": 3,
                "type": "received",
                "amount": Decimal('1000'),
                "sender_name": "Charlie Brown",
                "receiver_name": "John Doe",
                "date": "2024-01-13"
            },
        ]

        for tdata in transactions_data:
            sender = users.get(tdata['sender_name'])
            receiver = users.get(tdata['receiver_name'])
            created_at = datetime.strptime(tdata['date'], '%Y-%m-%d').replace(tzinfo=timezone.utc)

            Transaction.objects.create(
                id=tdata['id'],
                sender=sender,
                receiver=receiver,
                amount=tdata['amount'],
                type=tdata['type'],
                status='completed',
                created_at=created_at,
            )

        # Create contacts for John Doe (user id=1)
        john = users['John Doe']
        contact_names = ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Prince", "Edward Norton"]
        for cname in contact_names:
            contact_user = users[cname]
            Contact.objects.create(user=john, contact_user=contact_user)

        self.stdout.write(self.style.SUCCESS('Dummy data seeded successfully.'))
