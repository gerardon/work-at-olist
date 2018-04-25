from django.db import models
from django.urls import reverse_lazy


class Call(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    source = models.CharField(max_length=11)
    destination = models.CharField(max_length=11)

    @property
    def started_at(self):
        if self.start_record:
            return self.start_record.timestamp

    @property
    def ended_at(self):
        if self.end_record:
            return self.end_record.timestamp

    @property
    def start_record(self):
        return self.records.filter(record_type='start').last()

    @property
    def end_record(self):
        return self.records.filter(record_type='end').last()


class CallRecord(models.Model):
    RECORD_TYPES = (
        ('start', 'Start'),
        ('end', 'End'),
    )
    id = models.PositiveIntegerField(primary_key=True)
    call = models.ForeignKey(Call, on_delete=True, related_name='records')
    record_type = models.CharField(max_length=5, choices=RECORD_TYPES)
    timestamp = models.DateTimeField()

    class Meta:
        unique_together = ('call', 'record_type')
