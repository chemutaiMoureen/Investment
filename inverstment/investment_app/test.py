import pytest
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from .models import InvestmentAccount, Transaction, AccountMembership

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(username='admin', password='admin')

@pytest.fixture
def view_only_user():
    return User.objects.create_user(username='viewonlyuser', password='viewonlypass')

@pytest.fixture
def crud_user():
    return User.objects.create_user(username='cruduser', password='crudpass')

@pytest.fixture
def post_only_user():
    return User.objects.create_user(username='postonlyuser', password='postonlypass')

@pytest.fixture
def account1():
    return InvestmentAccount.objects.create(name='View Account')

@pytest.fixture
def account2():
    return InvestmentAccount.objects.create(name='CRUD Account')

@pytest.fixture
def account3():
    return InvestmentAccount.objects.create(name='Post Account')

@pytest.fixture
def setup_account_memberships(view_only_user, crud_user, post_only_user, account1, account2, account3):
    AccountMembership.objects.create(user=view_only_user, account=account1, role='view')
    AccountMembership.objects.create(user=crud_user, account=account2, role='crud')
    AccountMembership.objects.create(user=post_only_user, account=account3, role='post')

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client

@pytest.mark.django_db
def test_view_only_user_cannot_perform_crud_operations(api_client, view_only_user, account1, setup_account_memberships):
    api_client.force_authenticate(user=view_only_user)
    
    response = api_client.post('/api/investment-accounts/', data={'name': 'New Account'}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    response = api_client.patch(f'/api/investment-accounts/{account1.id}/', data={'name': 'Updated Account'}, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    response = api_client.delete(f'/api/investment-accounts/{account1.id}/')
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_crud_user_can_perform_all_crud_operations(api_client, crud_user, account2, setup_account_memberships):
    api_client.force_authenticate(user=crud_user)
    
    response = api_client.post('/api/investment-accounts/', data={'name': 'New CRUD Account'}, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    
    account_id = response.data['id']
    
    response = api_client.patch(f'/api/investment-accounts/{account_id}/', data={'name': 'Updated CRUD Account'}, format='json')
    assert response.status_code == status.HTTP_200_OK
    
    response = api_client.delete(f'/api/investment-accounts/{account_id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.django_db
def test_post_only_user_can_post_transactions(api_client, post_only_user, account3, setup_account_memberships):
    api_client.force_authenticate(user=post_only_user)
    
    # Post a transaction
    response = api_client.post('/api/transactions/', data={
        'account': account3.id, 
        'user': post_only_user.id, 
        'amount': 100, 
        'date': '2024-01-01', 
        'description': 'Test Transaction'
    }, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Try to get transactions (should be forbidden)
    response = api_client.get('/api/transactions/')
    print(response.data)  # Add this line to inspect the response data
    assert response.status_code == status.HTTP_403_FORBIDDEN

# def test_post_only_user_can_post_transactions(api_client, post_only_user, account3, setup_account_memberships):
#     api_client.force_authenticate(user=post_only_user)
    
#     response = api_client.post('/api/transactions/', data={'account': account3.id, 'user': post_only_user.id, 'amount': 100, 'date': '2024-01-01', 'description': 'Test Transaction'}, format='json')
#     assert response.status_code == status.HTTP_201_CREATED
    
#     response = api_client.get('/api/transactions/')
#     assert response.status_code == status.HTTP_403_FORBIDDEN
# @pytest.mark.django_db
# def test_admin_endpoint_returns_all_transactions(api_client, admin_user, account3):
#     # Make sure admin_user is an actual admin
#     admin_user.is_staff = True
#     admin_user.save()

#     api_client.force_authenticate(user=admin_user)
#     Transaction.objects.create(account=account3, user=admin_user, amount=100, date='2024-01-01', description='Test Transaction')
    
#     response = api_client.get('/api/transactions/admin-list/')
    
#     assert response.status_code == status.HTTP_200_OK
#     assert 'transactions' in response.data
#     assert len(response.data['transactions']) > 0

# @pytest.mark.django_db
# def test_admin_endpoint_returns_all_transactions(api_client, admin_user, account3):
#     api_client.force_authenticate(user=admin_user)
#     Transaction.objects.create(account=account3, user=admin_user, amount=100, date='2024-01-01', description='Test Transaction')
#     response = api_client.get('/api/transactions/admin-list/')
    
#     assert response.status_code == status.HTTP_200_OK
#     assert 'transactions' in response.data
#     assert len(response.data['transactions']) > 0

# @pytest.mark.django_db
# def test_admin_endpoint_sum_of_total_balance(api_client, admin_user, account3):
#     api_client.force_authenticate(user=admin_user)
#     Transaction.objects.create(account=account3, user=admin_user, amount=100, date='2024-01-01', description='Test Transaction')
#     Transaction.objects.create(account=account3, user=admin_user, amount=200, date='2024-02-01', description='Test Transaction 2')
    
#     response = api_client.get('/api/transactions/admin-list/')
#     assert response.status_code == status.HTTP_200_OK
#     total_balance = response.data['total_balance']
#     assert total_balance == 300
