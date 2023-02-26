from datetime import datetime
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer, UserSerializer

class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class TransactionViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    API endpoint that allows for transactions handling.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    start_date = None
    end_date = None

    def get_queryset(self):
        queryset = Transaction.objects.all()

        if self.start_date is not None and self.end_date is not None:
            queryset = queryset.filter(
                created_at__range=(self.start_date, self.end_date))

        type = self.request.query_params.get('type')
        if type is not None:
            queryset = queryset.filter(type=type)

        merchant = self.request.query_params.get('merchant')
        if merchant is not None:
            queryset = queryset.filter(merchant=merchant)

        return queryset

    def list(self, request, *args, **kwargs):
        dtFrom = self.request.query_params.get('from', None)
        dtTo = self.request.query_params.get('to', None)

        if dtFrom and dtTo is None or dtTo and dtFrom is None:
            return Response(
                data={'error': 'you must define both \'from\' and \'to\' parameters'},
                status=400)

        if dtFrom and dtTo:
            start_date = datetime.strptime(dtFrom, '%Y-%m-%dT%H:%M:%S')
            end_date = datetime.strptime(dtTo, '%Y-%m-%dT%H:%M:%S')

            if start_date > end_date:
                return Response(
                    data={'error': '\'from\' parameter is ahead of \'to\''},
                    status=400)

            self.start_date = start_date
            self.end_date = end_date

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        type = request.data.get('type')
        if type != Transaction.TransactionTypes.DEPOSIT:
            old_balance = self._calculate_balance()
            new_balance = old_balance - request.data.get('value')
            if new_balance < 0:
                return Response(
                    data={'error': 'insufficient balance'}, status=400)


        merchant = request.data.get('merchant', None)
        if merchant is None and type == Transaction.TransactionTypes.EXPENSE:
            return Response(
                data={'error': 'merchant can\'t be null'}, status=400)

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def user_balance(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user.id)
        user_balance = self._calculate_balance(transactions)
        return Response(data={'balance': user_balance}, status=200)

    def _calculate_balance(self, transactions):
        user_balance = 0
        for t in transactions:
            if t.type == 1:
                user_balance += t.value
            else:
                user_balance -= t.value
        return user_balance
