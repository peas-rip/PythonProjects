import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone, email, name, pin, **extra_fields):
        if not phone or not email or not name or not pin:
            raise ValueError('All fields are required')
        user = self.model(
            id=str(uuid.uuid4()),
            phone=phone,
            email=self.normalize_email(email),
            name=name,
            **extra_fields
        )
        user.set_password(pin)  # Use set_password for hashing
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email, name, pin, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone, email, name, pin, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(primary_key=True, max_length=50, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'name']

    objects = UserManager()

    def __str__(self):
        return self.phone

class Transaction(models.Model):
    TYPE_CHOICES = (('sent', 'Sent'), ('received', 'Received'))
    STATUS_CHOICES = (('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'))

    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, related_name='sent_transactions', on_delete=models.CASCADE, null=True)
    receiver = models.ForeignKey(User, related_name='received_transactions', on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    contact_user = models.ForeignKey(User, related_name='contacted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'contact_user')
