from __future__ import unicode_literals

from .alignment import Alignment
from .border_style import BorderStyle


class TableStyle:
    """
    Defines the style of a Table
    """

    _borderless = None

    _ascii = None

    _solid = None

    def __init__(self):  # type: () -> None
        self.padding_char = " "
        self.header_cell_format = "{}"
        self.cell_format = "{}"
        self.column_alignments = []
        self.default_column_alignment = Alignment.LEFT

        self.border_style = None
        self.header_cell_style = None
        self.cell_style = None

    def get_column_alignments(self, nb_columns):  # type: (int) -> List[int]
        default_alignments = [self.default_column_alignment] * nb_columns

        for i, alignment in enumerate(self.column_alignments):
            default_alignments[i] = alignment

        return default_alignments

    def set_column_alignment(self, col, alignment):  # type: (int, int) -> TableStyle
        if col > len(self.column_alignments) - 1:
            diff = abs(len(self.column_alignments) - col) + 1

            self.column_alignments += [self.default_column_alignment] * diff

        self.column_alignments[col] = alignment

    @classmethod
    def borderless(cls):  # type: () -> TableStyle
        style = TableStyle()
        style.border_style = BorderStyle.none()
        style.border_style.line_hc_char = "="
        style.border_style.line_vc_char = " "
        style.border_style.crossing_c_char = " "

        return style

    @classmethod
    def compact(cls):  # type: () -> TableStyle
        style = TableStyle()
        style.border_style = BorderStyle.none()
        style.border_style.line_hc_char = ""
        style.border_style.line_vc_char = " "
        style.border_style.crossing_c_char = ""

        return style

    @classmethod
    def ascii(cls):  # type: () -> TableStyle
        style = TableStyle()
        style.header_cell_format = " {} "
        style.cell_format = " {} "
        style.border_style = BorderStyle.ascii()

        return style

    @classmethod
    def solid(cls):  # type: () -> TableStyle
        style = TableStyle()
        style.header_cell_format = " {} "
        style.cell_format = " {} "
        style.border_style = BorderStyle.solid()

        return style
