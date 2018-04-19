from django.test import TestCase
from django.utils import timezone

from rest_framework import serializers

from ..serializers import PhoneField, TimestampField


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

    def test_to_internal_value_parses_timestamp_without_microseconds(self):
        field = TimestampField()

        now = timezone.now()

        self.assertEquals(field.to_internal_value(now.timestamp()),
                          now.replace(microsecond=0))
