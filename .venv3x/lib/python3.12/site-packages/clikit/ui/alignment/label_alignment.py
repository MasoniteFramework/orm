from typing import List

from clikit.api.formatter import Formatter
from clikit.ui.components import LabeledParagraph


class LabelAlignment:
    """
    Aligns labeled paragraphs.
    """

    def __init__(self):  # type: () -> None
        self._paragraphs = []  # type: List[LabeledParagraph]
        self._indentations = []  # type: List[int]
        self._text_offset = 0

    def add(self, paragraph, indentation=0):  # type: (LabeledParagraph, int) -> None
        if paragraph.is_aligned():
            self._paragraphs.append(paragraph)
            self._indentations.append(indentation)

    def align(self, formatter, indentation=0):  # type: (Formatter, int) -> None
        self._text_offset = 0

        for i, paragraph in enumerate(self._paragraphs):
            label = formatter.remove_format(paragraph.label)
            text_offset = self._indentations[i] + len(label) + paragraph.padding

            self._text_offset = max(self._text_offset, text_offset)

        self._text_offset += indentation

    def set_text_offset(self, offset):  # type: (int) -> None
        self._text_offset = offset

    @property
    def text_offset(self):  # type: () -> int
        return self._text_offset
