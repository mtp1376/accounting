from django.db import models


class MoneyLocation(models.Model):
    name = ''


class PaymentGateway(MoneyLocation):
    # money flowing into the system
    ...


class Moneypool(MoneyLocation):
    ...


class UserWallet(MoneyLocation):
    ...


class Bank(MoneyLocation):
    # money flowing out of the system
    ...

