import json
from model_mommy import mommy

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from ..models import Call, CallRecord
from ..serializers import CallRecordSerializer


class SerializerContextTestCase(TestCase):
    def setUp(self):
        factory = RequestFactory()
        request = factory.get('/api/')
        self.serializer_context = {'request': request}


class CallRecordsListCreateTestCase(SerializerContextTestCase):
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
        super().setUp()

    def test_get_responds_all_serialized_records_list(self):
        records = mommy.make(CallRecord, _quantity=3)

        response = self.client.get(self.url)

        self.assertEquals(response.status_code, 200)
        data = response.json()

        for record in records:
            serialized_record = CallRecordSerializer(
                record, context=self.serializer_context
            ).data
            self.assertIn(serialized_record, data)

    def test_post_creates_a_new_record(self):
        self.assertEquals(Call.objects.count(), 0)
        self.assertEquals(CallRecord.objects.count(), 0)

        response = self.client.post(self.url,
                                    json.dumps(self.start_record_post_data),
                                    content_type='application/json')

        self.assertEquals(response.status_code, 201)

        self.assertEquals(Call.objects.count(), 1)
        self.assertEquals(CallRecord.objects.count(), 1)

        data = response.json()
        record = CallRecord.objects.get()
        serialized_record = CallRecordSerializer(
            record, context=self.serializer_context
        ).data
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


class CallRecordRetrieveUpdateTestCase(SerializerContextTestCase):
    def setUp(self):
        self.record = mommy.make(CallRecord)
        self.url = reverse('call:record_detail', args=[self.record.id])

        super().setUp()

    def test_get_responds_serialized_record(self):
        response = self.client.get(self.url)

        self.assertEquals(response.status_code, 200)
        data = response.json()

        serialized_record = CallRecordSerializer(
            self.record, context=self.serializer_context
        ).data
        self.assertEquals(serialized_record, data)

    def test_put_should_update_record(self):
        put_data = {
            'id': self.record.id,
            'type': 'start',
            'timestamp': timezone.now().timestamp(),
            'call_id': self.record.call.id,
            'source': '00123456789',
            'destination': '10123456789',
        }
        response = self.client.put(self.url, json.dumps(put_data),
                                   content_type='application/json')

        self.assertEquals(response.status_code, 200)

        self.record.refresh_from_db()
        self.record.call.refresh_from_db()
        self.assertEquals(self.record.id, put_data['id'])
        self.assertEquals(self.record.record_type, put_data['type'])
        self.assertEquals(self.record.timestamp.timestamp(),
                          int(put_data['timestamp']))
        self.assertEquals(self.record.call_id, put_data['call_id'])
        self.assertEquals(self.record.call.source, put_data['source'])
        self.assertEquals(self.record.call.destination,
                          put_data['destination'])
