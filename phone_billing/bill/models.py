from django.db import models

from ..call.models import Call

from .pricing import calculate_call_charge


class BillRecordManager(models.Manager):

    def create_for_call(self, call):
        return self.create(
            call_id=call.id,
            price=calculate_call_charge(call.started_at, call.ended_at)
        )


class BillRecord(models.Model):
    objects = BillRecordManager()

    call = models.ForeignKey(Call, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
