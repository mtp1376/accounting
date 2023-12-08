from django.db import models, transaction
from django.db.models import F


class Account(models.Model):
    name = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    is_memo = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMMITTED = "COMMITTED", "Committed"
        FAILED = "FAILED", "Failed"

    description = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)

    def commit(self):
        if self.status != Transaction.Status.IN_PROGRESS:
            raise ValueError("Transaction is not in progress")
        if self.entries.filter(account__is_memo=False).aggregate(models.Sum('amount'))['amount__sum'] != 0:
            raise ValueError("Transaction must be balanced")
        with transaction.atomic():
            for entry in self.entries.all():
                entry.account = Account.objects.select_for_update().get(pk=entry.account.pk)
                entry.account.balance = F('balance') + entry.amount
                entry.account.save()
            self.status = Transaction.Status.COMMITTED
            self.save()

    def __str__(self):
        return f"{self.entries.all()} - {self.description}"


class Entry(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='entries')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='entries')

    def __str__(self):
        return f"{self.account} - {self.amount} - {self.date}"
