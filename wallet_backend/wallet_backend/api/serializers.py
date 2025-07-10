from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Transaction

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email', 'balance']

class SignupSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, min_length=4, max_length=10)

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email', 'pin']

    def create(self, validated_data):
        pin = validated_data.pop('pin')
        user = User.objects.create_user(pin=pin, **validated_data)

        # Set default balance if not already present
        if not user.balance or user.balance < 10000:
            user.balance = 10000
            user.save()

        return user

class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    pin = serializers.CharField(write_only=True)

class TransactionSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'amount', 'type', 'status', 'created_at']

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'email']
