from django.db import models

from ..call.models import Call


class BillRecord(models.Model):
    call = models.ForeignKey(Call, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
