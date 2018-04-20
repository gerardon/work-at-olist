from django.db import models
from django.urls import reverse_lazy


class Call(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    source = models.CharField(max_length=11)
    destination = models.CharField(max_length=11)


class CallRecord(models.Model):
    RECORD_TYPES = (
        ('start', 'Start'),
        ('end', 'End'),
    )
    id = models.PositiveIntegerField(primary_key=True)
    call = models.ForeignKey(Call, on_delete=True)
    record_type = models.CharField(max_length=5, choices=RECORD_TYPES)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('call', 'record_type')
