from datetime import timedelta
from unittest.mock import patch

from django.db.utils import IntegrityError, DataError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Call, CallRecord


class CallModelTestCase(TestCase):

    def test_valid_call(self):
        call = Call(id=1, source='00123456789', destination='00123456789')

        call.save()

        call.refresh_from_db()
        self.assertEqual(call.id, 1)
        self.assertEqual(call.source, '00123456789')
        self.assertEqual(call.destination, '00123456789')

    def test_call_id_requires_declaration(self):
        call = Call(source='00123456789', destination='00123456789')

        with self.assertRaises(IntegrityError):
            call.save()

    def test_call_source_max_length(self):
        call = Call(id=1, source='1098765432100', destination='00123456789')

        with self.assertRaises(DataError):
            call.save()

    def test_call_destination_max_length(self):
        call = Call(id=1, source='00123456789', destination='1098765432100')

        with self.assertRaises(DataError):
            call.save()

    def test_start_record_property(self):
        now = timezone.now()
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')
        record = CallRecord.objects.create(id=1, call=call,
                                           record_type='start', timestamp=now)

        CallRecord.objects.create(id=2, call=call,
                                  record_type='end',
                                  timestamp=now)

        self.assertEquals(call.start_record.id, record.id)

    def test_end_record_property(self):
        now = timezone.now()
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')

        CallRecord.objects.create(id=1, call=call,
                                  record_type='start', timestamp=now)
        record = CallRecord.objects.create(id=2, call=call,
                                           record_type='end',
                                           timestamp=now)

        self.assertEquals(call.end_record.id, record.id)

    def test_start_record_property_if_missing_record(self):
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')

        self.assertIsNone(call.start_record)

    def test_end_record_property_if_missing_record(self):
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')

        self.assertIsNone(call.end_record)

    def test_started_at_property(self):
        end_stamp = timezone.now()
        start_stamp = end_stamp - timedelta(minutes=5)

        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')
        CallRecord.objects.create(id=1, call=call,
                                  record_type='start',
                                  timestamp=start_stamp)
        CallRecord.objects.create(id=2, call=call,
                                  record_type='end',
                                  timestamp=end_stamp)

        self.assertEquals(call.started_at, start_stamp)

    def test_ended_at_property(self):
        end_stamp = timezone.now()
        start_stamp = end_stamp - timedelta(minutes=5)

        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')
        CallRecord.objects.create(id=1, call=call,
                                  record_type='start',
                                  timestamp=start_stamp)
        CallRecord.objects.create(id=2, call=call,
                                  record_type='end',
                                  timestamp=end_stamp)

        self.assertEquals(call.ended_at, end_stamp)

    def test_started_at_property_if_missing_record(self):
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')

        self.assertIsNone(call.started_at)

    def test_ended_at_property_if_missing_record(self):
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')

        self.assertIsNone(call.ended_at)

    def test_duration_property(self):
        duration = timedelta(minutes=5)
        end_stamp = timezone.now()
        start_stamp = end_stamp - duration

        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')
        CallRecord.objects.create(id=1, call=call,
                                  record_type='start',
                                  timestamp=start_stamp)
        CallRecord.objects.create(id=2, call=call,
                                  record_type='end',
                                  timestamp=end_stamp)

        self.assertEquals(call.duration, duration)

    def test_duration_property_if_missing_end_record(self):
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')
        CallRecord.objects.create(id=1, call=call,
                                  record_type='start',
                                  timestamp=timezone.now())

        self.assertIsNone(call.duration)

    def test_duration_property_if_missing_start_record(self):
        call = Call.objects.create(id=1, source='00123456789',
                                   destination='00123456789')
        CallRecord.objects.create(id=2, call=call,
                                  record_type='end',
                                  timestamp=timezone.now())

        self.assertIsNone(call.duration)


class CallRecordModelTestCase(TestCase):

    def setUp(self):
        self.call = Call.objects.create(id=1,
                                        source='00123456789',
                                        destination='00123456789')
        self.now = timezone.now()

    def test_valid_record(self):
        record = CallRecord(id=1,
                            call=self.call,
                            record_type='start',
                            timestamp=self.now)

        record.save()

        record.refresh_from_db()
        self.assertEquals(record.id, 1)
        self.assertEquals(record.call, self.call)
        self.assertEquals(record.record_type, 'start')
        self.assertEquals(record.timestamp, self.now)

    def test_record_id_requires_declaration(self):
        record = CallRecord(call=self.call,
                            record_type='start',
                            timestamp=self.now)

        with self.assertRaises(IntegrityError):
            record.save()

    def test_record_must_have_a_call_related(self):
        record = CallRecord(id=1,
                            record_type='start',
                            timestamp=self.now)

        with self.assertRaises(IntegrityError):
            record.save()

    def test_record_record_type_max_length(self):
        record = CallRecord(id=1,
                            call=self.call,
                            record_type='toolong',
                            timestamp=self.now)

        with self.assertRaises(DataError):
            record.save()

    def test_record_timestamp_is_required(self):
        record = CallRecord(id=1,
                            call=self.call,
                            record_type='start')

        with self.assertRaises(IntegrityError):
            record.save()

    def test_record_type_and_call_unique_together(self):
        record = CallRecord(id=1,
                            call=self.call,
                            record_type='start',
                            timestamp=self.now)
        record.save()

        other_record = CallRecord(id=2,
                                  call=self.call,
                                  record_type='start',
                                  timestamp=self.now)

        with self.assertRaises(IntegrityError):
            other_record.save()

    @patch('phone_billing.bill.receivers.bill_call_record')
    def test_after_save_should_call_bill_record_receiver(self, mocked_receiver):
        record = CallRecord(id=1,
                            call=self.call,
                            record_type='start',
                            timestamp=self.now)

        record.save()

        mocked_receiver.assert_called_once_with(record)
