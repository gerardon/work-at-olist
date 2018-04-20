from django.db.utils import IntegrityError, DataError
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

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


class CallRecordModelTestCase(TestCase):

    def setUp(self):
        self.call = Call.objects.create(id=1,
                                        source='00123456789',
                                        destination='00123456789')
        self.now = now()

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
