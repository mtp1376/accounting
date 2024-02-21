# noinspection NonAsciiCharacters

from django.db import models, transaction

from AccountingApp.models.party import Party


class PocketPurpose(models.Model):
    name = models.CharField(max_length=30)
    # TODO: add box identifier here


class Pocket(models.Model):
    """
    جیب
    """

    class Meta:
        unique_together = (('owner', 'purpose'),)

    owner = models.ForeignKey(Party, on_delete=models.PROTECT)
    purpose = models.ForeignKey(PocketPurpose, on_delete=models.RESTRICT)
    balance = models.PositiveIntegerField()

    def discharge_amount(self, amount):
        if amount < 0:
            raise ValueError("Can't discharge less than 0")

        with transaction.atomic():
            pocket: Pocket = Pocket.objects.select_for_update().get(pk=self.pk)
            pocket.balance -= amount
            # TODO: balance should not become negative
            pocket.save()

    def charge_amount(self, amount):
        if amount < 0:
            raise ValueError("Can't charge less than 0")

        with transaction.atomic():
            pocket: Pocket = Pocket.objects.select_for_update().get(pk=self.pk)
            pocket.balance += amount
            pocket.save()
