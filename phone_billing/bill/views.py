from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from .serializers import BillSerializer


class BillSearchView(APIView):
    def get_search_data(self, request, subscriber):
        search_data = {'subscriber': subscriber}
        if 'period' in request.query_params:
            search_data['period'] = request.query_params['period']

        return search_data

    def get(self, request, subscriber, format=None):
        search_data = self.get_search_data(request, subscriber)
        serializer = BillSerializer(data=search_data)
        if serializer.is_valid():
            serializer.search_bill_records()
            return Response(serializer.data)

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
