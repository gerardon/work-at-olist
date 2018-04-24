from datetime import time, datetime
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
