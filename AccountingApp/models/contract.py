from django.db import models, transaction
from django.db.models import Sum

from AccountingApp.choices import ContractStateChoices, DebtStateChoices
from AccountingApp.models.party import Party


class Contract(models.Model):
    """
    عقد
    """

    state = models.CharField(choices=ContractStateChoices.choices, max_length=20, default=ContractStateChoices.DRAFT)

    def check_validity(self):
        if hasattr(self, 'gharzolhasaneh'):
            self.gharzolhasaneh.check_validity()

    def initiate(self):
        with transaction.atomic():
            contract: Contract = Contract.objects.select_for_update().get(pk=self.pk)
            contract.check_validity()
            contract.state = ContractStateChoices.IN_PROGRESS
            contract.save()

    def signal_debt_repayment(self):
        if hasattr(self, 'gharzolhasaneh'):
            self.gharzolhasaneh.signal_debt_repayment()


class GharzolHasaneh(Contract):
    """
    عقد قرض‌الحسنه
    مُقرِض
    مُقتَرِض
    """

    lender = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='gharzes_given')
    taker = models.ForeignKey(Party, on_delete=models.PROTECT, related_name='gharzes_taken')
    # asset = models.ForeignKey(Asset, on_delete=models.PROTECT) # design decision
    amount = models.PositiveIntegerField()

    def check_validity(self):
        if self.payments.aggregate(payments_sum=Sum('amount'))['payments_sum'] != self.amount:
            raise ValueError("Contract payments not done")

    def _is_finished(self):
        return not self.resulting_debts.exclude(state=DebtStateChoices.PAID).exists()

    def signal_debt_repayment(self):
        if self._is_finished():
            self.state = ContractStateChoices.FINISHED
            self.save(update_fields=['state'])
