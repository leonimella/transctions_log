from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields= ['id', 'type', 'value', 'merchant', 'created_at', 'updated_at']
