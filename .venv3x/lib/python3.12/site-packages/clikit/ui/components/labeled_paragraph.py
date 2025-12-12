from __future__ import unicode_literals

import re
import textwrap

from clikit.api.io import IO
from clikit.ui import Component


class LabeledParagraph(Component):
    """
    A paragraph with a label on its left.
    """

    def __init__(
        self, label, text, padding=2, aligned=True
    ):  # type: (str, str, int, bool) -> None
        self._label = label
        self._text = text
        self._padding = padding
        self._aligned = aligned
        self._alignment = None

    @property
    def label(self):  # type: () -> str
        return self._label

    @property
    def text(self):  # type: () -> str
        return self._text

    @property
    def padding(self):  # type: () -> int
        return self._padding

    def is_aligned(self):  # type: () -> bool
        return self._aligned

    def set_alignment(self, alignment):  # type: (LabelAlignment) -> None
        self._alignment = alignment

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        line_prefix = " " * indentation
        visible_label = io.remove_format(self._label)
        style_tag_length = len(self._label) - len(visible_label)

        if self._aligned and self._alignment:
            text_offset = self._alignment.text_offset - indentation
        else:
            text_offset = 0

        text_offset = max(text_offset, len(visible_label) + self._padding)
        text_prefix = " " * text_offset

        # 1 trailing space
        text_width = io.terminal_dimensions.width - 1 - text_offset - indentation
        text = re.sub(
            r"\n(?!\n)",
            "\n" + line_prefix + text_prefix,
            "\n".join(textwrap.wrap(self._text, text_width)),
        )

        # Add the total length of the style tags ("<b>", ...)
        label_width = text_offset + style_tag_length

        io.write(
            "{}{:<{}}{}".format(
                line_prefix, self._label, label_width, text.rstrip()
            ).rstrip()
            + "\n"
        )
