from django.db import models
from django.contrib.auth.models import User as DjangoUser

# User
# Inherited from base user just for possible overrides
class User(DjangoUser):
    def __str__(self):
        return self.username

# Transaction
class Transaction(models.Model):
    class TransactionTypes(models.IntegerChoices):
        DEPOSIT = 1
        WITHDRAW = 2
        EXPENSE = 3

    type = models.IntegerField(choices=TransactionTypes.choices)
    value = models.PositiveBigIntegerField()
    merchant = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return "transaction_id_" + str(self.id)
