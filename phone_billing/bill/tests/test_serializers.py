from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from ...call.models import Call, CallRecord

from ..models import BillRecord
from ..serializers import BillRecordSerializer, BillSerializer, PhoneField


class BillRecordSerializerTestCase(TestCase):

    def setUp(self):
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='10123456789')

        end = timezone.now()
        start = end - timedelta(minutes=5)

        CallRecord.objects.create(id=1, record_type='start',
                                  timestamp=start, call=call)
        CallRecord.objects.create(id=2, record_type='end',
                                  timestamp=end, call=call)

        self.record = BillRecord.objects.get(call=call)

    def test_serializes_correctly(self):
        serializer = BillRecordSerializer(instance=self.record)
        data = serializer.data

        self.assertEquals(data['destination'], self.record.call.destination)
        self.assertEquals(data['call_start_date'],
                          self.record.call.started_at.strftime('%d/%m/%Y'))
        self.assertEquals(data['call_start_time'],
                          self.record.call.started_at.strftime('%H:%M:%S'))

        duration = self.record.call.duration.total_seconds()
        hours = str(int(duration // 3600)).zfill(2)
        minutes = str(int((duration // 60) % 60)).zfill(2)
        seconds = str(int(duration % 60)).zfill(2)
        string_duration = f'{hours}:{minutes}:{seconds}'
        self.assertEquals(data['call_duration'], string_duration)
        self.assertEquals(data['call_price'], str(self.record.price))

    def test_destination_custom_field(self):
        serializer = BillRecordSerializer(instance=self.record)

        self.assertIsInstance(serializer.fields['destination'], PhoneField)


class BillSerializerTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.last_month = self.now.replace(month=self.now.month - 1)
        self.subscriber = '00123456789'

        self.create_call_and_records(1, self.subscriber,
                                     '10123456789', self.now)
        self.create_call_and_records(2, self.subscriber,
                                     '10123456789', self.last_month)
        self.create_call_and_records(3, '10123456789',
                                     self.subscriber, self.now)

    def create_call_and_records(self, id, source, destination, timestamp):
        call = Call.objects.create(id=id, source=source,
                                   destination=destination)
        CallRecord.objects.create(id=id, record_type='end', call=call,
                                  timestamp=timestamp)
        BillRecord.objects.create(call=call, price=Decimal('1'))

    def test_subscriber_custom_field(self):
        serializer = BillSerializer(data={})

        self.assertIsInstance(serializer.fields['subscriber'], PhoneField)

    def test_required_fields(self):
        serializer = BillSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('subscriber', serializer.errors)

    def test_period_format(self):
        serializer = BillSerializer(data={
            'subscriber': self.subscriber,
            'period': self.now.strftime('%m-%Y')
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('period', serializer.errors)

        serializer = BillSerializer(data={
            'subscriber': self.subscriber,
            'period': self.now.strftime('%m/%Y')
        })

        self.assertTrue(serializer.is_valid())

    def test_get_default_period(self):
        serializer = BillSerializer(data={'subscriber': self.subscriber})
        self.assertTrue(serializer.is_valid())

        self.assertEquals(serializer.get_period(),
                          self.last_month.date())
        self.assertEquals(serializer.validated_data['period'],
                          self.last_month.date())

    def test_filter_calls_by_subscriber(self):
        serializer = BillSerializer(data={'subscriber': self.subscriber})

        self.assertTrue(serializer.is_valid())

        calls = serializer.filter_calls_by_subscriber()

        call_ids = calls.values_list('id', flat=True)
        self.assertIn(1, call_ids)
        self.assertIn(1, call_ids)
        self.assertNotIn(3, call_ids)

    def test_filter_calls_by_period_default(self):
        serializer = BillSerializer(data={'subscriber': self.subscriber})

        self.assertTrue(serializer.is_valid())

        calls = serializer.filter_calls_by_period(Call.objects.all())

        call_ids = calls.values_list('id', flat=True)
        self.assertNotIn(1, call_ids)
        self.assertIn(2, call_ids)
        self.assertNotIn(3, call_ids)

    def test_filter_calls_by_period(self):
        serializer = BillSerializer(data={
            'subscriber': self.subscriber, 'period': self.now.strftime('%m/%Y')
        })

        self.assertTrue(serializer.is_valid())

        calls = serializer.filter_calls_by_period(Call.objects.all())

        call_ids = calls.values_list('id', flat=True)
        self.assertIn(1, call_ids)
        self.assertNotIn(2, call_ids)
        self.assertIn(3, call_ids)

    @patch.object(BillSerializer, 'filter_calls_by_subscriber')
    @patch.object(BillSerializer, 'filter_calls_by_period')
    def test_filter_bill_records(self, period_filter, subscriber_filter):
        period_filter.return_value = Call.objects.filter(id=1)

        serializer = BillSerializer(data={'subscriber': self.subscriber})
        self.assertTrue(serializer.is_valid())

        records = serializer.filter_bill_records()

        record = records[0]
        self.assertIsInstance(record, BillRecord)
        self.assertEquals(record.call.id, 1)

        subscriber_filter.assert_called_once_with()
        period_filter.assert_called_once_with(subscriber_filter.return_value)

    @patch.object(BillSerializer, 'filter_bill_records')
    def test_search_bill_records(self, mocked_filter):
        records = BillRecord.objects.all()
        mocked_filter.return_value = records

        serializer = BillSerializer(data={'subscriber': self.subscriber})
        self.assertTrue(serializer.is_valid())

        serializer.search_bill_records()

        for record in records:
            self.assertIn(record, serializer.validated_data['bill_records'])
