from datetime import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Call, CallRecord


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
        dt = datetime.utcfromtimestamp(int(float(value)))
        return super().to_internal_value(dt)


class CallRecordSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(min_value=0)
    type = serializers.ChoiceField(choices=CallRecord.RECORD_TYPES,
                                   source='record_type')
    timestamp = TimestampField()
    call_id = serializers.IntegerField(min_value=0)
    source = PhoneField(source='call.source', required=False)
    destination = PhoneField(source='call.destination', required=False)

    class Meta:
        model = CallRecord
        fields = ('id', 'type', 'timestamp',
                  'call_id', 'source', 'destination')
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('record_type', 'call_id'),
                message='This call_id already has this type of call record.')]

    def validate(self, data):
        if data['record_type'] == 'start':
            if (data.get('call') is None
                    or 'destination' not in data['call'].keys()
                    or 'source' not in data['call'].keys()):
                raise serializers.ValidationError(
                    'The fields source and destination are required on a call'
                    ' start record.')

        return super().validate(data)

    def save(self):
        self.save_related_objects()
        return super().save()

    def save_related_objects(self):
        call_data = self.validated_data.pop('call', {})

        call_id = self.validated_data['call_id']
        source = call_data.get('source', None)
        destination = call_data.get('destination', None)

        if source and destination:
            Call.objects.update_or_create(
                id=call_id, defaults={'source': source,
                                      'destination': destination})
