from model_mommy import mommy

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Call, CallRecord
from ..serializers import CallRecordSerializer


class CallRecordsListCreateTestCase(TestCase):
    def setUp(self):
        self.url = reverse('call:records')
        self.start_record_post_data = {
            'id': 1,
            'type': 'start',
            'timestamp': timezone.now().timestamp(),
            'call_id': 1,
            'source': '00123456789',
            'destination': '10123456789'
        }

    def test_get_responds_all_serialized_records_list(self):
        records = mommy.make(CallRecord, _quantity=3)

        response = self.client.get(self.url)

        self.assertEquals(response.status_code, 200)
        data = response.json()

        for record in records:
            serialized_record = CallRecordSerializer(record).data
            self.assertIn(serialized_record, data)

    def test_post_creates_a_new_record(self):
        self.assertEquals(Call.objects.count(), 0)
        self.assertEquals(CallRecord.objects.count(), 0)

        response = self.client.post(self.url, self.start_record_post_data)

        self.assertEquals(response.status_code, 201)

        self.assertEquals(Call.objects.count(), 1)
        self.assertEquals(CallRecord.objects.count(), 1)

        data = response.json()
        record = CallRecord.objects.get()
        serialized_record = CallRecordSerializer(record).data
        self.assertEquals(serialized_record, data)

    def test_post_updates_record_if_already_created(self):
        self.client.post(self.url, self.start_record_post_data)

        right_now = timezone.now()
        post_data_copy = self.start_record_post_data.copy()
        post_data_copy['timestamp'] = right_now.timestamp()
        response = self.client.post(self.url, self.start_record_post_data)

        self.assertEquals(response.status_code, 201)

        self.assertEquals(Call.objects.count(), 1)
        self.assertEquals(CallRecord.objects.count(), 1)

        record = CallRecord.objects.get()
        self.assertEquals(record.timestamp, right_now.replace(microsecond=0))
