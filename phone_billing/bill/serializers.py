from datetime import timedelta
from rest_framework import serializers

from django.utils import timezone

from ..call.models import Call, CallRecord
from ..call.serializers import PhoneField

from .models import BillRecord


class BillRecordSerializer(serializers.ModelSerializer):
    destination = PhoneField(source='call.destination')
    call_start_date = serializers.DateTimeField(source='call.started_at',
                                                format='%d/%m/%Y')
    call_start_time = serializers.DateTimeField(source='call.started_at',
                                                format='%H:%M:%S')
    call_duration = serializers.DurationField(source='call.duration')
    call_price = serializers.DecimalField(source='price', max_digits=10,
                                          decimal_places=2)

    class Meta:
        model = BillRecord
        fields = ('id', 'destination', 'call_start_date', 'call_start_time',
                  'call_duration', 'call_price')


class BillSerializer(serializers.Serializer):
    subscriber = PhoneField()
    period = serializers.DateField(format='%m/%Y', input_formats=['%m/%Y'],
                                   required=False)
    bill_records = BillRecordSerializer(many=True, read_only=True)

    def filter_calls_by_subscriber(self):
        return Call.objects.filter(source=self.validated_data['subscriber'])

    def get_period(self):
        if not self.validated_data.get('period'):
            today = timezone.now().date()
            last_month = today.replace(month=today.month - 1)
            self.validated_data['period'] = last_month

        return self.validated_data['period']

    def filter_calls_by_period(self, calls):
        period = self.get_period()
        return CallRecord.objects.filter(
            record_type='end', timestamp__month=period.month,
            timestamp__year=period.year, call__in=calls
        ).values_list('call', flat=True)

    def filter_bill_records(self):
        calls = self.filter_calls_by_subscriber()
        calls = self.filter_calls_by_period(calls)

        return BillRecord.objects.filter(call__in=calls)

    def search_bill_records(self):
        records = self.filter_bill_records()
        self.validated_data['bill_records'] = records
