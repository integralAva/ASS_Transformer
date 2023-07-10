from datetime import timedelta

__all__ = ['ASSTime']


class ASSTime(object):
    def __init__(self, time_ass: str = None):
        if time_ass is None:
            self.time = timedelta(seconds=0)
        else:
            self.time = ASSTime._timedelta_from_ass(time_ass)

    def to_ass(self):
        return ASSTime._timedelta_to_ass(self.time)

    def time_offset(self, **kwargs):
        """days, seconds, microseconds, milliseconds, minutes, hours, weeks"""
        delta = timedelta()
        if 'last' in kwargs:
            delta = kwargs['last']
            kwargs.pop('last')
        self.time += timedelta(**kwargs) + delta

    @staticmethod
    def _timedelta_to_ass(td: timedelta):
        r = int(td.total_seconds())

        r, secs = divmod(r, 60)
        hours, mins = divmod(r, 60)

        return "{hours:.0f}:{mins:02.0f}:{secs:02.0f}.{csecs:02}".format(
            hours=hours,
            mins=mins,
            secs=secs,
            csecs=td.microseconds // 10000
        )

    @staticmethod
    def _timedelta_from_ass(time_ass: str):
        secs_str, _, csecs = time_ass.partition(".")
        hours, mins, secs = map(int, secs_str.split(":"))

        r = hours * 60 * 60 + mins * 60 + secs + int(csecs) * 1e-2

        return timedelta(seconds=r)
