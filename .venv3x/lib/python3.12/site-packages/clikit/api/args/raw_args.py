from typing import List
from typing import Optional


class RawArgs(object):
    """
    The unparsed console arguments.
    """

    @property
    def script_name(self):  # type: () -> Optional[str]
        raise NotImplementedError()

    @property
    def tokens(self):  # type: () -> List[str]
        raise NotImplementedError()

    def has_token(self, token):  # type: (str) -> bool
        raise NotImplementedError()

    def to_string(self, script_name=True):  # type: (bool) -> str
        raise NotImplementedError()

    @property
    def option_tokens(self):  # type: () -> List[str]
        raise NotImplementedError()
        return list(itertools.takewhile(lambda arg: arg != "--", self.tokens))

    def has_option_token(self, token):  # type: (str) -> bool
        raise NotImplementedError()
