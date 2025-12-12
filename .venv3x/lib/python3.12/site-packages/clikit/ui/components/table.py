from typing import List
from typing import Optional

from clikit.api.formatter import Formatter
from clikit.api.io import IO
from clikit.ui import Component
from clikit.ui.components import BorderUtil
from clikit.ui.components import CellWrapper
from clikit.ui.style import TableStyle
from clikit.utils.string import get_string_length


class Table(Component):
    """
    A table of rows and columns.
    """

    def __init__(self, style=None):  # type: (Optional[TableStyle]) -> None
        self._header_row = []
        self._rows = []
        self._nb_columns = None

        if style is None:
            style = TableStyle.ascii()

        self._style = style

    def set_header_row(self, row):  # type: (List[str]) -> Table
        if self._nb_columns is None:
            self._nb_columns = len(row)
        elif len(row) != self._nb_columns:
            raise ValueError(
                "Expected the header row to contain {} cells, but got {}.".format(
                    self._nb_columns, len(row)
                )
            )

        self._header_row = row

        return self

    def add_row(self, row):  # type: (List[str]) -> Table
        if self._nb_columns is None:
            self._nb_columns = len(row)
        elif len(row) != self._nb_columns:
            raise ValueError(
                "Expected the row to contain {} cells, but got {}.".format(
                    self._nb_columns, len(row)
                )
            )

        self._rows.append(row)

        return self

    def add_rows(self, rows):  # type: (List[List[str]]) -> Table
        for row in rows:
            self.add_row(row)

        return self

    def set_rows(self, rows):  # type: (List[List[str]]) -> Table
        self._rows = []

        for row in rows:
            self.add_row(row)

        return self

    def set_row(self, index, row):  # type: (int, List[str]) -> Table
        if len(row) != self._nb_columns:
            raise ValueError(
                "Expected the row to contain {} cells, but got {}.".format(
                    self._nb_columns, len(row)
                )
            )

        self._rows[index] = row

        return self

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        if not self._rows:
            return

        screen_width = io.terminal_dimensions.width
        excess_column_width = max(
            get_string_length(self._style.header_cell_format.format("")),
            get_string_length(self._style.cell_format.format("")),
        )

        wrapper = self._get_cell_wrapper(
            io, screen_width, excess_column_width, indentation
        )

        return self._render_rows(
            io,
            wrapper.wrapped_rows,
            wrapper.column_lengths,
            excess_column_width,
            indentation,
        )

    def _get_cell_wrapper(
        self, formatter, screen_width, excess_column_width, indentation
    ):  # type: (Formatter, int, int, int) -> CellWrapper
        border_style = self._style.border_style
        border_width = (
            get_string_length(border_style.line_vl_char)
            + (self._nb_columns - 1) * get_string_length(border_style.line_vc_char)
            + get_string_length(border_style.line_vr_char)
        )
        available_width = (
            screen_width
            - indentation
            - border_width
            - self._nb_columns * excess_column_width
        )

        wrapper = CellWrapper()

        for header_cell in self._header_row:
            wrapper.add_cell(header_cell)

        for row in self._rows:
            for cell in row:
                wrapper.add_cell(cell)

        wrapper.fit(available_width, self._nb_columns, formatter)

        return wrapper

    def _render_rows(
        self, io, rows, column_lengths, excess_column_length, indentation
    ):  # type: (IO, List[List[str]], List[int], int, int) -> None
        alignments = self._style.get_column_alignments(len(column_lengths))
        border_style = self._style.border_style
        border_column_lengths = [
            length + excess_column_length for length in column_lengths
        ]

        BorderUtil.draw_top_border(io, border_style, border_column_lengths, indentation)

        if self._header_row:
            BorderUtil.draw_row(
                io,
                border_style,
                rows.pop(0),
                column_lengths,
                alignments,
                self._style.header_cell_format,
                self._style.padding_char,
                self._style.header_cell_style,
                indentation,
            )

            BorderUtil.draw_middle_border(
                io, border_style, border_column_lengths, indentation
            )

        for row in rows:
            BorderUtil.draw_row(
                io,
                border_style,
                row,
                column_lengths,
                alignments,
                self._style.cell_format,
                self._style.padding_char,
                self._style.cell_style,
                indentation,
            )

        BorderUtil.draw_bottom_border(
            io, border_style, border_column_lengths, indentation
        )
