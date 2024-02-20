from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from AccountingApp.models import Pocket, PocketPurpose
from AccountingApp.models.contract import GharzolHasaneh
from AccountingApp.models.debt import Debt
from AccountingApp.models.money_movement import ContractPayment, DebtRepayment
from AccountingApp.models.party import Person


class TestSandogh(TestCase):
    # fixtures = ['PocketPurpose.json'] # TODO

    def test_give_loan(self):
        # 1. Parties and Pockets
        box_owner = Person.objects.create(name='محمد تیموری پابندی')
        box_pocket = Pocket.objects.create(
            owner=box_owner,
            purpose=PocketPurpose.objects.get_or_create(name='BOX')[0],
            balance=1_500_000,  # TODO: properly charge balance instead of this
        )

        taker = Person.objects.create(name='امیر زنگنه')
        taker_pocket = Pocket.objects.create(
            owner=taker,
            purpose=PocketPurpose.objects.get_or_create(name='WALLET')[0],
            balance=0,
        )

        # 2. Contract
        gharzol_hasaneh = GharzolHasaneh.objects.create(
            lender=box_owner,
            taker=taker,
            amount=1_000_000
        )

        # 3. Debts
        installment_1 = Debt.objects.create(
            type=Debt.TypeChoices.WITH_DUE,
            due_date=timezone.now() + timedelta(days=10),
            contract=gharzol_hasaneh,
            state=Debt.StateChoices.NOT_DUE,
            amount=500_000,
            paid_amount=0,
        )
        installment_2 = Debt.objects.create(
            type=Debt.TypeChoices.WITH_DUE,
            due_date=timezone.now() + timedelta(days=20),
            contract=gharzol_hasaneh,
            state=Debt.StateChoices.NOT_DUE,
            amount=500_000,
            paid_amount=0,
        )

        # 4. Money movement
        loan_giving_payment = ContractPayment.objects.create(
            contract=gharzol_hasaneh,
            from_pocket=box_pocket,
            to_pocket=taker_pocket,
            amount=1_000_000,
        )
        loan_giving_payment.commit()

        # now pay the debt
        repayment_1 = DebtRepayment.objects.create(
            amount=450_000,
            from_pocket=taker_pocket,
            to_pocket=box_pocket,
            debt=installment_1,
        )
        repayment_1.commit()

        print(
            'yo'
        )