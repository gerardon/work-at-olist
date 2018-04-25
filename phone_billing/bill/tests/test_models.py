from decimal import Decimal
from unittest.mock import patch, Mock

from django.db.utils import IntegrityError
from django.test import TestCase

from ...call.models import Call

from ..models import BillRecord


class BillRecordTestCase(TestCase):

    def setUp(self):
        self.call = Call.objects.create(id=1, source='00123456789',
                                        destination='10123456789')

    def test_valid_bill_record(self):
        record = BillRecord(call=self.call, price=Decimal('1'))

        record.save()

        record.refresh_from_db()
        self.assertEquals(record.call, self.call)
        self.assertEquals(record.price, Decimal('1'))

    @patch('phone_billing.bill.models.calculate_call_charge')
    def test_create_for_call_manager(self, mocked_service):
        mocked_service.return_value = Decimal('1')

        mock_call = Mock()
        mock_call.id = self.call.id
        mock_call.started_at = 'started_at'
        mock_call.ended_at = 'ended_at'

        record = BillRecord.objects.create_for_call(mock_call)
        self.assertEquals(record.call, self.call)
        self.assertEquals(record.price, Decimal('1'))

        mocked_service.assert_called_once_with('started_at', 'ended_at')

    def test_only_one_bill_record_per_call(self):
        record = BillRecord(call=self.call, price=Decimal('1'))
        record.save()

        other_record = BillRecord(call=self.call, price=Decimal('1'))

        with self.assertRaises(IntegrityError):
            other_record.save()
