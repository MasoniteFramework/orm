from __future__ import division

import textwrap

from typing import List

from clikit.api.formatter import Formatter
from clikit.utils.string import get_max_line_length
from clikit.utils.string import get_max_word_length
from clikit.utils.string import get_string_length


class CellWrapper:
    """
    Wraps cells to fit a given screen width with a given number of columns.
    """

    def __init__(self):  # type: () -> None
        self._cells = []
        self._cell_lengths = []
        self._wrapped_rows = []
        self._nb_columns = 0
        self._column_lengths = []
        self._word_wraps = False
        self._word_cuts = False
        self._max_total_width = 0
        self._total_width = 0

    @property
    def cells(self):  # type: () -> List[str]
        return self._cells

    @property
    def wrapped_rows(self):  # type: () -> List[List[str]]
        return self._wrapped_rows

    @property
    def column_lengths(self):  # type: () -> List[int]
        return self._column_lengths

    @property
    def nb_columns(self):  # type: () -> int
        return self._nb_columns

    @property
    def max_total_width(self):  # type: () -> int
        return self._max_total_width

    @property
    def total_width(self):  # type: () -> int
        return self._total_width

    def add_cell(self, cell):  # type: (str) -> CellWrapper
        self._cells.append(cell.rstrip())

        return self

    def add_cells(self, cells):  # type: (List[str]) -> CellWrapper
        for cell in cells:
            self.add_cell(cell)

        return self

    def get_estimated_nb_columns(self, max_total_width):  # type: (int) -> int
        """
        Returns an estimated number of columns for the given maximum width.
        """
        row_width = 0

        for i, cell in enumerate(self._cells):
            row_width += get_string_length(cell)

            if row_width > max_total_width:
                return i

        return len(self._cells) - 1

    def has_word_wraps(self):  # type: () -> bool
        return self._word_wraps

    def has_word_cuts(self):  # type: () -> bool
        return self._word_cuts

    def fit(
        self, max_total_width, nb_columns, formatter
    ):  # type: (int, int, Formatter) -> None
        self._reset_state(max_total_width, nb_columns)
        self._init_rows(formatter)

        # If the cells fit within the max width we're good
        if self._total_width <= max_total_width:
            return

        self._wrap_columns(formatter)

    def _reset_state(self, max_total_width, nb_columns):  # type: (int, int) -> None
        self._wrapped_rows = []
        self._nb_columns = nb_columns
        self._cell_lengths = []
        self._column_lengths = [0] * nb_columns
        self._word_wraps = False
        self._word_cuts = False
        self._max_total_width = max_total_width
        self._total_width = 0

    def _init_rows(self, formatter):  # type: (Formatter) -> None
        col = 0

        for i, cell in enumerate(self._cells):
            if col == 0:
                self._wrapped_rows.append([""] * self._nb_columns)
                self._cell_lengths.append([0] * self._nb_columns)

            self._wrapped_rows[-1][col] = cell
            self._cell_lengths[-1][col] = get_string_length(cell, formatter)
            self._column_lengths[col] = max(
                self._column_lengths[col], self._cell_lengths[-1][col]
            )

            col = (col + 1) % self._nb_columns

        # Fill last row
        if col > 0:
            while col < self._nb_columns:
                self._wrapped_rows[-1][col] = ""
                self._cell_lengths[-1][col] = 0
                col += 1

        self._total_width = sum(self._column_lengths)

    def _wrap_columns(self, formatter):  # type: (Formatter) -> None
        available_width = self._max_total_width
        long_column_lengths = self._column_lengths[:]

        # Filter "short" column, i.e. columns that are not wrapped
        # We distribute the available screen width by the number of columns
        # and decide that all columns that are shorter than their share are
        # "short".
        # This process is repeated until no more "short" columns are found.
        repeat = True
        while repeat:
            threshold = available_width / len(long_column_lengths)
            repeat = False

            for col, length in enumerate(long_column_lengths):
                if length is not None and length <= threshold:
                    available_width -= length
                    long_column_lengths[col] = None
                    repeat = True

        # Calculate actual and available width
        actual_width = 0
        last_adapted_col = 0

        # "Long" columns, i.e. columns that need to be wrapped, are added to
        # the actual width
        for col, length in enumerate(long_column_lengths):
            if length is None:
                continue

            actual_width += length
            last_adapted_col = col

        # Fit columns into available width
        for col, length in enumerate(long_column_lengths):
            if length is None:
                continue

            # Keep ratios of column lengths and distribute them among the
            # available width
            self._column_lengths[col] = int(
                round((length / actual_width) * available_width)
            )

            if col == last_adapted_col:
                # Fix rounding errors
                self._column_lengths[col] += self._max_total_width - sum(
                    self._column_lengths
                )

            self._wrap_column(col, self._column_lengths[col], formatter)

            # Recalculate the column length based on the actual wrapped length
            self._refresh_column_length(col)

            # Recalculate the actual width based on the changed length.
            actual_width = actual_width - length + self._column_lengths[col]

        self._total_width = sum(self._column_lengths)

    def _wrap_column(
        self, col, column_length, formatter
    ):  # type: (int, List[int], Formatter) -> None
        for i, row in enumerate(self._wrapped_rows):
            cell = row[col]
            cell_length = self._cell_lengths[i][col]

            if cell_length > column_length:
                self._word_wraps = True

                if not self._word_cuts:
                    min_length_without_cut = get_max_word_length(cell, formatter)

                    if min_length_without_cut > column_length:
                        self._word_cuts = True

                # TODO: use format aware wrapper
                wrapped_cell = "\n".join(textwrap.wrap(cell, column_length))

                self._wrapped_rows[i][col] = wrapped_cell

                # Refresh cell length
                self._cell_lengths[i][col] = get_max_line_length(
                    wrapped_cell, formatter
                )

    def _refresh_column_length(self, col):  # type: (int) -> None
        self._column_lengths[col] = 0

        for i, row in enumerate(self._wrapped_rows):
            self._column_lengths[col] = max(
                self._column_lengths[col], self._cell_lengths[i][col]
            )
