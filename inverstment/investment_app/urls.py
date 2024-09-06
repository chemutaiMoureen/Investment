# investment_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestmentAccountViewSet, TransactionViewSet, AdminTransactionViewSet

router = DefaultRouter()
router.register(r'investment-accounts', InvestmentAccountViewSet)
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'admin-transactions', AdminTransactionViewSet, basename='admin-transaction')

urlpatterns = [
    path('', include(router.urls)),
]
