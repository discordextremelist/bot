import traceback
import datetime
import parsedatetime as pdt
import re

from discord.ext import commands
from dateutil.relativedelta import relativedelta


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'


def human_join(seq, delim=', ', final='or'):
    size = len(seq)
    if size == 0:
        return ''

    if size == 1:
        return seq[0]

    if size == 2:
        return f'{seq[0]} {final} {seq[1]}'

    return delim.join(seq[:-1]) + f' {final} {seq[-1]}'


def traceback_maker(err, advance: bool = True):
    _traceback = ''.join(traceback.format_tb(err.__traceback__))
    error = '```py\n{1}{0}: {2}\n```'.format(type(err).__name__, _traceback, err)
    return error if advance else f"{type(err).__name__}: {err}"


class HumanTime:
    calendar = pdt.Calendar(version=pdt.VERSION_CONTEXT_STYLE)

    def __init__(self, argument, *, now=None):
        now = now or datetime.datetime.utcnow()
        dt, status = self.calendar.parseDT(argument, sourceTime=now)
        if not status.hasDateOrTime:
            raise commands.BadArgument('invalid time provided, try e.g. "tomorrow" or "3 days"')

        if not status.hasTime:
            # replace it with the current time
            dt = dt.replace(hour=now.hour, minute=now.minute, second=now.second, microsecond=now.microsecond)

        self.dt = dt
        self._past = dt < now.replace(tzinfo=None)

    @classmethod
    async def convert(cls, ctx, argument):
        return cls(argument, now=ctx.message.created_at.replace(tzinfo=None))


class ShortTime:
    compiled = re.compile("""(?:(?P<years>[0-9])(?: years?|y))?             # e.g. 2y
                             (?:(?P<months>[0-9]{1,2})(?: months?|mo))?     # e.g. 2months
                             (?:(?P<weeks>[0-9]{1,4})(?: weeks?|w))?        # e.g. 10w
                             (?:(?P<days>[0-9]{1,5})(?: days?|d))?          # e.g. 14d
                             (?:(?P<hours>[0-9]{1,5})(?: hours?|h))?        # e.g. 12h
                             (?:(?P<minutes>[0-9]{1,5})(?: minutes?|m))?    # e.g. 10m
                             (?:(?P<seconds>[0-9]{1,5})(?: seconds?|s))?    # e.g. 15s
                          """, re.VERBOSE)

    def __init__(self, argument, *, now=None):
        match = self.compiled.fullmatch(argument)
        if match is None or not match.group(0):
            raise commands.BadArgument('invalid time provided')

        data = {k: int(v) for k, v in match.groupdict(default=0).items()}
        now = now or datetime.datetime.utcnow()
        self.dt = now.replace(tzinfo=None) + relativedelta(**data)

    @classmethod
    async def convert(cls, ctx, argument):
        return cls(argument, now=ctx.message.created_at)


class Time(HumanTime):
    def __init__(self, argument, *, now=None):
        try:
            o = ShortTime(argument, now=now.replace(tzinfo=None))
        except Exception:
            super().__init__(argument)
        else:
            self.dt = o.dt
            self._past = False


class FutureTime(Time):
    def __init__(self, argument, *, now=None):
        super().__init__(argument, now=now)

        if self._past:
            raise commands.BadArgument(f"{self.bot.settings['formats']['error']} **Invalid time:** You provided the time"
                                       "that is in the past.")


def human_timedelta(dt, *, source=None, accuracy=3, brief=False, suffix=True):
    now = source or datetime.datetime.now()
    now = now.replace(microsecond=0)
    dt = dt.replace(microsecond=0)

    if dt.replace(tzinfo=None) > now.replace(tzinfo=None):
        delta = relativedelta(dt, now.replace(tzinfo=None))
        suffix = ''
    else:
        delta = relativedelta(now.replace(tzinfo=None), dt)
        suffix = ' ago' if suffix else ''

    attrs = [
        ('year', 'y'),
        ('month', 'mo'),
        ('day', 'd'),
        ('hour', 'h'),
        ('minute', 'm'),
        ('second', 's'),
    ]

    output = []
    for attr, brief_attr in attrs:
        elem = getattr(delta, attr + 's')
        if not elem:
            continue

        if attr == 'day':
            weeks = delta.weeks
            if weeks:
                elem -= weeks * 7
                if not brief:
                    output.append(format(plural(weeks), 'week'))
                else:
                    output.append(f'{weeks}w')

        if elem <= 0:
            continue

        if brief:
            output.append(f'{elem}{brief_attr}')
        else:
            output.append(format(plural(elem), attr))

    if accuracy is not None:
        output = output[:accuracy]

    if len(output) == 0:
        return 'now'
    else:
        if not brief:
            return human_join(output, final='and') + suffix
        else:
            return ' '.join(output) + suffix
