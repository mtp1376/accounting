from django.db import transaction
from django.test import TestCase

from AccountingApp.models import Account, Transaction


# Create your tests here.
class AccountTestCase(TestCase):
    def setUp(self):
        self.mohammad_account = Account.objects.create(name="Mohammad Teimori Pabandi wallet", balance=2_000_000)
        self.alireza_account = Account.objects.create(name="Alireza Ghanimati wallet", balance=5000)
        self.hamyanestan_cashbox_account = Account.objects.create(name="Hamyanestan Cashbox", balance=0)
        self.hazrat_zahra_cashbox_account = Account.objects.create(name="Hazrat Zahra Cashbox", balance=0)

    def test_non_balancing_entries(self):
        with transaction.atomic():
            t = Transaction.objects.create(
                description="Mohammad pays 1m to Hamyanestan, but Hamyanestan is getting 2m",
                status=Transaction.Status.IN_PROGRESS,
            )
            t.entries.create(
                account=self.mohammad_account,
                amount=-1_000_000,
                date="2023-12-06",
            )
            t.entries.create(
                account=self.hamyanestan_cashbox_account,
                amount=2_000_000,
                date="2023-12-06",
            )
            with self.assertRaises(ValueError) as commit_exception:
                t.commit()
            self.assertEqual(commit_exception.exception.args[0], "Transaction must be balanced")

    def test_cashbox_cashin(self):
        with transaction.atomic():
            t = Transaction.objects.create(
                description="Mohammad pays 1m to Hamyan cashbox",
                status=Transaction.Status.IN_PROGRESS,
            )
            t.entries.create(
                account=self.mohammad_account,
                amount=-1_000_000,
                date="2023-12-06",
            )
            t.entries.create(
                account=self.hamyanestan_cashbox_account,
                amount=1_000_000,
                date="2023-12-06",
            )
            t.commit()

        self.hamyanestan_cashbox_account.refresh_from_db()
        self.mohammad_account.refresh_from_db()

        self.assertEqual(self.hamyanestan_cashbox_account.balance, 1_000_000)
        self.assertEqual(self.mohammad_account.balance, 1_000_000)

    def test_multi_legged_cashbox_cashin(self):
        with transaction.atomic():
            t = Transaction.objects.create(
                description="Mohammad pays 1m to Hamyan and 1m to Hazrat Zahra cashboxes",
                status=Transaction.Status.IN_PROGRESS,
            )
            t.entries.create(
                account=self.mohammad_account,
                amount=-2_000_000,
                date="2023-12-06",
            )
            t.entries.create(
                account=self.hamyanestan_cashbox_account,
                amount=1_000_000,
                date="2023-12-06",
            )
            t.entries.create(
                account=self.hazrat_zahra_cashbox_account,
                amount=1_000_000,
                date="2023-12-06",
            )
            t.commit()

        self.hamyanestan_cashbox_account.refresh_from_db()
        self.hazrat_zahra_cashbox_account.refresh_from_db()
        self.mohammad_account.refresh_from_db()

        self.assertEqual(self.hamyanestan_cashbox_account.balance, 1_000_000)
        self.assertEqual(self.hazrat_zahra_cashbox_account.balance, 1_000_000)
        self.assertEqual(self.mohammad_account.balance, 0)

    def test_memo_account_no_balance_needed(self):
        hamyanestan_debts_memo_account = Account.objects.create(
            name="Hamyanestan Total Debt Memo Account",
            balance=0,
            is_memo=True,
        )
        with transaction.atomic():
            t = Transaction.objects.create(
                description="Mohammad pays 1m to Hamyanestan",
                status=Transaction.Status.IN_PROGRESS,
            )
            t.entries.create(
                account=self.mohammad_account,
                amount=-1_000_000,
                date="2023-12-06",
            )
            t.entries.create(
                account=self.hamyanestan_cashbox_account,
                amount=1_000_000,
                date="2023-12-06",
            )
            t.entries.create(
                account=hamyanestan_debts_memo_account,
                amount=1_000_000,
                date="2023-12-06",
            )
            t.commit()

        self.hamyanestan_cashbox_account.refresh_from_db()
        self.mohammad_account.refresh_from_db()
        hamyanestan_debts_memo_account.refresh_from_db()

        self.assertEqual(self.hamyanestan_cashbox_account.balance, 1_000_000)
        self.assertEqual(self.mohammad_account.balance, 1_000_000)
        self.assertEqual(hamyanestan_debts_memo_account.balance, 1_000_000)
