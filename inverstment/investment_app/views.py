from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import InvestmentAccount, Transaction
from .serializers import InvestmentAccountSerializer, TransactionSerializer
from .permissions import IsViewUser, IsPostOnlyUser, IsCRUDUser
from django.utils.dateparse import parse_date

class InvestmentAccountViewSet(viewsets.ModelViewSet):
    queryset = InvestmentAccount.objects.all()
    serializer_class = InvestmentAccountSerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PATCH', 'DELETE']:
            self.permission_classes = [IsCRUDUser]
        elif self.request.method == 'GET':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsPostOnlyUser]
        elif self.request.method == 'GET':
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='admin-list')
    def admin_list(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        try:
            if start_date:
                start_date = parse_date(start_date)
            if end_date:
                end_date = parse_date(end_date)
        except ValueError:
            return Response({"detail": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)
        
        transactions = self.queryset
        if start_date and end_date:
            transactions = transactions.filter(date__range=[start_date, end_date])
        
        serializer = self.get_serializer(transactions, many=True)
        total_balance = sum(tx.amount for tx in transactions)
        return Response({
            'transactions': serializer.data,
            'total_balance': total_balance
        })
