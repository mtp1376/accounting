from django.db import models, transaction
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _

from AccountingApp.models.party import Party


class Contract(models.Model):
    """
    عقد
    """

    def check_validity(self):
        if hasattr(self, 'gharzolhasaneh'):
            self.gharzolhasaneh.check_validity()

    def initiate(self):
        with transaction.atomic():
            contract: Contract = Contract.objects.select_for_update().get(pk=self.pk)
            contract.check_validity()
            contract.state = Contract.StateChoices.IN_PROGRESS
            contract.save()

    class StateChoices(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        FINISHED = 'FINISHED', _('Finished')

    state = models.CharField(choices=StateChoices.choices, max_length=20, default=StateChoices.DRAFT)


class GharzolHasaneh(Contract):
    """
    عقد قرض‌الحسنه
    """

    lender = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='gharzes_given')
    taker = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='gharzes_taken')
    # asset = models.ForeignKey(Asset, on_delete=models.PROTECT) # design decision
    amount = models.PositiveIntegerField()

    def check_validity(self):
        if self.payments.aggregate(payments_sum=Sum('amount'))['payments_sum'] != self.amount:
            raise ValueError("Contract payments not done")
