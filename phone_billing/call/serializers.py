from datetime import datetime

from rest_framework import serializers


class PhoneField(serializers.CharField):
    def __init__(self, *args, max_length=11, min_length=10, **kwargs):
        super().__init__(*args, max_length=max_length,
                         min_length=min_length, **kwargs)

    def to_internal_value(self, data):
        if not isinstance(data, str):
            data = str(data)

        if not data.isdigit():
            msg = ('Incorrect type, expected a phone number'
                   ' comprised exclusively of digits.')
            raise serializers.ValidationError(msg)
        return super().to_internal_value(data)


class TimestampField(serializers.DateTimeField):
    def to_representation(self, value):
        return int(value.timestamp())

    def to_internal_value(self, value):
        dt = datetime.utcfromtimestamp(int(value))
        return super().to_internal_value(dt)
