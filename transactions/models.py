from django.db import models

# Transaction Model
class Transaction(models.Model):
    class TransactionTypes(models.IntegerChoices):
        DEPOSIT = 1
        WITHDRAW = 2
        EXPENSE = 3

    type = models.IntegerField(choices=TransactionTypes.choices)
    value = models.PositiveBigIntegerField()
    merchant = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.IntegerField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return "transaction_id_" + str(self.id)
