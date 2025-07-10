from rest_framework import status, generics, permissions, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import models
from django.db import transaction as db_transaction
from decimal import Decimal
from .models import User, Transaction, Contact
from .serializers import (
    UserSerializer, SignupSerializer, LoginSerializer,
    TransactionSerializer, ContactSerializer
)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

# --- Authentication Views ---

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'user': UserSerializer(user).data, 'token': token}, status=status.HTTP_201_CREATED)

class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        pin = serializer.validated_data['pin']
        user = authenticate(request, phone=phone, password=pin)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'user': UserSerializer(user).data, 'token': token})
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# --- User Views ---

class ProfileView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'user': UserSerializer(request.user).data})

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'user': serializer.data})

class ChangePinView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        current_pin = request.data.get('current_pin')
        new_pin = request.data.get('new_pin')
        if not current_pin or not new_pin:
            return Response({'detail': 'Both current_pin and new_pin are required.'}, status=400)
        user = request.user
        if not user.check_password(current_pin):
            return Response({'detail': 'Current PIN is incorrect.'}, status=400)
        user.set_password(new_pin)
        user.save()
        return Response({'success': True})

# --- Transaction Views ---

class TransactionListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        sent = Transaction.objects.filter(sender=user)
        received = Transaction.objects.filter(receiver=user)
        transactions = sent.union(received).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response({'transactions': serializer.data, 'balance': float(user.balance)})

class SendTransactionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @db_transaction.atomic
    def post(self, request):
        sender = request.user
        recipient_phone = request.data.get('recipient_phone')
        amount = request.data.get('amount')
        if not recipient_phone or not amount:
            return Response({'detail': 'recipient_phone and amount are required.'}, status=400)
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                raise ValueError
        except:
            return Response({'detail': 'Amount must be a positive number.'}, status=400)
        if sender.balance < amount:
            return Response({'detail': 'Insufficient balance.'}, status=400)
        try:
            receiver = User.objects.get(phone=recipient_phone)
        except User.DoesNotExist:
            return Response({'detail': 'Recipient not found.'}, status=404)

        # Deduct and add balance atomically
        sender.balance -= amount
        receiver.balance += amount
        sender.save()
        receiver.save()

        # Create transactions for both sender and receiver
        tx_sent = Transaction.objects.create(
            sender=sender, receiver=receiver, amount=amount, type='sent', status='completed'
        )
        tx_received = Transaction.objects.create(
            sender=sender, receiver=receiver, amount=amount, type='received', status='completed'
        )

        serializer = TransactionSerializer(tx_sent)
        return Response({'transaction': serializer.data, 'new_balance': float(sender.balance)})


# --- Contact Views ---

class ContactSearchView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '')
        user = request.user
        contacts = User.objects.filter(
            models.Q(name__icontains=q) | models.Q(phone__icontains=q) | models.Q(email__icontains=q)
        ).exclude(id=user.id)
        serializer = UserSerializer(contacts, many=True)
        return Response({'contacts': serializer.data})
