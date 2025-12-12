import math

from typing import List
from typing import Optional

from clikit.api.formatter import Formatter
from clikit.utils.terminal import Terminal

from .output import Output
from .output_stream import OutputStream


class SectionOutput(Output):
    def __init__(
        self, stream, sections, formatter=None
    ):  # type: (OutputStream, List[SectionOutput], Optional[Formatter]) -> None
        super(SectionOutput, self).__init__(stream, formatter=formatter)

        self._content = []
        self._lines = 0
        sections.insert(0, self)
        self._sections = sections
        self._terminal = Terminal()

    @property
    def content(self):  # type: () -> str
        return "".join(self._content)

    @property
    def lines(self):  # type: () -> int
        return self._lines

    def clear(self, lines=None):  # type: (Optional[int]) -> None
        if (
            not self._content
            or not self.supports_ansi()
            and not self._formatter.force_ansi()
        ):
            return

        if lines:
            # Multiply lines by 2 to cater for each new line added between content
            del self._content[-(lines * 2) :]
        else:
            lines = self._lines
            self._content = []

        self._lines -= lines

        super(SectionOutput, self).write(
            self._pop_stream_content_until_current_section(lines)
        )

    def overwrite(self, message):  # type: (str) -> None
        self.clear()
        self.write_line(message)

    def add_content(self, content):  # type: (str) -> None
        for line_content in content.split("\n"):
            self._lines += (
                math.ceil(
                    len(self.remove_format(line_content).replace("\t", "        "))
                    / self._terminal.width
                )
                or 1
            )
            self._content.append(line_content)
            self._content.append("\n")

    def write(
        self, string, flags=None, new_line=False
    ):  # type: (str, Optional[int], bool) -> None
        if not self.supports_ansi() and not self._formatter.force_ansi():
            return super(SectionOutput, self).write(string, flags=flags)

        erased_content = self._pop_stream_content_until_current_section()

        self.add_content(string)

        super(SectionOutput, self).write(string, new_line=True)
        super(SectionOutput, self).write(erased_content)

    def _pop_stream_content_until_current_section(
        self, lines_to_clear_count=0
    ):  # type: (int) -> str
        erased_content = []

        for section in self._sections:
            if section is self:
                break

            lines_to_clear_count += section.lines
            erased_content.append(section.content)

        if lines_to_clear_count > 0:
            # Move cursor up n lines
            super(SectionOutput, self).write("\x1b[{}A".format(lines_to_clear_count))
            # Erase to end of screen
            super(SectionOutput, self).write("\x1b[0J")

        return "".join(reversed(erased_content))
