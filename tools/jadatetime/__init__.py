# -*- coding: utf-8 -*-
# Jalali Advance datetime by Pouya Malekinejad <pouya.malekinejad@gmail.com>
# this jadatetime is based on jdatetime library
# jdatetime is (c) 2010-2011 Milad Rastian <eslashmili at gmail.com>.
# The jdatetime module was contributed to Python as of Python 2.7 and thus
# was licensed under the Python license. Same license applies to all files in
# the jdatetime package project.

import platform
import datetime as py_datetime
import locale as _locale
import re as _re
from dateutil import relativedelta
from datetime import timedelta

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from _thread import get_ident

from .jalali import (GregorianToJalali, JalaliToGregorian,
                     j_days_in_month)

# Making translators
make_translations = lambda n, m: dict((ord(a), b) for a, b in zip(n, m))
number_converter = make_translations(
    u'١٢٣٤٥٦٧٨٩٠۱۲۳۴۵۶۷۸۹۰₀₁₂₃₄₅₆₇₈₉¹²⁰⁴⁵⁶⁷⁸⁹⓪①②③④⑤⑥⑦⑧⑨⑴⑵⑶⑷⑸⑹⑺⑻⑼⒈⒉⒊⒋⒌⒍⒎⒏⒐',
    u'1234567890123456789001234567891204567890123456789123456789123456789'
)
persian_converter = make_translations(u'1234567890', u'۱۲۳۴۵۶۷۸۹۰')

# The first version will be released when tests for format_date completes
__VERSION__ = "0.11.0"
MINYEAR = -650
MAXYEAR = 9377

timedelta = py_datetime.timedelta
tzinfo = py_datetime.tzinfo

timestamp_is_supported = hasattr(py_datetime.datetime, 'timestamp') and \
                         callable(py_datetime.datetime.timestamp)


if platform.system() == 'Windows':
    FA_LOCALE = 'Persian_Iran'
else:
    FA_LOCALE = 'fa_IR'


def _format_time(hour, minute, second, microsecond, timespec='auto'):
    specs = {
        'hours': '{:02d}',
        'minutes': '{:02d}:{:02d}',
        'seconds': '{:02d}:{:02d}:{:02d}',
        'milliseconds': '{:02d}:{:02d}:{:02d}.{:03d}',
        'microseconds': '{:02d}:{:02d}:{:02d}.{:06d}',
    }

    if timespec == 'auto':
        # Skip trailing microseconds when equals to 0
        timespec = 'microseconds' if microsecond else 'seconds'
    elif timespec == 'milliseconds':
        # convert to millisecond
        microsecond //= 1000

    try:
        fmt = specs[timespec]
    except KeyError:
        raise ValueError('Unknown timespec value: %s' % timespec)
    else:
        return fmt.format(hour, minute, second, microsecond)


class time(py_datetime.time):
    def __repr__(self):
        return "jadatetime.time(%s, %s, %s)" % (self.hour, self.minute, self.second)


_thread_local_locales = dict()


def set_locale(locale):
    """Set the thread local module locale. This will be the default locale
    for new date/datetime instances in current thread.
    Returns the previous value of locale set on current thread.

    Note: since Python thread identities maybe recycled and reused,
    always ensure the desied locale is set for current thread,
    or the locale maybe affected by previous threads with the same
    identity.

    :param str|None: locale
    :return: str|None
    """
    thread_identity = get_ident()
    prev_locale = _thread_local_locales.get(thread_identity)
    _thread_local_locales[thread_identity] = locale
    return prev_locale


def get_locale():
    """Get the thread local module locale. This will be the default locale
    for newly date/datetime instances in current thread.

    :return: str|None
    """
    return _thread_local_locales.get(get_ident())


class date(object):
    """date(year, month, day) --> date object"""
    j_months_en = ('Farvardin',
                   'Ordibehesht',
                   'Khordad',
                   'Tir',
                   'Mordad',
                   'Shahrivar',
                   'Mehr',
                   'Aban',
                   'Azar',
                   'Dey',
                   'Bahman',
                   'Esfand')
    j_months_short_en = ('Far',
                         'Ord',
                         'Kho',
                         'Tir',
                         'Mor',
                         'Sha',
                         'Meh',
                         'Aba',
                         'Aza',
                         'Dey',
                         'Bah',
                         'Esf')

    j_weekdays_en = ('Saturday',
                     'Sunday',
                     'Monday',
                     'Tuesday',
                     'Wednesday',
                     'Thursday',
                     'Friday')
    j_weekdays_short_en = ('Sat',
                           'Sun',
                           'Mon',
                           'Tue',
                           'Wed',
                           'Thu',
                           'Fri')
    j_ampm_en = ('AM', 'PM')
    j_ampm_short_en = ('AM', 'PM')

    j_quarter_en = ('Spring', 'Summer', 'Autumn', 'Winter')

    j_quarter_short_en = ('Q1', 'Q2', 'Q3', 'Q4')

    j_GMT_en = 'GMT'

    j_era_en = ('Before Hegira', 'After Hegira')
    j_era_short_en = ('BH', 'AH')
    j_era_narrow_en = ('B', 'A')

    j_months_fa = (u'فروردین',
                   u'اردیبهشت',
                   u'خرداد',
                   u'تیر',
                   u'مرداد',
                   u'شهریور',
                   u'مهر',
                   u'آبان',
                   u'آذر',
                   u'دی',
                   u'بهمن',
                   u'اسفند')

    j_months_short_fa = (u'فرو',
                         u'ارد',
                         u'خرد',
                         u'تیر',
                         u'مرد',
                         u'شهر',
                         u'مهر',
                         u'آبا',
                         u'آذر',
                         u'دی',
                         u'بهم',
                         u'اسف')

    j_weekdays_fa = (u'شنبه',
                     u'یکشنبه',
                     u'دوشنبه',
                     u'سه‌شنبه',
                     u'چهارشنبه',
                     u'پنجشنبه',
                     u'جمعه')

    j_weekdays_short_fa = (u'شنبه',
                           u'یک',
                           u'دو',
                           u'سه',
                           u'چهار',
                           u'پنج',
                           u'جمعه')
    j_ampm_fa = (u'قبل از ظهر.', u'بعد از ظهر.')
    j_ampm_short_fa = (u'ق. ظ.', u'ب. ظ.')

    j_quarter_fa = ('بهار', 'تابستان', 'پاییز', 'زمستان')

    j_quarter_short_fa = ('ب', 'ت', 'پ', 'ز')

    j_GMT_fa = 'گرینویچ'

    j_era_fa = ('قبل از هجرت', '')
    j_era_short_fa = ('ق. ه.', '')
    j_era_narrow_fa = ('ق. ه.', '')

    @property
    def year(self):
        return self.__year

    @property
    def month(self):
        return self.__month

    @property
    def day(self):
        return self.__day

    def timetuple(self):
        "Return local time tuple compatible with time.localtime()."
        return self.togregorian().timetuple()

    @property
    def locale(self):
        return self.__locale

    __year = 0
    __month = 0
    __day = 0
    __locale = None

    def _check_arg(self, value):
        if isinstance(value, int):
            return True
        return False

    def __init__(self, year, month, day, **kwargs):
        """date(year, month, day) --> date object"""
        if not (self._check_arg(year) and
                self._check_arg(month) and
                self._check_arg(day)):
            raise TypeError("an integer is required" + repr(type(year)))
        if year < MINYEAR or year > MAXYEAR:
            raise ValueError("%s year is out of range" % year)
        self.__year = year

        if month < 1 or month > 12:
            raise ValueError("month must be in 1..12 not %s" % month)
        self.__month = month

        if day < 1:
            raise ValueError("day %s is out of range for month %s" % (day, month))
        if self.__month == 12 and day == 30 and self.isleap():
            # for leap years it's ok to have 30 days in Esfand
            pass
        elif self.__month == 12 and day == 30 and not self.isleap():
            raise ValueError("day %s is out of range for month %s" % (day, month))
        elif day > j_days_in_month[self.__month - 1]:
            raise ValueError("day %s is out of range for month %s" % (day, month))
        self.__day = day
        self.__locale = kwargs['locale'] if ('locale' in kwargs and kwargs['locale']) else get_locale()

        if self._is_fa_locale():
            self.j_months = self.j_months_fa
            self.j_months_short = self.j_months_short_fa
            self.j_weekdays = self.j_weekdays_fa
            self.j_weekdays_short = self.j_weekdays_short_fa
            self.j_ampm = self.j_ampm_fa
            self.j_ampm_short = self.j_ampm_short_fa
            self.j_quarter = self.j_quarter_fa
            self.j_quarter_short = self.j_quarter_short_fa
            self.j_GMT = self.j_GMT_fa
            self.j_era = self.j_era_fa
            self.j_era_short = self.j_era_short_fa
            self.j_era_narrow = self.j_era_narrow_fa
        else:
            self.j_months = self.j_months_en
            self.j_months_short = self.j_months_short_en
            self.j_weekdays = self.j_weekdays_en
            self.j_weekdays_short = self.j_weekdays_short_en
            self.j_ampm = self.j_ampm_en
            self.j_ampm_short = self.j_ampm_short_en
            self.j_quarter = self.j_quarter_en
            self.j_quarter_short = self.j_quarter_short_en
            self.j_GMT = self.j_GMT_en
            self.j_era = self.j_era_en
            self.j_era_short = self.j_era_short_en
            self.j_era_narrow = self.j_era_narrow_en

    def _is_fa_locale(self):
        if self.__locale and self.__locale == FA_LOCALE:
            return True
        if FA_LOCALE in _locale.getlocale():
            return True
        if None not in _locale.getlocale():
            return False
        if FA_LOCALE in _locale.getdefaultlocale():
            return True
        return False

    """The smallest possible difference between
    non-equal date objects, timedelta(days=1)."""
    resolution = timedelta(1)

    """The earliest representable date, date(MINYEAR, 1, 1)"""
    # min = date(MINYEAR, 1, 1)
    # TODO fixed errror:  name 'date' is not defined
    """The latest representable date, date(MAXYEAR, 12, 31)."""

    # max = date(MAXYEAR, 12,29)

    def isleap(self):
        """check if year is leap year
            algortim is based on http://en.wikipedia.org/wiki/Leap_year"""
        return self.year % 33 in (1, 5, 9, 13, 17, 22, 26, 30)

    def togregorian(self):
        """Convert current jalali date to gregorian and return datetime.date"""
        (y, m, d) = JalaliToGregorian(self.year,
                                      self.month,
                                      self.day).getGregorianList()
        return py_datetime.date(y, m, d)

    @staticmethod
    def fromgregorian(**kw):
        """Convert gregorian to jalali and return jadatetime.date

        jadatetime.date.fromgregorian(day=X,month=X,year=X)
        jadatetime.date.fromgregorian(date=datetime.date)
        jadatetime.date.fromgregorian(date=datetime.date, locale='fa_IR')
        """
        locale = kw.get('locale')
        if 'date' in kw:
            d = kw['date']
            try:
                (y, m, d) = GregorianToJalali(d.year,
                                              d.month,
                                              d.day).getJalaliList()
                return date(y, m, d, locale=locale)
            except AttributeError:
                raise ValueError('When calling fromgregorian(date=) the parameter should be a date like object.')
        if 'day' in kw and 'month' in kw and 'year' in kw:
            (year, month, day) = (kw['year'], kw['month'], kw['day'])
            (y, m, d) = GregorianToJalali(year, month, day).getJalaliList()
            return date(y, m, d, locale=locale)

        error_msg = ["fromgregorian have to be be called"]
        error_msg += ["or"]
        error_msg += ["fromgregorian(day=X,month=X,year=X)"]
        error_msg += ["fromgregorian(date=datetime.date)"]
        raise ValueError(" ".join(error_msg))

    @staticmethod
    def today():
        """Current date or datetime:  same as self.__class__.fromtimestamp(time.time())."""
        to = py_datetime.date.today()
        (y, m, d) = GregorianToJalali(to.year,
                                      to.month,
                                      to.day).getJalaliList()
        return date(y, m, d)

    @staticmethod
    def fromtimestamp(timestamp):
        d = py_datetime.date.fromtimestamp(timestamp)
        (y, m, d) = GregorianToJalali(d.year, d.month, d.day).getJalaliList()
        return date(y, m, d)

    def toordinal(self):
        """Return proleptic jalali ordinal. Farvardin 1 of year 1 which is equal to 622-3-21 of Gregorian."""
        d = self.togregorian()
        return d.toordinal() - 226894

    @staticmethod
    def fromordinal(ordinal):
        """int -> date corresponding to a proleptic Jalali ordinal. it starts from Farvardin 1 of year 1, which is equal to 622-3-21 of Gregorian"""
        if ordinal < 1:
            raise ValueError("ordinal must be >= 1")
        d = py_datetime.date.fromordinal(226894 + ordinal)
        (y, m, d) = GregorianToJalali(d.year, d.month, d.day).getJalaliList()
        return date(y, m, d)

    def __repr__(self):
        return "jadatetime.date(%s, %s, %s)" % (self.year,
                                                self.month,
                                                self.day)

    def __str__(self):
        return self.strftime("%Y-%m-%d")

    def __add__(self, other):
        """x.__add__(y) <==> x+y"""
        if isinstance(other, relativedelta.relativedelta) or \
                isinstance(other, py_datetime.timedelta):
            return date.fromgregorian(date=self.togregorian() + other, locale=self.locale)
        raise TypeError(
            "unsupported operand type(s) for +: '%s' and '%s'" %
            (type(self), type(other)))

    def __sub__(self, other):
        """x.__sub__(y) <==> x-y"""

        if isinstance(other, relativedelta.relativedelta) or \
                isinstance(other, py_datetime.timedelta):
            return date.fromgregorian(date=self.togregorian() - other, locale=self.locale)
        if isinstance(other, date):
            return self.togregorian() - other.togregorian()
        if isinstance(other, py_datetime.date):
            return self.togregorian() - other

        raise TypeError(
            "unsupported operand type(s) for -: '%s' and '%s'" %
            (type(self), type(timedelta)))

    def __radd__(self, other):
        """x.__radd__(y) <==> y+x"""
        if isinstance(other, relativedelta.relativedelta) or \
                isinstance(other, py_datetime.timedelta):
            return self.__add__(other)
        raise TypeError(
            "unsupported operand type for +: '%s' and '%s'" %
            (type(other), type(self)))

    def __rsub__(self, other):
        """x.__rsub__(y) <==> y-x"""
        if isinstance(other, date):
            return other.__sub__(self)
        if isinstance(other, py_datetime.date):
            return other - self.togregorian()
        raise TypeError("unsupported operand type for -: '%s' and '%s'" %
                        (type(other), type(self)))

    def __eq__(self, other_date):
        """x.__eq__(y) <==> x==y"""
        if other_date is None:
            return False
        if isinstance(other_date, date):
            if self.year == other_date.year and \
                    self.month == other_date.month and \
                    self.day == other_date.day and \
                    self.locale == other_date.locale:
                return True
        if isinstance(other_date, py_datetime.date):
            return self.__eq__(date.fromgregorian(date=other_date))

        return False

    def __ge__(self, other_date):
        """x.__ge__(y) <==> x>=y"""
        if isinstance(other_date, date):

            if self.year > other_date.year:
                return True
            elif self.year == other_date.year:
                if self.month > other_date.month:
                    return True
                elif self.month == other_date.month and self.day >= other_date.day:
                    return True
            return False
        if isinstance(other_date, py_datetime.date):
            return self.__ge__(date.fromgregorian(date=other_date))
        raise TypeError(
            "unsupported operand type for >=: '%s'" %
            (type(other_date)))

    def __gt__(self, other_date):
        """x.__gt__(y) <==> x>y"""
        if isinstance(other_date, date):

            if self.year > other_date.year:
                return True
            elif self.year == other_date.year:
                if self.month > other_date.month:
                    return True
                elif self.month >= other_date.month and self.day > other_date.day:
                    return True
            return False
        if isinstance(other_date, py_datetime.date):
            return self.__gt__(date.fromgregorian(date=other_date))

        raise TypeError(
            "unsupported operand type for >: '%s'" %
            (type(other_date)))

    def __le__(self, other_date):
        """x.__le__(y) <==> x<=y"""
        if isinstance(other_date, date):
            return not self.__gt__(other_date)
        if isinstance(other_date, py_datetime.date):
            return self.__le__(date.fromgregorian(date=other_date))

        raise TypeError(
            "unsupported operand type for <=: '%s'" %
            (type(other_date)))

    def __lt__(self, other_date):
        """x.__lt__(y) <==> x<y"""
        if isinstance(other_date, date):
            return not self.__ge__(other_date)
        if isinstance(other_date, py_datetime.date):
            return self.__lt__(date.fromgregorian(date=other_date))

        raise TypeError(
            "unsupported operand type for <: '%s'" %
            (type(other_date)))

    def __ne__(self, other_date):
        """x.__ne__(y) <==> x!=y"""
        if other_date is None:
            return True
        if isinstance(other_date, date):
            return not self.__eq__(other_date)
        if isinstance(other_date, py_datetime.date):
            return self.__ne__(date.fromgregorian(date=other_date))
        return True

    def __hash__(self):
        """x.__hash__() <==> hash(x)"""
        gd = self.togregorian()
        return gd.__hash__()

    def ctime(self):
        """Return ctime() style string."""
        return self.strftime("%c")

    def replace(self, year=0, month=0, day=0):
        """Return date with new specified fields."""
        new_year = self.year
        new_month = self.month
        new_day = self.day

        if year != 0:
            new_year = year
        if month != 0:
            new_month = month
        if day != 0:
            new_day = day

        return date(new_year, new_month, new_day, locale=self.locale)

    def yday(self):
        """return day of year"""
        day = 0
        for i in range(0, self.month - 1):
            day = day + j_days_in_month[i]
        day = day + self.day
        return day

    def weekday(self):
        """Return the day of the week represented by the date.
        Shanbeh == 0 ... Jomeh == 6"""
        gd = self.togregorian()
        return (gd.weekday() - 5) % 7

    def isoweekday(self):
        """Return the day of the week as an integer, where Shanbeh is 1 and Jomeh is 7"""
        return self.weekday() + 1

    def weeknumber(self):
        """Return week number """
        return (self.yday() + date(self.year, 1, 1).weekday() - 1) // 7 + 1

    def weekofmonth(self):
        """Returns week number of current day in current month"""
        return (self.day + date(self.year, self.month, 1).weekday() - 1) // 7 + 1

    def quarter(self):
        return (self.month - 1) // 3 + 1

    def isocalendar(self):
        """Return a 3-tuple, (ISO year, ISO week number, ISO weekday)."""
        return (self.year, self.weeknumber(), self.isoweekday())

    def isoformat(self):
        """Return a string representing the date in ISO 8601 format, 'YYYY-MM-DD'"""
        return self.strftime("%Y-%m-%d")

    def __format__(self, fmt):
        """
        PEP-3101
        Make string formating work!
        """
        return self.strftime(fmt)

    def strftime(self, fmt):
        """format -> strftime() style string."""
        # TODO: change stupid str.replace
        # formats = {
        #           '%a': lambda: self.j_weekdays_short[self.weekday()]
        # }
        # find all %[a-zA-Z] and call method if it in formats

        # convert to unicode

        fmt = fmt.replace("%a", self.j_weekdays_short[self.weekday()])

        fmt = fmt.replace("%A", self.j_weekdays[self.weekday()])

        fmt = fmt.replace("%b", self.j_months_short[self.month - 1])

        fmt = fmt.replace("%B", self.j_months[self.month - 1])

        if '%c' in fmt:
            fmt = fmt.replace(
                "%c", self.strftime("%a %d %b %Y, %H:%M:%S"))

        fmt = fmt.replace("%d", '%02.d' % (self.day))
        fmt = fmt.replace("%-d", '%d' % (self.day))

        try:
            fmt = fmt.replace("%f", '%06.d' % (self.microsecond))
        except:
            fmt = fmt.replace("%f", "000000")

        try:
            fmt = fmt.replace("%H", '%02.d' % (self.hour))
        except:
            fmt = fmt.replace("%H", '00')

        try:
            fmt = fmt.replace("%-H", '%d' % (self.hour))
        except:
            fmt = fmt.replace("%-H", '0')

        try:
            fmt = fmt.replace("%I", '%02.d' % (self.hour % 12 or 12))
        except:
            fmt = fmt.replace("%I", '12')

        try:
            fmt = fmt.replace("%-I", '%d' % (self.hour % 12 or 12))
        except:
            fmt = fmt.replace("%-I", '12')

        fmt = fmt.replace("%j", '%03.d' % (self.yday()))

        fmt = fmt.replace("%m", '%02.d' % (self.month))
        fmt = fmt.replace("%-m", '%d' % (self.month))

        try:
            fmt = fmt.replace("%M", '%02.d' % (self.minute))
        except:
            fmt = fmt.replace("%M", '00')

        try:
            fmt = fmt.replace("%-M", '%d' % (self.minute))
        except:
            fmt = fmt.replace("%-M", '0')

        try:
            fmt = fmt.replace("%p", self.j_ampm_short[int(self.hour >= 12)])
        except:
            fmt = fmt.replace("%p", self.j_ampm[0])

        try:
            fmt = fmt.replace("%S", '%02.d' % (self.second))
        except:
            fmt = fmt.replace("%S", '00')

        try:
            fmt = fmt.replace("%-S", '%d' % (self.second))
        except:
            fmt = fmt.replace("%-S", '0')

        fmt = fmt.replace("%w", str(self.weekday()))

        fmt = fmt.replace("%W", str(self.weeknumber()))

        if '%x' in fmt:
            fmt = fmt.replace("%x", self.strftime("%Y/%m/%d"))

        if '%X' in fmt:
            fmt = fmt.replace("%X", self.strftime('%H:%M:%S'))

        fmt = fmt.replace("%Y", str(self.year))

        fmt = fmt.replace("%y", str(self.year)[2:])

        fmt = fmt.replace("%Y", str(self.year))

        try:
            sign = "+"
            diff = self.tzinfo.utcoffset(self)
            diff_sec = diff.seconds
            if diff.days > 0 or diff.days < -1:
                raise ValueError(
                    "tzinfo.utcoffset() returned big time delta! ; must be in -1439 .. 1439")
            if diff.days != 0:
                sign = "-"
                diff_sec = (1 * 24 * 60 * 60) - diff_sec
            tmp_min = diff_sec / 60
            diff_hour = tmp_min / 60
            diff_min = tmp_min % 60
            fmt = fmt.replace(
                "%z", '%s%02.d%02.d' %
                      (sign, diff_hour, diff_min))
        except AttributeError:
            fmt = fmt.replace("%z", '')

        try:
            fmt = fmt.replace("%Z", self.tzinfo.tzname(self))
        except AttributeError:
            fmt = fmt.replace("%Z", '')

        if self._is_fa_locale():
            fmt = fmt.translate(persian_converter)
        return fmt

    def format_datetime(self, fmt):
        """format -> LDML style string.
        formats according to the Unicode Technical Standard #35
        Unicode Locale Data Markup Language (LDML)
        https://www.unicode.org/reports/tr35/tr35.html
        Part 4 of that standard is used in this function:
        http://www.unicode.org/reports/tr35/tr35-dates.html

        if called with a date object, time tokens are ignored

        Warning: Time Zone names are not properly handled.
        """

        result = []
        for tok_type, tok_value in _tokenize_pattern(fmt):
            if tok_type == "chars":
                result.append(tok_value.replace('%', '%%'))
            elif tok_type == "field":
                fieldchar, fieldnum = tok_value
                limit = PATTERN_CHARS[fieldchar]
                if limit and fieldnum not in limit:
                    raise ValueError('Invalid length for field: %r'
                                     % (fieldchar * fieldnum))
                res = self.parse_token(fieldchar, fieldnum)
                if self._is_fa_locale() and fieldchar != 'r':
                    res = res.translate(persian_converter)
                result.append(res)
            else:
                raise NotImplementedError("Unknown token type: %s" % tok_type)
        return ''.join(result)

    def parse_token(self, token, num):

        # Date Formats
        if token == 'G':
            if num < 4:
                return self.j_era_short[int(self.year >= 0)]
            elif num == 4:
                return self.j_era[int(self.year >= 0)]
            elif num == 5:
                return self.j_era_narrow[int(self.year >= 0)]

        if token == 'y' or token == 'Y' or token == 'U':
            year = abs(self.year)
            if num == 2:
                return '{}'.format(str(year)[-2:]) if year > 9 else '{:02d}'.format(year)
            else:
                return '{:0{}d}'.format(year, num)

        if token == 'u':
            return '{:0{}d}'.format(self.year, num)

        if token == 'r':
            return '{:0{}d}'.format(self.year + 621, num)

        if token == 'q' or token == 'Q':
            quarter = (self.month - 1) // 3
            if num < 3:
                return '{:0{}d}'.format(quarter + 1, num)
            elif num == 4:
                return self.j_quarter[quarter]
            elif num == 5 and not self._is_fa_locale():
                return '{:d}'.format(quarter)
            else:  # 3 or 5, short nd narrow are the same
                return self.j_quarter_short[quarter]

        if token == 'M' or token == 'L':
            if num < 3:
                return '{:0{}d}'.format(self.month, num)
            elif num == 3:
                return self.j_months_short[self.month - 1]
            elif num == 4:
                return self.j_months[self.month - 1]
            elif num == 5:
                self.j_months[self.month - 1][0]

        if token == 'w':
            return '{:0{}d}'.format(self.weeknumber(), num)

        if token == 'W':
            return '{:d}'.format(self.weekofmonth())

        if token == 'd':
            return '{:0{}d}'.format(self.day, num)

        if token == 'D':
            return '{:0{}d}'.format(self.yday(), num)

        if token == 'F':
            # if dayofweek of self is equal or greater than first of month, it should be equal to self.weekofmonth()
            # otherwise, it is one less because first week of month does not have self.weekday (it starts later)
            return '{:d}'.format(self.weekofmonth() - int(self.weekday() < self.replace(day=1).weekday()))

        if token == 'E':
            if num < 4:
                return self.j_weekdays_short[self.weekday()]
            elif num == 4:
                return self.j_weekdays[self.weekday()]
            elif num == 5:
                return self.j_weekdays[self.weekday()][0]
            elif num == 6:
                return self.j_weekdays[self.weekday()][:2]

        if token == 'e':
            if num < 3:
                return '{:0{}d}'.format(self.weekday(), num)
            elif num == 3:
                return self.j_weekdays_short[self.weekday()]
            elif num == 4:
                return self.j_weekdays[self.weekday()]
            elif num == 5:
                return self.j_weekdays[self.weekday()][0]
            elif num == 6:
                return self.j_weekdays[self.weekday()][:2]

        if token == 'c':
            if num < 3:
                return '{:d}'.format(self.weekday())
            elif num == 3:
                return self.j_weekdays_short[self.weekday()]
            elif num == 4:
                return self.j_weekdays[self.weekday()]
            elif num == 5:
                return self.j_weekdays[self.weekday()][0]
            elif num == 6:
                return self.j_weekdays[self.weekday()][:2]

        # if it called on date object but the token is a time token, exception would raise. it does not touch the time
        # tokens and does not raise exception as well.
        try:
            if token == 'a':
                if num < 4:
                    return self.j_ampm_short[int(self.hour >= 12)]
                elif num == 4:
                    return self.j_ampm[int(self.hour >= 12)]
                elif num == 5:
                    return self.j_ampm[int(self.hour >= 12)][0]

            if token == 'h':
                return '{:0{}d}'.format(self.hour % 12 or 12, num)
            if token == 'H':
                return '{:0{}d}'.format(self.hour, num)
            if token == 'k':
                return '{:0{}d}'.format(self.hour % 12, num)
            if token == 'K':
                return '{:0{}d}'.format(self.hour + 1, num)

            if token == 'm':
                return '{:0{}d}'.format(self.minute, num)

            if token == 's':
                return '{:0{}d}'.format(self.second, num)

            if token == 'S':
                # note: babel rounds microseconds but LDML specifies it should be truncated
                return '{:0<{}}'.format(str(self.microsecond)[:num], num)

            if token == 'A':
                ms = int(((self.hour * 60 + self.minute) * 60 + self.second) * 1000 + self.microsecond / 1000)
                # note: babel rounds microseconds but LDML specifies it should be truncated
                return '{:0{}d}'.format(ms, num)

            if token == 'z' or token == 'v' or token == 'V':
                # it needs a hell amount of data, we just tzname
                return self.tzinfo.tzname(self)

            # Time Zone calculations
            sign = "+"
            diff = self.tzinfo.utcoffset(self)
            diff_sec = diff.seconds
            if diff.days > 0 or diff.days < -1:
                raise ValueError(
                    "tzinfo.utcoffset() returned big time delta! ; must be in -1439 .. 1439")
            if diff.days != 0:
                sign = "-"
                diff_sec = (1 * 24 * 60 * 60) - diff_sec
            tmp_min = diff_sec // 60
            diff_hour = tmp_min // 60
            diff_min = tmp_min % 60
            diff_frac_sec = diff_sec % 60

            if token == 'Z':
                if num < 4:
                    return '{}{:02d}{:02d}'.format(sign, diff_hour, diff_min)
                elif num == 4:
                    return '{}{}{:d}:{:02d}'.format(self.j_GMT, sign, diff_hour, diff_min)
                elif num == 5:
                    if diff_sec == 0:
                        return 'Z'
                    return '{}{:02d}:{:02d}'.format(sign, diff_hour, diff_min) + ':{}'.format(
                        diff_frac_sec) if diff_frac_sec else ''

            if token == 'O':
                if num == 1:
                    return '{}{}{:d}'.format(self.j_GMT, sign, diff_hour) + (
                        '{:d}'.format(diff_min) if diff_min else '')
                elif num == 4:
                    return '{}{}{:02d}:{:02d}'.format(self.j_GMT, sign, diff_hour, diff_min)

            if token == 'X' or token == 'x':
                if token == 'X' and diff_sec == 0:
                    return 'Z'
                elif num == 1:
                    return '{}{:2d}'.format(sign, diff_hour) + ('{:2d}'.format(diff_min) if diff_min else '')
                elif num == 2:
                    return '{}{:2d}{:2d}'.format(sign, diff_hour, diff_min)
                elif num == 3:
                    return '{}{:2d}:{:2d}'.format(sign, diff_hour, diff_min)
                elif num == 4:
                    return '{}{:2d}{:2d}' '{}'.format(sign, diff_hour, diff_min, diff_frac_sec) if diff_frac_sec else ''
                elif num == 5:
                    return '{}{:2d}:{:2d}' ':{}'.format(sign, diff_hour, diff_min,
                                                        diff_frac_sec) if diff_frac_sec else ''

        except AttributeError:
            return token * num

    def aslocale(self, locale):
        return date(self.year, self.month, self.day, locale=locale)

    #####################
    # Utility Functions #
    #####################
    def get_period(self, period):
        jdate_from = jdate_to = self
        if period in ['month', 'm', '%m']:
            jdate_from = self.replace(day=1)
            jdate_to = jdate_from.replace(year=jdate_from.year + jdate_from.month // 12,
                                          # adds a year only if month is 12
                                          month=(jdate_from.month + 1) % 13 or 1) - timedelta(days=1)
        elif period in ['quarter', 'quart', 'q']:
            jdate_from = self.replace(month=(self.quarter() - 1) * 3 + 1, day=1)
            jmonth_to_next = (self.quarter() * 3 + 1) % 13 or 1
            jdate_to = self.replace(year=jdate_from.year + int(jmonth_to_next == 1), month=jmonth_to_next,
                                    day=1) - timedelta(days=1)
        elif period in ['year', 'y', 'Y', '%y', '%Y']:
            jdate_from = self.replace(month=1, day=1)
            jdate_to = jdate_from.replace(year=self.year + 1) - timedelta(days=1)
        return jdate_from, jdate_to

    def get_period_in_gregorian(self, period):
        jdate_from, jdate_to = self.get_period(period)
        return jdate_from.togregorian(), jdate_to.togregorian()


PATTERN_CHARS = {  # note: 'g', 'j', 'J', 'C', 'b' and 'B' are not implemented
    'G': [1, 2, 3, 4, 5],  # era
    'y': None, 'Y': None, 'U': None, 'u': None, 'r': None,  # year
    'Q': [1, 2, 3, 4, 5], 'q': [1, 2, 3, 4, 5],  # quarter
    'M': [1, 2, 3, 4, 5], 'L': [1, 2, 3, 4, 5],  # month
    'w': [1, 2], 'W': [1],  # week
    'd': [1, 2], 'D': [1, 2, 3], 'F': [1], 'g': None,  # day
    'E': [1, 2, 3, 4, 5, 6], 'e': [1, 2, 3, 4, 5, 6], 'c': [1, 3, 4, 5, 6],  # week day
    'a': [1],  # period
    'h': [1, 2], 'H': [1, 2], 'K': [1, 2], 'k': [1, 2],  # hour
    'm': [1, 2],  # minute
    's': [1, 2], 'S': None, 'A': None,  # second
    'z': [1, 2, 3, 4], 'Z': [1, 2, 3, 4, 5], 'O': [1, 4], 'v': [1, 4],  # zone
    'V': [1, 2, 3, 4], 'x': [1, 2, 3, 4, 5], 'X': [1, 2, 3, 4, 5]  # zone
}


def _tokenize_pattern(pattern):
    """
    Borrowed from Babel, it is used for format_datetime method

    Tokenize date format patterns.

    Returns a list of (token_type, token_value) tuples.

    ``token_type`` may be either "chars" or "field".

    For "chars" tokens, the value is the literal value.

    For "field" tokens, the value is a tuple of (field character, repetition count).

    :param pattern: Pattern string
    :type pattern: str
    :rtype: list[tuple]
    """
    result = []
    quotebuf = None
    charbuf = []
    fieldchar = ['']
    fieldnum = [0]

    def append_chars():
        result.append(('chars', ''.join(charbuf).replace('\0', "'")))
        del charbuf[:]

    def append_field():
        result.append(('field', (fieldchar[0], fieldnum[0])))
        fieldchar[0] = ''
        fieldnum[0] = 0

    for idx, char in enumerate(pattern.replace("''", '\0')):
        if quotebuf is None:
            if char == "'":  # quote started
                if fieldchar[0]:
                    append_field()
                elif charbuf:
                    append_chars()
                quotebuf = []
            elif char in PATTERN_CHARS:
                if charbuf:
                    append_chars()
                if char == fieldchar[0]:
                    fieldnum[0] += 1
                else:
                    if fieldchar[0]:
                        append_field()
                    fieldchar[0] = char
                    fieldnum[0] = 1
            else:
                if fieldchar[0]:
                    append_field()
                charbuf.append(char)

        elif quotebuf is not None:
            if char == "'":  # end of quote
                charbuf.extend(quotebuf)
                quotebuf = None
            else:  # inside quote
                quotebuf.append(char)

    if fieldchar[0]:
        append_field()
    elif charbuf:
        append_chars()

    return result


class datetime(date):
    """datetime(year, month, day, [hour, [minute, [seconds, [microsecond, [tzinfo]]]]]) --> datetime objects"""
    __time = None

    def time(self):
        """Return time object with same time but with tzinfo=None."""
        return time(self.hour, self.minute, self.second, self.microsecond)

    def date(self):
        """Return date object with same year, month and day."""
        return date(self.year, self.month, self.day, locale=self.locale)

    def __init__(
            self,
            year,
            month,
            day,
            hour=None,
            minute=None,
            second=None,
            microsecond=None,
            tzinfo=None, **kwargs):
        date.__init__(self, year, month, day, **kwargs)
        tmp_hour = 0
        tmp_min = 0
        tmp_sec = 0
        tmp_micr = 0
        if hour is not None:
            tmp_hour = hour
        if minute is not None:
            tmp_min = minute
        if second is not None:
            tmp_sec = second
        if microsecond is not None:
            tmp_micr = microsecond

        if not (self._check_arg(tmp_hour) and self._check_arg(tmp_min) and
                self._check_arg(tmp_sec) and self._check_arg(tmp_micr)):
            raise TypeError("an integer is required")

        self.__time = time(tmp_hour, tmp_min, tmp_sec, tmp_micr, tzinfo)

    def __repr__(self):
        if self.__time.tzinfo is not None:
            return "jadatetime.datetime(%s, %s, %s, %s, %s, %s, %s, tzinfo=%s)" % (
                self.year,
                self.month,
                self.day, self.hour,
                self.minute,
                self.second,
                self.microsecond,
                self.tzinfo)

        if self.__time.microsecond != 0:
            return "jadatetime.datetime(%s, %s, %s, %s, %s, %s, %s)" % (
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second,
                self.microsecond)

        if self.__time.second != 0:
            return "jadatetime.datetime(%s, %s, %s, %s, %s, %s)" % (
                self.year,
                self.month,
                self.day,
                self.hour,
                self.minute,
                self.second)

        return "jadatetime.datetime(%s, %s, %s, %s, %s)" % (
            self.year, self.month, self.day, self.hour, self.minute)

    @staticmethod
    def today():
        """Current date or datetime"""
        return datetime.now()

    @staticmethod
    def now(tz=None):
        """[tz] -> new datetime with tz's local day and time."""
        now_datetime = py_datetime.datetime.now(tz)
        now = date.fromgregorian(date=now_datetime.date())
        return datetime(
            now.year,
            now.month,
            now.day,
            now_datetime.hour,
            now_datetime.minute,
            now_datetime.second,
            now_datetime.microsecond,
            tz)

    @staticmethod
    def utcnow():
        """Return a new datetime representing UTC day and time."""
        now_datetime = py_datetime.datetime.utcnow()
        now = date.fromgregorian(date=now_datetime.date())
        return datetime(
            now.year,
            now.month,
            now.day,
            now_datetime.hour,
            now_datetime.minute,
            now_datetime.second,
            now_datetime.microsecond)

    @staticmethod
    def fromtimestamp(timestamp, tz=None):
        """timestamp[, tz] -> tz's local time from POSIX timestamp."""
        now_datetime = py_datetime.datetime.fromtimestamp(timestamp, tz)
        now = date.fromgregorian(date=now_datetime.date())
        return datetime(
            now.year,
            now.month,
            now.day,
            now_datetime.hour,
            now_datetime.minute,
            now_datetime.second,
            now_datetime.microsecond,
            tz)

    @staticmethod
    def utcfromtimestamp(timestamp):
        """timestamp -> UTC datetime from a POSIX timestamp (like time.time())."""
        now_datetime = py_datetime.datetime.fromtimestamp(timestamp)
        now = date.fromgregorian(date=now_datetime.date())
        return datetime(
            now.year,
            now.month,
            now.day,
            now_datetime.hour,
            now_datetime.minute,
            now_datetime.second,
            now_datetime.microsecond)

    @staticmethod
    def combine(d=None, t=None, **kw):
        """date, time -> datetime with same date and time fields"""

        c_date = None
        if d is not None:
            c_date = d
        elif 'date' in kw:
            c_date = kw['date']

        c_time = None
        if t is not None:
            c_time = t
        elif 'time' in kw:
            c_time = kw['time']

        if c_date is None:
            raise TypeError("Required argument 'date' (pos 1) not found")
        if c_time is None:
            raise TypeError("Required argument 'time' (pos 2) not found")

        if not isinstance(c_date, date):
            raise TypeError(
                "combine() argument 1 must be jadatetime.date, not %s" %
                (type(c_date)))
        if not isinstance(c_time, time):
            raise TypeError(
                "combine() argument 2 must be jadatetime.time, not %s" %
                (type(c_time)))

        return datetime(
            c_date.year,
            c_date.month,
            c_date.day,
            c_time.hour,
            c_time.minute,
            c_time.second,
            c_time.microsecond,
            c_time.tzinfo,
            locale=c_date.locale)

    def timestamp(self):
        gregorian_datetime = self.togregorian()
        if timestamp_is_supported:
            return gregorian_datetime.timestamp()
        raise NotImplementedError('`datetime.datetime.timestamp` is not '
                                  'implemented in this version of python')

    @staticmethod
    def fromordinal(ordinal):
        """int -> date corresponding to a proleptic Jalali ordinal. it starts from Farvardin 1 of year 1, which is equal to 622-3-21 of Gregorian"""
        if ordinal < 1:
            raise ValueError("ordinal must be >= 1")
        d = py_datetime.date.fromordinal(226894 + ordinal)
        j_date = date.fromgregorian(date=d)
        return datetime(j_date.year, j_date.month, j_date.day, 0, 0)

    @property
    def hour(self):
        return self.__time.hour

    @property
    def minute(self):
        return self.__time.minute

    @property
    def second(self):
        return self.__time.second

    @property
    def microsecond(self):
        return self.__time.microsecond

    @property
    def tzinfo(self):
        return self.__time.tzinfo

    @staticmethod
    def strptime(date_string, format):
        """string, format -> new datetime parsed from a string (like time.strptime())"""
        dt_string = date_string.translate(number_converter)

        if '*' in format:
            format = format.replace("*", "\*")
        if '+' in format:
            format = format.replace("+", "\+")
        if '(' in format or ')' in format:
            format = format.replace("(", "\(")
            format = format.replace(")", "\)")
        if '[' in format or ']' in format:
            format = format.replace("[", "\[")
            format = format.replace("]", "\]")
        result_date = {
            'day': 1,
            'month': 1,
            'year': 1279,
            'microsecond': 0,
            'second': 0,
            'minute': 0,
            'hour': 0}
        apply_order = []
        format_map = {
            '%d': ['[0-9]{1,2}', 'day'],
            '%f': ['[0-9]{1,6}', 'microsecond'],
            '%H': ['[0-9]{1,2}', 'hour'],
            '%m': ['[0-9]{1,2}', 'month'],
            '%M': ['[0-9]{1,2}', 'minute'],
            '%S': ['[0-9]{1,2}', 'second'],
            '%Y': ['[0-9]{4,5}', 'year'],
        }
        regex = format
        find = _re.compile("(%[a-zA-Z])")

        for form in find.findall(format):
            if form in format_map:
                regex = regex.replace(form, "(" + format_map[form][0] + ")")
                apply_order.append(format_map[form][1])
        try:
            p = _re.compile(regex)
            if not p.match(dt_string):
                raise ValueError()
            for i, el in enumerate(p.match(dt_string).groups()):
                result_date[apply_order[i]] = int(el)
            return datetime(
                result_date['year'],
                result_date['month'],
                result_date['day'],
                result_date['hour'],
                result_date['minute'],
                result_date['second'])
        except:
            raise ValueError(
                "time data '%s' does not match format '%s'" %
                (date_string, format))

    def replace(
            self,
            year=None,
            month=None,
            day=None,
            hour=None,
            minute=None,
            second=None,
            microsecond=None,
            tzinfo=True):
        """Return datetime with new specified fields."""
        t_year = self.year
        if year is not None:
            t_year = year

        t_month = self.month
        if month is not None:
            t_month = month

        t_day = self.day
        if day is not None:
            t_day = day

        t_hour = self.hour
        if hour is not None:
            t_hour = hour

        t_min = self.minute
        if minute is not None:
            t_min = minute

        t_sec = self.second
        if second is not None:
            t_sec = second

        t_mic = self.microsecond
        if microsecond is not None:
            t_mic = microsecond

        t_tz = self.tzinfo
        if tzinfo is not True:
            t_tz = tzinfo
        return datetime(
            t_year,
            t_month,
            t_day,
            t_hour,
            t_min,
            t_sec,
            t_mic,
            t_tz,
            locale=self.locale)

    def __add__(self, other):
        """x.__add__(y) <==> x+y"""
        if isinstance(other, relativedelta.relativedelta) or \
                isinstance(other, py_datetime.timedelta):
            return datetime.fromgregorian(datetime=self.togregorian() + other, locale=self.locale)
        raise TypeError(
            "unsupported operand type(s) for +: '%s' and '%s'" %
            (type(self), type(other)))

    def __sub__(self, other):
        """x.__sub__(y) <==> x-y"""

        if isinstance(timedelta, relativedelta.relativedelta) or \
                isinstance(other, py_datetime.timedelta):
            return datetime.fromgregorian(datetime=self.togregorian() - other, locale=self.locale)
        if isinstance(other, datetime):
            return self.togregorian() - other.togregorian()
        if isinstance(other, py_datetime.datetime):
            return self.togregorian() - other
        raise TypeError(
            "unsupported operand type(s) for -: '%s' and '%s'" %
            (type(self), type(other)))

    def __radd__(self, other):
        """x.__radd__(y) <==> y+x"""
        if isinstance(other, relativedelta.relativedelta) or \
                isinstance(other, py_datetime.timedelta):
            return self.__add__(other)
        raise TypeError(
            "unsupported operand type for +: '%s' and '%s'" %
            (type(other), type(self)))

    def __rsub__(self, other):
        """x.__rsub__(y) <==> y-x"""
        if isinstance(other, datetime):
            return other.__sub__(self)
        if isinstance(other, py_datetime.datetime):
            return other - self.togregorian()
        raise TypeError("unsupported operand type for -: '%s' and '%s'" %
                        (type(other), type(self)))

    def __eq__(self, other_datetime):
        """x.__eq__(y) <==> x==y"""
        if other_datetime is None:
            return False
        if isinstance(other_datetime, datetime):
            if self.year == other_datetime.year and \
                    self.month == other_datetime.month and \
                    self.day == other_datetime.day and \
                    self.locale == other_datetime.locale:
                return self.timetz() == other_datetime.timetz(
                ) and self.microsecond == other_datetime.microsecond
            return False
        if isinstance(other_datetime, py_datetime.datetime):
            return self.__eq__(datetime.fromgregorian(datetime=other_datetime))
        return False

    def __ge__(self, other_datetime):
        """x.__ge__(y) <==> x>=y"""
        if isinstance(other_datetime, datetime):
            return (self.year,
                    self.month,
                    self.day,
                    self.hour,
                    self.minute,
                    self.second,
                    self.microsecond) >= \
                   (other_datetime.year,
                    other_datetime.month,
                    other_datetime.day,
                    other_datetime.hour,
                    other_datetime.minute,
                    other_datetime.second,
                    other_datetime.microsecond)
        if isinstance(other_datetime, py_datetime.datetime):
            return self.__ge__(datetime.fromgregorian(datetime=other_datetime))
        raise TypeError(
            "unsupported operand type for >=: '%s'" %
            (type(other_datetime)))

    def __gt__(self, other_datetime):
        """x.__gt__(y) <==> x>y"""
        if isinstance(other_datetime, datetime):
            return (self.year,
                    self.month,
                    self.day,
                    self.hour,
                    self.minute,
                    self.second,
                    self.microsecond) > \
                   (other_datetime.year,
                    other_datetime.month,
                    other_datetime.day,
                    other_datetime.hour,
                    other_datetime.minute,
                    other_datetime.second,
                    other_datetime.microsecond)
        if isinstance(other_datetime, py_datetime.datetime):
            return self.__gt__(datetime.fromgregorian(datetime=other_datetime))

        raise TypeError(
            "unsupported operand type for >: '%s'" %
            (type(other_datetime)))

    def __hash__(self):
        """x.__hash__() <==> hash(x)"""
        gdt = self.togregorian()
        return gdt.__hash__()

    def __le__(self, other_datetime):
        """x.__le__(y) <==> x<=y"""
        if isinstance(other_datetime, datetime):
            return not self.__gt__(other_datetime)
        if isinstance(other_datetime, py_datetime.datetime):
            return self.__le__(datetime.fromgregorian(datetime=other_datetime))

        raise TypeError(
            "unsupported operand type for <=: '%s'" %
            (type(other_datetime)))

    def __lt__(self, other_datetime):
        """x.__lt__(y) <==> x<y"""
        if isinstance(other_datetime, datetime):
            return not self.__ge__(other_datetime)
        if isinstance(other_datetime, py_datetime.datetime):
            return self.__lt__(datetime.fromgregorian(datetime=other_datetime))
        raise TypeError(
            "unsupported operand type for <: '%s'" %
            (type(other_datetime)))

    def __ne__(self, other_datetime):
        """x.__ne__(y) <==> x!=y"""
        if other_datetime is None:
            return True
        if isinstance(other_datetime, datetime):
            return not self.__eq__(other_datetime)
        if isinstance(other_datetime, py_datetime.datetime):
            return self.__ne__(datetime.fromgregorian(datetime=other_datetime))

        return True

    @staticmethod
    def fromgregorian(**kw):
        """Convert gregorian to jalali and return jadatetime.datetime
        jadatetime.date.fromgregorian(day=X,month=X,year=X,[hour=X, [minute=X, [second=X, [tzinfo=X]]]])
        jadatetime.date.fromgregorian(date=datetime.date)
        jadatetime.date.fromgregorian(datetime=datetime.date)
        jadatetime.date.fromgregorian(datetime=datetime.datetime)
        jadatetime.date.fromgregorian(datetime=datetime.datetime, locale='fa_IR')
        """
        locale = kw.get('locale')
        date_param = kw.get('date') or kw.get('datetime')
        if date_param:
            try:
                (y, m, d) = GregorianToJalali(date_param.year,
                                              date_param.month,
                                              date_param.day).getJalaliList()
            except AttributeError:
                raise ValueError(
                    'When calling fromgregorian(date=) or fromgregorian(datetime=) the parameter should be date like.')
            try:
                return datetime(
                    y,
                    m,
                    d,
                    date_param.hour,
                    date_param.minute,
                    date_param.second,
                    date_param.microsecond,
                    date_param.tzinfo,
                    locale=locale)
            except AttributeError:
                return datetime(y, m, d, locale=locale)

        if 'day' in kw and 'month' in kw and 'year' in kw:
            (year, month, day) = (kw['year'], kw['month'], kw['day'])
            (y, m, d) = GregorianToJalali(year, month, day).getJalaliList()
            hour = None
            minute = None
            second = None
            microsecond = None
            tzinfo = None
            if 'hour' in kw:
                hour = kw['hour']
                if 'minute' in kw:
                    minute = kw['minute']
                    if 'second' in kw:
                        second = kw['second']
                        if 'microsecond' in kw:
                            microsecond = kw['microsecond']
                            if 'tzinfo' in kw:
                                tzinfo = kw['tzinfo']
            return datetime(y, m, d, hour, minute, second, microsecond, tzinfo, locale=locale)

        raise ValueError(
            "fromgregorian have to called fromgregorian(day=X,month=X,year=X, [hour=X, [minute=X, [second=X, [tzinfo=X]]]]) or fromgregorian(date=datetime.date) or fromgregorian(datetime=datetime.datetime)")

    def togregorian(self):
        """Convert current jalali date to gregorian and return datetime.datetime"""
        gdate = date.togregorian(self)
        return py_datetime.datetime.combine(gdate, self.__time)

    def astimezone(self, tz):
        """tz -> convert to local time in new timezone tz"""
        gdt = self.togregorian()
        gdt = gdt.astimezone(tz)
        return datetime.fromgregorian(datetime=gdt)

    def ctime(self):
        """Return ctime() style string."""
        return self.strftime("%c")

    # TODO: check what this def does !
    def dst(self):
        """Return self.tzinfo.dst(self)"""
        if self.tzinfo:
            return self.tzinfo.dst(self)
        return None

    def isoformat(self, sep=str('T'), timespec='auto'):
        """[sep] -> string in ISO 8601 format,
        YYYY-MM-DDTHH:MM:SS[.mmmmmm][+HH:MM]."""

        assert isinstance(sep, str) and len(sep) == 1, \
            'argument 1 must be a single character: {}'.format(sep)

        tz = self.strftime("%z")

        date_ = self.strftime("%Y-%m-%d")
        time_ = _format_time(self.hour, self.minute, self.second,
                             self.microsecond, timespec)

        return '{}{}{}{}'.format(date_, sep, time_, tz)

    def timetuple(self):
        """Return time tuple, compatible with time.localtime().
        It returns Gregorian object!
        """
        dt = self.togregorian()
        return dt.timetuple()

    def timetz(self):
        """Return time object with same time and tzinfo."""
        return self.__time

    def tzname(self):
        """Return self.tzinfo.tzname(self)"""
        if self.tzinfo:
            return self.tzinfo.tzname(self)
        return None

    def utcoffset(self):
        """Return self.tzinfo.utcoffset(self)."""
        if self.tzinfo:
            return self.tzinfo.utcoffset(self)

    def utctimetuple(self):
        """Return UTC time tuple, compatible with time.localtime().
        It returns Gregorian object !
        """
        dt = self.togregorian()
        return dt.utctimetuple()

    def __str__(self):
        mil = self.strftime("%f")
        if int(mil) == 0:
            mil = ""
        else:
            mil = "." + mil
        tz = self.strftime("%z")
        return self.strftime("%Y-%m-%d %H:%M:%S") + "%s%s" % (mil, tz)

    def aslocale(self, locale):
        return datetime(self.year, self.month, self.day, self.hour, self.minute,
                        self.second, self.microsecond, tzinfo=self.tzinfo, locale=locale)
