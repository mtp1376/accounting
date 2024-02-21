from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from AccountingApp.choices import ContractStateChoices, DebtTypeChoices, DebtStateChoices
from AccountingApp.models import Pocket, PocketPurpose
from AccountingApp.models.contract import GharzolHasaneh
from AccountingApp.models.debt import Debt
from AccountingApp.models.money_movement import ContractPayment, DebtRepayment
from AccountingApp.models.party import Person


class TestGiveLoan(TestCase):
    # fixtures = ['PocketPurpose.json'] # TODO

    def setUp(self):
        # 1. Parties and Pockets
        self.box_owner = Person.objects.create(name='محمد تیموری پابندی')
        self.box_pocket = Pocket.objects.create(
            owner=self.box_owner,
            purpose=PocketPurpose.objects.get_or_create(name='BOX')[0],
            balance=1_500_000,  # TODO: properly charge balance instead of this
        )

        self.taker = Person.objects.create(name='امیر زنگنه')
        self.taker_pocket = Pocket.objects.create(
            owner=self.taker,
            purpose=PocketPurpose.objects.get_or_create(name='WALLET')[0],
            balance=0,
        )

        # 2. Contract
        self.gharzol_hasaneh_contract = GharzolHasaneh.objects.create(
            lender=self.box_owner,
            taker=self.taker,
            amount=1_000_000
        )

        # 3. Debts
        self.installment_1 = Debt.objects.create(
            type=DebtTypeChoices.WITH_DUE,
            due_date=timezone.now() + timedelta(days=10),
            contract=self.gharzol_hasaneh_contract,
            state=DebtStateChoices.NOT_DUE,
            amount=500_000,
            paid_amount=0,
        )
        self.installment_2 = Debt.objects.create(
            type=DebtTypeChoices.WITH_DUE,
            due_date=timezone.now() + timedelta(days=20),
            contract=self.gharzol_hasaneh_contract,
            state=DebtStateChoices.NOT_DUE,
            amount=500_000,
            paid_amount=0,
        )

        # 4. Money movement
        self.loan_giving_payment = ContractPayment.objects.create(
            contract=self.gharzol_hasaneh_contract,
            from_pocket=self.box_pocket,
            to_pocket=self.taker_pocket,
            amount=1_000_000,
        )
        self.loan_giving_payment.commit()

    def test_give_loan(self):
        # check outcomes
        # o1. contract state
        self.gharzol_hasaneh_contract.refresh_from_db()
        self.assertEquals(self.gharzol_hasaneh_contract.state, ContractStateChoices.IN_PROGRESS)

        # o2. money movement
        self.box_pocket.refresh_from_db()
        self.taker_pocket.refresh_from_db()
        self.assertEquals(self.box_pocket.balance, 500_000)
        self.assertEquals(self.taker_pocket.balance, 1_000_000)

        # o3. debts
        self.installment_1.refresh_from_db()
        self.installment_2.refresh_from_db()
        self.assertEquals(self.installment_1.state, DebtStateChoices.NOT_DUE)
        self.assertEquals(self.installment_2.state, DebtStateChoices.NOT_DUE)

    def test_give_loan_and_pay_one_installment_in_full(self):
        # pay the debt
        self.repayment_1 = DebtRepayment.objects.create(
            amount=500_000,
            from_pocket=self.taker_pocket,
            to_pocket=self.box_pocket,
            debt=self.installment_1,
        )
        self.repayment_1.commit()

        # check outcomes
        # o1. contract state
        self.gharzol_hasaneh_contract.refresh_from_db()
        self.assertEquals(self.gharzol_hasaneh_contract.state, ContractStateChoices.IN_PROGRESS)

        # o2. money movement
        self.box_pocket.refresh_from_db()
        self.taker_pocket.refresh_from_db()
        self.assertEquals(self.box_pocket.balance, 1_000_000)
        self.assertEquals(self.taker_pocket.balance, 500_000)

        # o3. debts
        self.installment_1.refresh_from_db()
        self.installment_2.refresh_from_db()
        self.assertEquals(self.installment_1.state, DebtStateChoices.PAID)
        self.assertEquals(self.installment_2.state, DebtStateChoices.NOT_DUE)

    def test_give_loan_and_pay_one_installment_partially(self):
        # pay the debt
        self.repayment_1 = DebtRepayment.objects.create(
            amount=450_000,
            from_pocket=self.taker_pocket,
            to_pocket=self.box_pocket,
            debt=self.installment_1,
        )
        self.repayment_1.commit()

        # check outcomes
        # o1. contract state
        self.gharzol_hasaneh_contract.refresh_from_db()
        self.assertEquals(self.gharzol_hasaneh_contract.state, ContractStateChoices.IN_PROGRESS)

        # o2. money movement
        self.box_pocket.refresh_from_db()
        self.taker_pocket.refresh_from_db()
        self.assertEquals(self.box_pocket.balance, 950_000)
        self.assertEquals(self.taker_pocket.balance, 550_000)

        # o3. debts
        self.installment_1.refresh_from_db()
        self.installment_2.refresh_from_db()
        self.assertEquals(self.installment_1.state, DebtStateChoices.NOT_DUE)
        self.assertEquals(self.installment_2.state, DebtStateChoices.NOT_DUE)

    def test_give_loan_and_pay_all_installments_in_full(self):
        # pay the debt
        self.repayment_1 = DebtRepayment.objects.create(
            amount=500_000,
            from_pocket=self.taker_pocket,
            to_pocket=self.box_pocket,
            debt=self.installment_1,
        )
        self.repayment_1.commit()
        self.repayment_2 = DebtRepayment.objects.create(
            amount=500_000,
            from_pocket=self.taker_pocket,
            to_pocket=self.box_pocket,
            debt=self.installment_2,
        )
        self.repayment_2.commit()

        # check outcomes
        # o1. contract state
        self.gharzol_hasaneh_contract.refresh_from_db()
        self.assertEquals(self.gharzol_hasaneh_contract.state, ContractStateChoices.FINISHED)

        # o2. money movement
        self.box_pocket.refresh_from_db()
        self.taker_pocket.refresh_from_db()
        self.assertEquals(self.box_pocket.balance, 1_500_000)
        self.assertEquals(self.taker_pocket.balance, 0)

        # o3. debts
        self.installment_1.refresh_from_db()
        self.installment_2.refresh_from_db()
        self.assertEquals(self.installment_1.state, DebtStateChoices.PAID)
        self.assertEquals(self.installment_2.state, DebtStateChoices.PAID)

    def test_give_loan_and_pay_one_installment_in_full_by_someone_else(self):
        payer = Person.objects.create(name='حسین افتخاری')  # نسل اندر نسل سفره‌دار
        payer_pocket = Pocket.objects.create(
            owner=payer,
            purpose=PocketPurpose.objects.get_or_create(name='WALLET')[0],
            balance=500_000,  # از محل کلاهبرداری
        )

        # pay the debt
        self.repayment_1 = DebtRepayment.objects.create(
            amount=500_000,
            from_pocket=payer_pocket,
            to_pocket=self.box_pocket,
            debt=self.installment_1,
        )
        self.repayment_1.commit()

        # check outcomes
        # o1. contract state
        self.gharzol_hasaneh_contract.refresh_from_db()
        self.assertEquals(self.gharzol_hasaneh_contract.state, ContractStateChoices.IN_PROGRESS)

        # o2. money movement
        self.box_pocket.refresh_from_db()
        self.taker_pocket.refresh_from_db()
        payer_pocket.refresh_from_db()
        self.assertEquals(self.box_pocket.balance, 1_000_000)
        self.assertEquals(self.taker_pocket.balance, 1_000_000)
        self.assertEquals(payer_pocket.balance, 0)

        # o3. debts
        self.installment_1.refresh_from_db()
        self.installment_2.refresh_from_db()
        self.assertEquals(self.installment_1.state, DebtStateChoices.PAID)
        self.assertEquals(self.installment_2.state, DebtStateChoices.NOT_DUE)
