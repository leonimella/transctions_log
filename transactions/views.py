from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.AllowAny]

    # def get_queryset(self):
    #     return Transaction.objects.get(user=1)

    def create(self, request, *args, **kwargs):
        type = request.data.get('type')
        if type != Transaction.TransactionTypes.DEPOSIT:
            old_balance = self._calculate_balance()
            new_balance = old_balance - request.data.get('value')
            if new_balance < 0:
                return Response(data={'error': 'insufficient balance'}, status=400)


        merchant = request.data.get('merchant', None)
        if merchant is None and type == Transaction.TransactionTypes.EXPENSE:
            return Response(data={'error': 'merchant can\'t be null'}, status=400)

        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def user_balance(self, request):
        user_balance = self._calculate_balance()
        return Response(data={'balance': user_balance}, status=200)

    def _calculate_balance(transactions=None):
        # TODO add real user
        transactions = Transaction.objects.filter(user=1)
        user_balance = 0
        for t in transactions:
            if t.type == 1:
                user_balance += t.value
            else:
                user_balance -= t.value
        return user_balance
