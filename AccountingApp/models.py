from django.db import models




class Transaction(models.Model):
    source = models.ForeignKey(MoneyLocation, on_delete=models.PROTECT, related_name='outgoing_transactions')
    destination = models.ForeignKey(MoneyLocation, on_delete=models.PROTECT, related_name='incoming_transactions')


class TransactionReason(models.Model):
    class Meta:
        abstract = True
