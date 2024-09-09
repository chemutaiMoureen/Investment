from django.db import models
from django.contrib.auth.models import User

class InvestmentAccount(models.Model):
    name = models.CharField(max_length=255)
    # Add any additional fields as needed

    def __str__(self):
        return self.name

class Transaction(models.Model):
    account = models.ForeignKey(InvestmentAccount, related_name='transactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField()

    def __str__(self):
        return f"{self.amount} on {self.date}"

class AccountMembership(models.Model):
    ROLE_CHOICES = [
        ('view', 'View'),
        ('post', 'Post'),
        ('crud', 'CRUD'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(InvestmentAccount, on_delete=models.CASCADE)
    role = models.CharField(max_length=4, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ('user', 'account')
