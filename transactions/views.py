from datetime import datetime
from rest_framework import viewsets, permissions, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer, UserSerializer

def _calculate_balance(user):
    transactions = Transaction.objects.filter(user=user)
    user_balance = 0
    for t in transactions:
        if t.type == 1:
            user_balance += t.value
        else:
            user_balance -= t.value
    return user_balance

class UserViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'])
    def balance(self, request):
        user_balance = _calculate_balance(request.user)
        return Response(data={'balance': user_balance}, status=200)

class TransactionViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    startDate = None
    endDate = None

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user)

        if self.startDate is not None and self.endDate is not None:
            queryset = queryset.filter(
                created_at__range=(self.startDate, self.endDate))

        type = self.request.query_params.get('type')
        if type is not None:
            queryset = queryset.filter(type=type)

        merchant = self.request.query_params.get('merchant')
        if merchant is not None:
            queryset = queryset.filter(merchant=merchant)

        return queryset

    def list(self, request, *args, **kwargs):
        dtFrom = self.request.query_params.get('from')
        dtTo = self.request.query_params.get('to')

        if dtFrom and dtTo is None or dtTo and dtFrom is None:
            return Response(
                data={'error': 'you must define both \'from\' and \'to\' parameters'},
                status=400)

        if dtFrom and dtTo:
            startDate = datetime.strptime(dtFrom, '%Y-%m-%d').date()
            endDate = datetime.strptime(dtTo, '%Y-%m-%d').date()

            if startDate > endDate:
                return Response(
                    data={'error': '\'from\' parameter is ahead of \'to\''},
                    status=400)

            self.startDate = startDate
            self.endDate = endDate

        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        #TODO Validate request.data
        type = request.data.get('type')
        if type != Transaction.TransactionTypes.DEPOSIT:
            oldBalance = _calculate_balance(request.user)
            newBalance = oldBalance - request.data.get('value')
            if newBalance < 0:
                return Response(
                    data={'error': 'insufficient balance'}, status=400)

        merchant = request.data.get('merchant', None)
        if merchant is None and type == Transaction.TransactionTypes.EXPENSE:
            return Response(
                data={'error': 'merchant can\'t be null'}, status=400)

        request.data.update({'user': request.user})
        return super().create(request, *args, **kwargs)
