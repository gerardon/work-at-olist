from datetime import time
from decimal import Decimal

from django.test import TestCase

from ..pricing import BaseTariff, StandardTariff, ReducedTariff


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
