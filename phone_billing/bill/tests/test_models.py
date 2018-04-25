from datetime import timedelta
from decimal import Decimal

from django.db.utils import IntegrityError, DataError
from django.test import TestCase
from django.utils import timezone

from ...call.models import Call

from ..models import BillRecord


class BillRecordTestCase:

    def setUp(self):
        self.call = Call.objects.create(id=1, source='00123456789',
                                        destination='10123456789')

    def test_valid_bill_record(self):
        record = BillRecord(call=self.call, price=Decimal('1'))

        record.save()

        record.refresh_from_db()
        self.assertEquals(record.id, 1)
        self.assertEquals(record.call, self.call)
        self.assertEquals(record.price, Decimal('1'))
