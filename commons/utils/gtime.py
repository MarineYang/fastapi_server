import time
from datetime import date, datetime, timedelta, timezone


class GTime:
    def UTC():
        return datetime.now(timezone.utc)

    def UTCStr(format="%Y-%m-%d %H:%M:%S"):
        return GTime.UTC().strftime(format)

    def UTCInt():
        return int(GTime.UTC().strftime("%Y%m%d%H%M%S"))

    def UTCTupleByAddTime(dd: int = 0, h: int = 0, m: int = 0, s: int = 0):
        temp = GTime.UTC() + timedelta(days=dd, hours=h, minutes=m, seconds=s)
        return temp

    def UTCIntTuple():
        form = GTime.UTC()
        return form.year, form.month, form.day, form.hour, form.minute, form.second

    def UTCIntTupleByAddTime(dd: int = 0, h: int = 0, m: int = 0):
        form = GTime.UTC() + timedelta(days=dd, hours=h, minutes=m)
        return form.year, form.month, form.day, form.hour, form.minute, form.second

    def UTCTupleBySubTime(dd: int = 0, h: int = 0, m: int = 0, s: int = 0):
        temp = GTime.UTC() - timedelta(days=dd, hours=h, minutes=m, seconds=s)
        return temp

    def UTCIntTupleBySubTime(dd: int = 0, h: int = 0, m: int = 0):
        form = GTime.UTC() - timedelta(days=dd, hours=h, minutes=m)
        return form.year, form.month, form.day, form.hour, form.minute, form.second

    def UTCStrTupleBySubTime(dd: int = 0, h: int = 0, m: int = 0, format="%Y-%m-%d %H:%M:%S"):
        temp = GTime.UTC() - timedelta(days=dd, hours=h, minutes=m)
        return temp.strftime(format)

    def StrParseTime(date_string, format="%Y-%m-%d %H:%M:%S"):
        return datetime.strptime(date_string, format).replace(tzinfo=timezone.utc)

    def date_to_str(yy: int = 0, mm: int = 0, dd: int = 0) -> str:
        temp = date(yy, mm, dd)
        return str(temp)

    def datetime_to_str(dt: datetime, format="%Y-%m-%d %H:%M:%S") -> str:
        return dt.strftime(format)

    def target_to_sub(target: str = "", dd: int = 0, format="%Y-%m-%d %H:%M:%S"):
        temp = datetime.strptime(target, "%Y-%m-%d") - timedelta(days=dd)
        return temp.strftime(format)

    def datetime_to_str(target: datetime, format="%Y-%m-%d %H:%M:%S"):
        return target.strftime(format)

    def start_and_end_dt(target: datetime = datetime.now(timezone.utc), dd: int = 0, format="%Y-%m-%d %H:%M:%S"):
        start_dt = target.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = start_dt.replace(hour=23, minute=59, second=59) + timedelta(days=dd)
        return start_dt.strftime(format), end_dt.strftime(format)


class StopWatch:
    def __init__(self) -> None:
        super().__init__()
        self.start = time.time()

    def Stop(self) -> None:
        self.finish = time.time()

    def Duration(self, stop=True) -> float:
        if stop:
            self.Stop()

        return self.finish - self.start

    def Print(self, stop=True) -> None:
        if stop:
            self.Stop()

        print(f"Duration : {self.finish - self.start} sec")


def HowLong(func):
    def Wrapper(*args, **kwargs):
        sw = StopWatch()
        ret = func(*args, **kwargs)
        print(f"DELAY - {func.__module__}.{func.__name__}: {sw.Duration()} sec")
        return ret

    return Wrapper
