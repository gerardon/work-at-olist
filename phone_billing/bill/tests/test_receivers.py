from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from ...call.models import Call, CallRecord

from ..models import BillRecord
from ..receivers import bill_call_record


class BillCallRecordReceiverTestCase(TestCase):
    def setUp(self):
        self.call = Call.objects.create(id=1, source='00123456789',
                                        destination='10123456789')

        now = timezone.now()
        self.start_record = CallRecord.objects.create(id=1, call=self.call,
                                                      timestamp=now,
                                                      record_type='start')
        self.end_record = CallRecord.objects.create(id=2, call=self.call,
                                                    timestamp=now,
                                                    record_type='end')

    @patch.object(BillRecord.objects, 'create_for_call')
    def test_bill_call_record_receiver_with_created_end_record(self, mocked_manager):
        bill_call_record(instance=self.call.end_record)

        mocked_manager.assert_called_once_with(self.call)

    @patch.object(BillRecord.objects, 'create_for_call')
    def test_bill_call_record_receiver_with_created_start_record(self, mocked_manager):
        bill_call_record(instance=self.call.start_record)

        mocked_manager.assert_called_once_with(self.call)

    @patch.object(BillRecord.objects, 'create_for_call')
    def test_bill_call_record_receiver_with_no_end_record(self, mocked_manager):
        self.end_record.delete()
        bill_call_record(instance=self.call.start_record)

        mocked_manager.assert_not_called()

    @patch.object(BillRecord.objects, 'create_for_call')
    def test_bill_call_record_receiver_with_no_start_record(self, mocked_manager):
        self.start_record.delete()
        bill_call_record(instance=self.call.end_record)

        mocked_manager.assert_not_called()
