from .args import Args
from .format.args_format import ArgsFormat
from .raw_args import RawArgs


class ArgsParser(object):
    """
    Parses raw console arguments and returns the parsed arguments.
    """

    def parse(
        self, args, fmt, lenient=False
    ):  # type: (RawArgs, ArgsFormat, bool) -> Args
        raise NotImplementedError()
