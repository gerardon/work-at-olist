from datetime import time, datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from ..pricing import BaseTariff, StandardTariff, ReducedTariff, get_tariff


class BaseTariffTestCase(TestCase):
    def test_default_attributes(self):
        self.assertEquals(BaseTariff.standing_charge, Decimal('0.36'))
        self.assertIsNone(BaseTariff.charge_per_minute)
        self.assertIsNone(BaseTariff.start_time)
        self.assertIsNone(BaseTariff.end_time)

    def test_is_applicable_day_time(self):
        BaseTariff.start_time = time(8)
        BaseTariff.end_time = time(10)

        self.assertTrue(BaseTariff.is_applicable(time(8)))
        self.assertTrue(BaseTariff.is_applicable(time(9)))
        self.assertFalse(BaseTariff.is_applicable(time(10)))

    def test_is_applicable_night_time(self):
        BaseTariff.start_time = time(22)
        BaseTariff.end_time = time(4)

        self.assertTrue(BaseTariff.is_applicable(time(22)))
        self.assertTrue(BaseTariff.is_applicable(time(0)))
        self.assertTrue(BaseTariff.is_applicable(time(2)))
        self.assertFalse(BaseTariff.is_applicable(time(4)))

    def test_get_called_minutes(self):
        delta = timedelta(minutes=5)
        self.assertEquals(BaseTariff.get_called_minutes(delta), 5)

    def test_get_called_minutes_disregarding_seconds(self):
        delta = timedelta(minutes=10, seconds=30)
        self.assertEquals(BaseTariff.get_called_minutes(delta), 10)

    @patch.object(BaseTariff, 'get_called_minutes')
    def test_calculate_uses_standing_charge_as_base(self, mock_called_minutes):
        mock_called_minutes.return_value = 0

        old_charge = BaseTariff.charge_per_minute
        BaseTariff.charge_per_minute = Decimal('0')

        self.assertEquals(BaseTariff.calculate(None),
                          BaseTariff.standing_charge)

        BaseTariff.charge_per_minute = old_charge

    @patch.object(BaseTariff, 'get_called_minutes')
    def test_calculate_uses_called_minutes_for_charging(self,
                                                        mock_called_minutes):
        called_minutes = 3
        mock_called_minutes.return_value = called_minutes

        old_charge = BaseTariff.standing_charge
        BaseTariff.standing_charge = Decimal('0')
        BaseTariff.charge_per_minute = Decimal('2')

        self.assertEquals(BaseTariff.calculate(None),
                          BaseTariff.charge_per_minute * called_minutes)

        BaseTariff.standing_charge = old_charge
        BaseTariff.charge_per_minute = None


class StandardTariffTestCase(TestCase):

    def test_inherits_base_tariff(self):
        self.assertTrue(issubclass(StandardTariff, BaseTariff))

    def test_attributes(self):
        self.assertEquals(BaseTariff.standing_charge, Decimal('0.36'))
        self.assertEquals(StandardTariff.charge_per_minute, Decimal('0.09'))
        self.assertEquals(StandardTariff.start_time, time(6))
        self.assertEquals(StandardTariff.end_time, time(22))


class ReducedTariffTestCase(TestCase):

    def test_inherits_base_tariff(self):
        self.assertTrue(issubclass(ReducedTariff, BaseTariff))

    def test_attributes(self):
        self.assertEquals(BaseTariff.standing_charge, Decimal('0.36'))
        self.assertEquals(ReducedTariff.charge_per_minute, Decimal('0.00'))
        self.assertEquals(ReducedTariff.start_time, time(22))
        self.assertEquals(ReducedTariff.end_time, time(6))


class GetTariffTestCase(TestCase):
    @patch.object(ReducedTariff, 'is_applicable')
    @patch.object(StandardTariff, 'is_applicable')
    def test_standard_tariff_if_applicable(self, standard_applicable,
                                           reduced_applicable):
        standard_applicable.return_value = True
        reduced_applicable.return_value = False

        self.assertEquals(get_tariff(datetime.now()), StandardTariff)

    @patch.object(ReducedTariff, 'is_applicable')
    @patch.object(StandardTariff, 'is_applicable')
    def test_standard_tariff_if_both_applicable(self, standard_applicable,
                                                reduced_applicable):
        standard_applicable.return_value = True
        reduced_applicable.return_value = True

        self.assertEquals(get_tariff(datetime.now()), StandardTariff)

    @patch.object(ReducedTariff, 'is_applicable')
    @patch.object(StandardTariff, 'is_applicable')
    def test_reduced_tariff_if_applicable(self, standard_applicable,
                                          reduced_applicable):
        standard_applicable.return_value = False
        reduced_applicable.return_value = True

        self.assertEquals(get_tariff(datetime.now()), ReducedTariff)
