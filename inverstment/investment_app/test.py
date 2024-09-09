from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import InvestmentAccount, Transaction, AccountMembership

class InvestmentAppTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass')
        self.view_only_user = User.objects.create_user(username='viewonlyuser', password='viewonlypass')
        self.crud_user = User.objects.create_user(username='cruduser', password='crudpass')
        self.post_only_user = User.objects.create_user(username='postonlyuser', password='postonlypass')
        
        self.account1 = InvestmentAccount.objects.create(name='View Account')
        self.account2 = InvestmentAccount.objects.create(name='CRUD Account')
        self.account3 = InvestmentAccount.objects.create(name='Post Account')

        AccountMembership.objects.create(user=self.view_only_user, account=self.account1, role='view')
        AccountMembership.objects.create(user=self.crud_user, account=self.account2, role='crud')
        AccountMembership.objects.create(user=self.post_only_user, account=self.account3, role='post')

        self.client.force_authenticate(user=self.admin_user)
    
    def test_view_only_user_cannot_perform_crud_operations(self):
        self.client.force_authenticate(user=self.view_only_user)
        
        response = self.client.post('/investment-accounts/', data={'name': 'New Account'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.patch(f'/investment-accounts/{self.account1.id}/', data={'name': 'Updated Account'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        response = self.client.delete(f'/investment-accounts/{self.account1.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crud_user_can_perform_all_crud_operations(self):
        self.client.force_authenticate(user=self.crud_user)
        
        response = self.client.post('/investment-accounts/', data={'name': 'New CRUD Account'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        account_id = response.data['id']
        
        response = self.client.patch(f'/investment-accounts/{account_id}/', data={'name': 'Updated CRUD Account'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.delete(f'/investment-accounts/{account_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_post_only_user_can_post_transactions(self):
        self.client.force_authenticate(user=self.post_only_user)
        
        response = self.client.post('/transactions/', data={'account': self.account3.id, 'user': self.post_only_user.id, 'amount': 100, 'date': '2024-01-01', 'description': 'Test Transaction'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.get('/transactions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_endpoint_returns_all_transactions(self):
        self.client.force_authenticate(user=self.admin_user)
        Transaction.objects.create(account=self.account3, user=self.admin_user, amount=100, date='2024-01-01', description='Test Transaction')
        
        response = self.client.get('/admin-transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['transactions']), 0)

    def test_admin_endpoint_sum_of_total_balance(self):
        self.client.force_authenticate(user=self.admin_user)
        Transaction.objects.create(account=self.account3, user=self.admin_user, amount=100, date='2024-01-01', description='Test Transaction')
        Transaction.objects.create(account=self.account3, user=self.admin_user, amount=200, date='2024-02-01', description='Test Transaction 2')
        
        response = self.client.get('/admin-transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        total_balance = response.data['total_balance']
        self.assertEqual(total_balance, 300)
