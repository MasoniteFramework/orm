import math


_TIME_FORMATS = [
    (0, "< 1 sec"),
    (2, "1 sec"),
    (59, "secs", 1),
    (60, "1 min"),
    (3600, "mins", 60),
    (5400, "1 hr"),
    (86400, "hrs", 3600),
    (129600, "1 day"),
    (604800, "days", 86400),
]


def format_time(secs):  # type: (int) -> str
    for fmt in _TIME_FORMATS:
        if secs > fmt[0]:
            continue

        if len(fmt) == 2:
            return fmt[1]

        return "{} {}".format(math.ceil(secs / fmt[2]), fmt[1])
