from django.db import models
from django.utils.translation import gettext_lazy as _


class ContractStateChoices(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    FINISHED = 'FINISHED', _('Finished')


class DebtTypeChoices(models.TextChoices):
    WITH_DUE = 'WITH_DUE', _('With Due')
    WITHOUT_DUE = 'WITHOUT_DUE', _('With Due')


class DebtStateChoices(models.TextChoices):
    NOT_DUE = 'NOT_DUE', _('Not Due')
    DUE = 'DUE', _('Due')
    PAID = 'PAID', _('PAID')


class MoneyMovementStateChoices(models.TextChoices):
    DRAFT = 'DRAFT', _('Draft')
    IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
    COMMITTED = 'COMMITTED', _('Committed')
