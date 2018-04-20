from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView

from .models import CallRecord
from .serializers import CallRecordSerializer


class CallRecordsListCreate(ListCreateAPIView):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs and 'id' in kwargs['data']:
            id = kwargs['data']['id']
            qs = self.get_queryset().filter(id=id)
            if qs.exists():
                kwargs['instance'] = qs.get()

        return super().get_serializer(*args, **kwargs)


class CallRecordRetrieveUpdate(RetrieveUpdateAPIView):
    queryset = CallRecord.objects.all()
    serializer_class = CallRecordSerializer
