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
    
    def validate(self, data):
        """
        Check that the user is allowed to create a transaction for the given account.
        """
        user = data.get('user')
        account = data.get('account')
        if not AccountMembership.objects.filter(user=user, account=account).exists():
            raise serializers.ValidationError("User is not a member of the specified account.")
        return data

class AccountMembershipSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    account = serializers.PrimaryKeyRelatedField(queryset=InvestmentAccount.objects.all())

    class Meta:
        model = AccountMembership
        fields = ['user', 'account', 'role']
    
    def validate(self, data):
        """
        Validate that the user does not already have a role in the account.
        """
        user = data.get('user')
        account = data.get('account')
        if AccountMembership.objects.filter(user=user, account=account).exists():
            raise serializers.ValidationError("User already has a role in the specified account.")
        return data
