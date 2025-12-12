from clikit.api.io import IO
from clikit.api.io import Input
from clikit.api.io import Output

from .input_stream import NullInputStream
from .output_stream import NullOutputStream


class NullIO(IO):
    """
    An I/O that does nothing.
    """

    def __init__(self):  # type: () -> None
        input = Input(NullInputStream())
        output = Output(NullOutputStream())
        error_output = Output(NullOutputStream())

        super(NullIO, self).__init__(input, output, error_output)
