from django.db import models

# Transaction Model
class Transaction(models.Model):
    class TransactionTypes(models.IntegerChoices):
        DEPOSIT = 1
        WITHDRAW = 2
        EXPENSE = 3

    type = models.IntegerField(choices=TransactionTypes.choices)
    value = models.PositiveBigIntegerField()
    merchant = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "id " + str(self.id)
