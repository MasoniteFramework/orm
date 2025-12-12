from __future__ import unicode_literals

import math

from typing import List

from clikit.api.formatter import Style
from clikit.api.io import IO
from clikit.ui.style.alignment import Alignment
from clikit.ui.style.border_style import BorderStyle
from clikit.utils.string import get_string_length


class BorderUtil:
    """
    Contains utility methods to draw borders and bordered cells.
    """

    @classmethod
    def draw_top_border(
        cls, io, style, column_lengths, indentation=0
    ):  # type: (IO, BorderStyle, List[int], int) -> None
        cls.draw_border(
            io,
            column_lengths,
            indentation,
            style.line_ht_char,
            style.corner_tl_char,
            style.crossing_t_char,
            style.corner_tr_char,
            style.style,
        )

    @classmethod
    def draw_middle_border(
        cls, io, style, column_lengths, indentation=0
    ):  # type: (IO, BorderStyle, List[int], int) -> None
        cls.draw_border(
            io,
            column_lengths,
            indentation,
            style.line_hc_char,
            style.crossing_l_char,
            style.crossing_c_char,
            style.crossing_r_char,
            style.style,
        )

    @classmethod
    def draw_bottom_border(
        cls, io, style, column_lengths, indentation=0
    ):  # type: (IO, BorderStyle, List[int], int) -> None
        cls.draw_border(
            io,
            column_lengths,
            indentation,
            style.line_hb_char,
            style.corner_bl_char,
            style.crossing_b_char,
            style.corner_br_char,
            style.style,
        )

    @classmethod
    def draw_row(
        cls,
        io,
        style,
        row,
        column_lengths,
        alignments,
        cell_format,
        padding_char,
        cell_style=None,
        indentation=0,
    ):  # type: (IO, BorderStyle, List[str], List[int], List[int], str, str, Style, int) -> None
        total_lines = 0

        # Split all cells into lines
        for col, cell in enumerate(row):
            row[col] = cell.split("\n")
            total_lines = max(total_lines, len(row[col]))

        nb_columns = len(row)
        border_vl_char = io.format(style.line_vl_char, style.style)
        border_vc_char = io.format(style.line_vc_char, style.style)
        border_vr_char = io.format(style.line_vr_char, style.style)

        for i in range(total_lines):
            line = " " * indentation
            line += border_vl_char

            for col, remaining_lines in enumerate(row):
                if remaining_lines:
                    cell_line = remaining_lines.pop(0)
                else:
                    cell_line = ""

                total_pad_length = column_lengths[col] - get_string_length(
                    cell_line, io
                )
                padding_left = ""
                padding_right = ""

                if total_pad_length >= 0:
                    try:
                        alignment = alignments[col]
                    except IndexError:
                        alignment = Alignment.LEFT

                    if alignment == Alignment.LEFT:
                        padding_right = padding_char * total_pad_length
                    elif alignment == Alignment.RIGHT:
                        padding_left = padding_char * total_pad_length
                    else:
                        left_pad_length = int(math.floor(total_pad_length / 2))
                        padding_left = padding_char * left_pad_length
                        padding_right = padding_char * (
                            total_pad_length - left_pad_length
                        )

                    line += io.format(
                        cell_format.format(padding_left + cell_line + padding_right),
                        cell_style,
                    )
                    if col < nb_columns - 1:
                        line += border_vc_char
                    else:
                        line += border_vr_char

            # Remove trailing space
            io.write(line.rstrip() + "\n")

    @classmethod
    def draw_border(
        cls,
        io,
        column_lengths,
        indentation,
        line_char,
        crossing_l_char,
        crossing_c_char,
        crossing_r_char,
        style=None,
    ):  # type: (IO, List[int], int, str, str, str, str, Style) -> None
        line = " " * indentation
        line += crossing_l_char

        l = len(column_lengths)
        for i in range(l):
            line += line_char * column_lengths[i]
            if i < l - 1:
                line += crossing_c_char
            else:
                line += crossing_r_char

        line = line.rstrip()

        if line:
            io.write(io.format(line, style) + "\n")
