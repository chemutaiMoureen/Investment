from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone

class User(AbstractUser):
    # Custom fields and methods can be added here if needed
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user'
    )

class InvestmentAccount(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, through='AccountMembership')

    def __str__(self):
        return self.name

class AccountMembership(models.Model):
    ROLE_CHOICES = [
        ('view', 'View'),
        ('crud', 'CRUD'),
        ('post', 'Post Only'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'account')  # Ensure a user can't have multiple roles in the same account

class Transaction(models.Model):
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)  # Default to the current time in the timezone-aware format
    description = models.TextField()

    def __str__(self):
        return f"{self.amount} - {self.description}"
