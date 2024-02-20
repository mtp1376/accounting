from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from AccountingApp.models.contract import Contract


class Debt(models.Model):
    """
    دین: مثل بدهی ناشی از گرفتن قرض‌الحسنه
    مؤجل و بدون أجل می‌تونه باشه
    """

    class TypeChoices(models.TextChoices):
        WITH_DUE = 'WITH_DUE', _('With Due')
        WITHOUT_DUE = 'WITHOUT_DUE', _('With Due')

    class StateChoices(models.TextChoices):
        NOT_DUE = 'NOT_DUE', _('Not Due')
        DUE = 'DUE', _('Due')
        PAID = 'PAID', _('PAID')

    # TODO: design decision whether have debter and debtee here? -- I believe they should be here

    type = models.CharField(max_length=20, choices=TypeChoices.choices)
    due_date = models.DateField(null=True, blank=True)
    contract = models.ForeignKey(Contract, related_name='resulting_debts', on_delete=models.PROTECT)
    state = models.CharField(max_length=20, choices=StateChoices.choices, default=StateChoices.NOT_DUE)
    amount = models.PositiveIntegerField()
    paid_amount = models.PositiveIntegerField(default=0)

    @staticmethod
    def _find_state(amount, paid_amount, due_date):
        if amount == paid_amount:
            return Debt.StateChoices.PAID
        if due_date < timezone.now().date():
            return Debt.StateChoices.DUE
        return Debt.StateChoices.NOT_DUE

    def charge_paid_amount(self, amount):
        with transaction.atomic():
            debt: Debt = Debt.objects.select_for_update().get(pk=self.pk)
            debt.paid_amount += amount
            if debt.paid_amount > debt.amount:
                raise ValueError("Can't pay more than debt amount")

            debt.state = Debt._find_state(debt.amount, debt.paid_amount, debt.due_date)
            debt.save()
