from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase


class BillSearchViewTestCase(APITestCase):
    def setUp(self):
        self.subscriber = '00123456789'
        self.url = reverse('bill:search', args=[self.subscriber])

    @patch('phone_billing.bill.views.BillSerializer')
    def test_success(self, MockedSerializer):
        mock_serializer = MockedSerializer.return_value
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {'test': 'test'}

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, mock_serializer.data)

        MockedSerializer.assert_called_once_with(
            data={'subscriber': self.subscriber})
        mock_serializer.is_valid.assert_called_once_with()
        mock_serializer.search_bill_records.assert_called_once_with()

    @patch('phone_billing.bill.views.BillSerializer')
    def test_success_with_period_param(self, MockedSerializer):
        mock_serializer = MockedSerializer.return_value
        mock_serializer.is_valid.return_value = True
        mock_serializer.data = {'test': 'test'}

        response = self.client.get(self.url, {'period': '04/2018'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, mock_serializer.data)

        MockedSerializer.assert_called_once_with(
            data={'subscriber': self.subscriber, 'period': '04/2018'})
        mock_serializer.is_valid.assert_called_once_with()
        mock_serializer.search_bill_records.assert_called_once_with()

    @patch('phone_billing.bill.views.BillSerializer')
    def test_bad_request(self, MockedSerializer):
        mock_serializer = MockedSerializer.return_value
        mock_serializer.is_valid.return_value = False
        mock_serializer.errors = {'test': 'test'}

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, mock_serializer.errors)

        MockedSerializer.assert_called_once_with(
            data={'subscriber': self.subscriber})
        mock_serializer.is_valid.assert_called_once_with()
