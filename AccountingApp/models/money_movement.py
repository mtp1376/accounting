from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from AccountingApp.models.pocket import Pocket
from AccountingApp.models.contract import Contract
from AccountingApp.models.debt import Debt


class MoneyMovement(models.Model):
    class StateChoices(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMMITTED = 'COMMITTED', _('Committed')

    amount = models.PositiveIntegerField()
    from_pocket = models.ForeignKey(Pocket, on_delete=models.PROTECT, related_name='money_outgoing')
    to_pocket = models.ForeignKey(Pocket, on_delete=models.PROTECT, related_name='money_incoming')
    state = models.CharField(max_length=20, choices=StateChoices.choices, default=StateChoices.DRAFT)

    def commit(self):
        with transaction.atomic():
            movement: MoneyMovement = MoneyMovement.objects.select_for_update().get(pk=self.pk)

            movement.state = MoneyMovement.StateChoices.COMMITTED
            movement.save()

            movement.from_pocket.discharge_amount(self.amount)
            movement.to_pocket.charge_amount(self.amount)


class ContractPayment(MoneyMovement):
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, related_name='payments')

    def commit(self):
        with transaction.atomic():
            contract = Contract.objects.select_for_update().get(pk=self.contract.pk)
            contract.initiate()

            super().commit()


class DebtRepayment(MoneyMovement):
    debt = models.ForeignKey(Debt, on_delete=models.PROTECT, related_name='repayments')

    def commit(self):
        with transaction.atomic():
            debt: Debt = Debt.objects.select_for_update().get(pk=self.debt.pk)
            debt.charge_paid_amount(self.amount)

            super().commit()
