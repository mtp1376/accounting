from django.db import models, transaction

from AccountingApp.choices import MoneyMovementStateChoices
from AccountingApp.models.contract import Contract
from AccountingApp.models.debt import Debt
from AccountingApp.models.pocket import Pocket


class MoneyMovement(models.Model):
    amount = models.PositiveIntegerField()
    from_pocket = models.ForeignKey(Pocket, on_delete=models.PROTECT, related_name='money_outgoing')
    to_pocket = models.ForeignKey(Pocket, on_delete=models.PROTECT, related_name='money_incoming')
    state = models.CharField(
        max_length=20, choices=MoneyMovementStateChoices.choices, default=MoneyMovementStateChoices.DRAFT
    )

    def commit(self):
        with transaction.atomic():
            movement: MoneyMovement = MoneyMovement.objects.select_for_update().get(pk=self.pk)

            movement.state = MoneyMovementStateChoices.COMMITTED
            movement.save()

            movement.from_pocket.discharge_amount(self.amount)
            movement.to_pocket.charge_amount(self.amount)


class ContractPayment(MoneyMovement):
    """
    پرداخت اولیه‌ی عقد که باعث جاری‌شدن اون عقد می‌شه
    """
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
