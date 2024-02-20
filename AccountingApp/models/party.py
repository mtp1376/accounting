from uuid import uuid4

from django.db import models


class Party(models.Model):
    """
    طرف حساب
    """
    uuid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=40)


class Person(Party):
    """
    شخص؛ مثل محمد تیموری و امیر زنگنه
    """
    pass


class Entity(Party):
    """
    شرکت؛ مثل همیان و بانک پاسارگاد
    """
    pass
