from model_mommy import mommy
from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.utils import timezone
from rest_framework import serializers
from rest_framework.reverse import reverse

from ..models import Call, CallRecord
from ..serializers import PhoneField, TimestampField, CallRecordSerializer


class PhoneFieldTestCase(TestCase):
    def test_min_and_max_length_default(self):
        field = PhoneField()

        self.assertEquals(field.min_length, 10)
        self.assertEquals(field.max_length, 11)

    def test_to_internal_value_parses_int_to_string(self):
        field = PhoneField()

        self.assertEquals(field.to_internal_value(10123456789), '10123456789')

    def test_to_internal_value_must_be_digits(self):
        field = PhoneField()

        with self.assertRaisesRegexp(serializers.ValidationError,
                                     'Incorrect type, expected a phone number'
                                     ' comprised exclusively of digits.'):
            field.to_internal_value('AA123456789')

        self.assertEquals(field.to_internal_value('00123456789'),
                          '00123456789')


class TimestampFieldTestCase(TestCase):
    def test_to_representation_parses_to_timestamp(self):
        field = TimestampField()
        now = timezone.now()

        self.assertEquals(field.to_representation(now), int(now.timestamp()))

    def test_to_internal_value_parses_float_timestamp_without_microseconds(self):
        field = TimestampField()
        now = timezone.now()

        self.assertEquals(field.to_internal_value(now.timestamp()),
                          now.replace(microsecond=0))

    def test_to_internal_value_parses_string_timestamp_without_microseconds(self):
        field = TimestampField()
        now = timezone.now()

        self.assertEquals(field.to_internal_value(str(now.timestamp())),
                          now.replace(microsecond=0))


class CallRecordSerializerTestCase(TestCase):
    def setUp(self):
        now = timezone.now()

        self.valid_start_data = {
            'id': 1,
            'type': 'start',
            'timestamp': now.timestamp(),
            'call_id': 1,
            'source': '10123456789',
            'destination': '00123456789'
        }
        self.valid_end_data = {
            'id': 2,
            'type': 'end',
            'timestamp': now.timestamp(),
            'call_id': 1,
        }

    def test_required_fields(self):
        serializer = CallRecordSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn('id', serializer.errors)
        self.assertIn('type', serializer.errors)
        self.assertIn('timestamp', serializer.errors)
        self.assertIn('call_id', serializer.errors)

    def test_start_records_require_source_and_destination(self):
        end_data_copy = self.valid_end_data.copy()
        end_data_copy['type'] = 'start'
        serializer = CallRecordSerializer(data=end_data_copy)

        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEquals(serializer.errors['non_field_errors'][0],
                          'The fields source and destination are required on a'
                          ' call start record.')

    def test_type_choices(self):
        test_type = 'test'
        valid_data_copy = self.valid_start_data.copy()
        valid_data_copy['type'] = test_type

        serializer = CallRecordSerializer(data=valid_data_copy)

        self.assertFalse(serializer.is_valid())

        self.assertIn('type', serializer.errors)
        self.assertEquals(serializer.errors['type'][0],
                          f'"{test_type}" is not a valid choice.')

    def test_timestamp_source_and_destination_custom_fields(self):
        serializer = CallRecordSerializer(data=self.valid_start_data)

        self.assertIsInstance(serializer.fields['timestamp'], TimestampField)
        self.assertIsInstance(serializer.fields['source'], PhoneField)
        self.assertIsInstance(serializer.fields['destination'], PhoneField)

    def test_type_and_call_id_unique_together(self):
        serializer = CallRecordSerializer(data=self.valid_start_data)
        serializer.is_valid()
        serializer.save()

        valid_data_copy = self.valid_start_data.copy()
        valid_data_copy['id'] = 2
        dup_serializer = CallRecordSerializer(data=valid_data_copy)

        self.assertFalse(dup_serializer.is_valid())
        self.assertIn('non_field_errors', dup_serializer.errors)
        self.assertEquals(dup_serializer.errors['non_field_errors'][0],
                          'This call_id already has this type of call record.')

    def test_start_record_save_related_objects_creates_call_and_removes_call_data(self):
        serializer = CallRecordSerializer(data=self.valid_start_data)

        self.assertTrue(serializer.is_valid())
        self.assertEquals(Call.objects.count(), 0)

        serializer.save_related_objects()

        self.assertEquals(Call.objects.count(), 1)
        call = Call.objects.first()
        self.assertEquals(call.id, self.valid_start_data['call_id'])
        self.assertEquals(call.source, self.valid_start_data['source'])
        self.assertEquals(call.destination,
                          self.valid_start_data['destination'])

        self.assertNotIn('call', serializer.validated_data)

    @patch.object(CallRecordSerializer, 'save_related_objects')
    def test_save_calls_save_related_objects(self, mocked_method):
        serializer = CallRecordSerializer(data=self.valid_start_data)

        self.assertTrue(serializer.is_valid())

        # This reproduces the save_related_objects behaviour.
        Call.objects.create(id=self.valid_start_data['call_id'],
                            source=self.valid_start_data['source'],
                            destination=self.valid_start_data['destination'])
        serializer.validated_data.pop('call')

        serializer.save()

        mocked_method.assert_called_once_with()

    def test_save_returns_a_correct_call_record(self):
        serializer = CallRecordSerializer(data=self.valid_start_data)

        self.assertTrue(serializer.is_valid())

        call_record = serializer.save()
        self.assertEquals(call_record.id, self.valid_start_data['id'])
        self.assertEquals(call_record.record_type,
                          self.valid_start_data['type'])
        self.assertEquals(int(call_record.timestamp.timestamp()),
                          int(self.valid_start_data['timestamp']))
        self.assertEquals(call_record.call_id,
                          self.valid_start_data['call_id'])

    def test_get_url(self):
        record = mommy.make(CallRecord)
        factory = RequestFactory()
        request = factory.get('/api/call/records/')

        serializer = CallRecordSerializer(record, context={'request': request})
        self.assertEquals(str(serializer.get_url(record)),
                          str(reverse('call:record_detail', args=[record.id],
                                      request=request)))
