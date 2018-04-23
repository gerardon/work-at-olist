from datetime import time
from decimal import Decimal


def get_tariff(call_dt):
    call_time = call_dt.time()

    if StandardTariff.is_applicable(call_time):
        return StandardTariff
    elif ReducedTariff.is_applicable(call_time):
        return ReducedTariff


class BaseTariff:
    standing_charge = Decimal('0.36')
    charge_per_minute = None
    start_time = None
    end_time = None

    @classmethod
    def is_applicable(cls, call_time):
        if cls.start_time < cls.end_time:
            return cls.start_time <= call_time < cls.end_time
        else:
            return call_time < cls.end_time or call_time >= cls.start_time


class StandardTariff(BaseTariff):
    charge_per_minute = Decimal('0.09')
    start_time = time(6)
    end_time = time(22)


class ReducedTariff(BaseTariff):
    charge_per_minute = Decimal('0.00')
    start_time = time(22)
    end_time = time(6)
