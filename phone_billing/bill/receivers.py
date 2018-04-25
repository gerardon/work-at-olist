from django.db.models.signals import post_save
from django.dispatch import receiver

from ..call.models import CallRecord

from .models import BillRecord


@receiver(post_save, sender=CallRecord)
def bill_call_record(sender, **kwargs):
    instance = kwargs['instance']

    if (kwargs['created']
            and instance.call.start_record
            and instance.call.end_record):
        BillRecord.objects.create_for_call(instance.call)
