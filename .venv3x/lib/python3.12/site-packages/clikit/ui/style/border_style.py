# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from clikit.api.formatter import Style


class BorderStyle:
    """
    Defines the style of a border.
    """

    _none = None
    _ascii = None
    _solid = None

    def __init__(self):  # type: () -> None
        self.line_ht_char = "-"
        self.line_hc_char = "-"
        self.line_hb_char = "-"

        self.line_vl_char = "|"
        self.line_vc_char = "|"
        self.line_vr_char = "|"

        self.corner_tl_char = "+"
        self.corner_tr_char = "+"
        self.corner_bl_char = "+"
        self.corner_br_char = "+"

        self.crossing_c_char = "+"
        self.crossing_l_char = "+"
        self.crossing_t_char = "+"
        self.crossing_r_char = "+"
        self.crossing_b_char = "+"

        self.style = None  # type: Style

    @classmethod
    def none(cls):  # type: () -> BorderStyle
        if cls._none is None:
            style = cls()
            style.line_ht_char = ""
            style.line_hc_char = ""
            style.line_hb_char = ""

            style.line_vl_char = ""
            style.line_vc_char = " "
            style.line_vr_char = ""

            style.corner_tl_char = ""
            style.corner_tr_char = ""
            style.corner_bl_char = ""
            style.corner_br_char = ""

            style.crossing_c_char = ""
            style.crossing_l_char = ""
            style.crossing_t_char = ""
            style.crossing_r_char = ""
            style.crossing_b_char = ""

            cls._none = style

        return cls._none

    @classmethod
    def ascii(cls):  # type: () -> BorderStyle
        if cls._ascii is None:
            style = cls()

            cls._ascii = style

        return cls._ascii

    @classmethod
    def solid(cls):  # type: () -> BorderStyle
        if cls._solid is None:
            style = cls()
            style.line_ht_char = "─"
            style.line_hc_char = "─"
            style.line_hb_char = "─"

            style.line_vl_char = "│"
            style.line_vc_char = "│"
            style.line_vr_char = "│"

            style.corner_tl_char = "┌"
            style.corner_tr_char = "┐"
            style.corner_bl_char = "└"
            style.corner_br_char = "┘"

            style.crossing_c_char = "┼"
            style.crossing_l_char = "├"
            style.crossing_r_char = "┤"
            style.crossing_t_char = "┬"
            style.crossing_b_char = "┴"

            cls._solid = style

        return cls._solid
