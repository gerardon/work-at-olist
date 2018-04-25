from .models import BillRecord


def bill_call_record(instance):
    if (instance.call.start_record and instance.call.end_record):
        BillRecord.objects.create_for_call(instance.call)
