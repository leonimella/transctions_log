from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets
from rest_framework import permissions
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.AllowAny]
