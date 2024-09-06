from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from .models import InvestmentAccount, Transaction, AccountMembership
from .serializers import InvestmentAccountSerializer, TransactionSerializer

class InvestmentAccountViewSet(viewsets.ModelViewSet):
    queryset = InvestmentAccount.objects.all()
    serializer_class = InvestmentAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return InvestmentAccount.objects.all()
        return InvestmentAccount.objects.filter(users=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        account_id = self.request.query_params.get('account', None)

        if not account_id:
            return Transaction.objects.none()

        account = get_object_or_404(InvestmentAccount, id=account_id, users=user)

        membership = AccountMembership.objects.filter(user=user, account=account).first()
        if not membership:
            return Transaction.objects.none()

        if membership.role == 'view':
            return Transaction.objects.none()
        elif membership.role == 'post':
            return Transaction.objects.filter(user=user, account=account)
        else:  # 'crud'
            return Transaction.objects.filter(account=account)

class AdminTransactionViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        if not user.is_superuser:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        transactions = Transaction.objects.all()

        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)

        total_balance = transactions.aggregate(Sum('amount'))['amount__sum'] or 0

        serializer = TransactionSerializer(transactions, many=True)
        return Response({
            'transactions': serializer.data,
            'total_balance': total_balance
        })
