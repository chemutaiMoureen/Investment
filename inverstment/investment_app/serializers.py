from rest_framework import serializers
from .models import User, InvestmentAccount, Transaction, AccountMembership

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InvestmentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentAccount
        fields = ['id', 'name']

class TransactionSerializer(serializers.ModelSerializer):
    account = serializers.PrimaryKeyRelatedField(queryset=InvestmentAccount.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'user', 'amount', 'date', 'description']

class AccountMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    account = InvestmentAccountSerializer()

    class Meta:
        model = AccountMembership
        fields = ['user', 'account', 'role']
