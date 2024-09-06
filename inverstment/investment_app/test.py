from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import datetime
from .models import User, InvestmentAccount, Transaction, AccountMembership

class InvestmentAccountAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')
        self.view_user = User.objects.create_user(username='view_user', password='viewpass')
        self.crud_user = User.objects.create_user(username='crud_user', password='crudpass')
        self.post_user = User.objects.create_user(username='post_user', password='postpass')

        self.view_account = InvestmentAccount.objects.create(name='View Account')
        self.crud_account = InvestmentAccount.objects.create(name='CRUD Account')
        self.post_account = InvestmentAccount.objects.create(name='Post Account')

        # Assign roles
        AccountMembership.objects.create(user=self.view_user, account=self.view_account, role='view')
        AccountMembership.objects.create(user=self.crud_user, account=self.crud_account, role='crud')
        AccountMembership.objects.create(user=self.post_user, account=self.post_account, role='post')

    def test_view_user_cannot_manage_transactions(self):
        # User with view-only access
        self.client.login(username='view_user', password='viewpass')
        response = self.client.post('/api/transactions/', {'account': self.view_account.id, 'amount': 100, 'description': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure they cannot update or delete
        transaction = Transaction.objects.create(account=self.view_account, user=self.view_user, amount=100, description='Test')
        response = self.client.put(f'/api/transactions/{transaction.id}/', {'amount': 200, 'description': 'Updated Test'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(f'/api/transactions/{transaction.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crud_user_can_manage_transactions(self):
        # User with CRUD access
        self.client.login(username='crud_user', password='crudpass')
        response = self.client.post('/api/transactions/', {'account': self.crud_account.id, 'amount': 100, 'description': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction_id = response.data['id']
        
        # Retrieve transaction
        response = self.client.get(f'/api/transactions/{transaction_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Update transaction
        response = self.client.put(f'/api/transactions/{transaction_id}/', {'amount': 150, 'description': 'Updated Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Delete transaction
        response = self.client.delete(f'/api/transactions/{transaction_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_user_can_only_create_transactions(self):
        # User with post-only access
        self.client.login(username='post_user', password='postpass')
        response = self.client.post('/api/transactions/', {'account': self.post_account.id, 'amount': 100, 'description': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure they cannot view transactions
        response = self.client.get(f'/api/transactions/?account={self.post_account.id}')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_transactions(self):
        # Create transaction and check admin access
        Transaction.objects.create(account=self.crud_account, user=self.crud_user, amount=100, description='Deposit')
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/api/admin-transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_balance', response.data)

    def test_admin_can_view_transactions_with_date_filter(self):
        # Create transactions with specific dates
        start_date = timezone.make_aware(datetime(2024, 1, 1))
        end_date = timezone.make_aware(datetime(2024, 1, 2))
        Transaction.objects.create(account=self.crud_account, user=self.crud_user, amount=100, date=start_date, description='Test1')
        Transaction.objects.create(account=self.crud_account, user=self.crud_user, amount=200, date=end_date, description='Test2')

        self.client.login(username='admin', password='adminpass')
        response = self.client.get(f'/api/admin-transactions/?start_date={start_date.date()}&end_date={start_date.date()}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['transactions']), 1)
        self.assertEqual(response.data['total_balance'], 100)
