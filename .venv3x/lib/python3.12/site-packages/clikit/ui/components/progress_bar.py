# -*- coding: utf-8 -*-
from __future__ import division

import time
import re
import math

from typing import Union

from clikit.api.io import IO
from clikit.api.io.flags import DEBUG
from clikit.api.io.flags import VERBOSE
from clikit.api.io.flags import VERY_VERBOSE
from clikit.api.io.section_output import SectionOutput
from clikit.api.io.output import Output
from clikit.utils.terminal import Terminal
from clikit.utils.time import format_time


class ProgressBar(object):
    """
    The ProgressBar provides helpers to display progress output.
    """

    # Options
    bar_width = 28
    bar_char = None
    empty_bar_char = "-"
    progress_char = ">"
    redraw_freq = 1

    formats = {
        "normal": " %current%/%max% [%bar%] %percent:3s%%",
        "normal_nomax": " %current% [%bar%]",
        "verbose": " %current%/%max% [%bar%] %percent:3s%% %elapsed:-6s%",
        "verbose_nomax": " %current% [%bar%] %elapsed:6s%",
        "very_verbose": " %current%/%max% [%bar%] %percent:3s%% %elapsed:6s%/%estimated:-6s%",
        "very_verbose_nomax": " %current% [%bar%] %elapsed:6s%",
        "debug": " %current%/%max% [%bar%] %percent:3s%% %elapsed:6s%/%estimated:-6s%",
        "debug_nomax": " %current% [%bar%] %elapsed:6s%",
    }

    def __init__(
        self, io, max=0, min_seconds_between_redraws=0.1
    ):  # type: (Union[IO, Output], int, float) -> None
        """
        Constructor.
        """
        # If we have an IO, ensure we write to the error output
        if isinstance(io, IO):
            io = io.error_output

        self._io = io
        self._terminal = Terminal()
        self._max = 0
        self._step_width = None
        self._set_max_steps(max)
        self._step = 0
        self._percent = 0.0
        self._format = None
        self._internal_format = None
        self._format_line_count = 0
        self._last_messages_length = 0
        self._should_overwrite = True
        self._min_seconds_between_redraws = 0
        self._max_seconds_between_redraws = 1
        self._write_count = 0

        if min_seconds_between_redraws > 0:
            self.redraw_freq = None
            self._min_seconds_between_redraws = min_seconds_between_redraws

        if not self._io.supports_ansi():
            # Disable overwrite when output does not support ANSI codes.
            self._should_overwrite = False

            # Set a reasonable redraw frequency so output isn't flooded
            self.redraw_freq = None

        self._messages = {}

        self._start_time = time.time()
        self._last_write_time = 0

    def set_message(self, message, name="message"):
        self._messages[name] = message

    def get_message(self, name="message"):
        return self._messages[name]

    def get_start_time(self):
        return self._start_time

    def get_max_steps(self):
        return self._max

    def get_progress(self):
        return self._step

    def get_progress_percent(self):
        return self._percent

    def set_bar_character(self, character):
        self.bar_char = character

        return self

    def get_bar_character(self):
        if self.bar_char is None:
            if self._max:
                return "="

            return self.empty_bar_char

        return self.bar_char

    def get_bar_width(self):
        return self.bar_width

    def set_bar_width(self, width):
        self.bar_width = width

        return self

    def get_empty_bar_character(self):
        return self.empty_bar_char

    def set_empty_bar_character(self, character):
        self.empty_bar_char = character

        return self

    def get_progress_character(self):
        return self.progress_char

    def set_progress_character(self, character):
        self.progress_char = character

        return self

    def set_format(self, fmt):
        self._format = None
        self._internal_format = fmt

    def set_redraw_frequency(self, freq):
        if self.redraw_freq is not None:
            self.redraw_freq = max(freq, 1)

    def min_seconds_between_redraws(self, freq):  # type:  (float) -> None
        if freq > 0:
            self.redraw_freq = None
            self._min_seconds_between_redraws = freq

    def max_seconds_between_redraws(self, freq):  # type: (float) -> None
        self._max_seconds_between_redraws = freq

    def start(self, max=None):
        """
        Start the progress output.
        """
        self._start_time = time.time()
        self._step = 0
        self._percent = 0.0

        if max is not None:
            self._set_max_steps(max)

        self.display()

    def advance(self, step=1):
        """
        Advances the progress output X steps.
        """
        self.set_progress(self._step + step)

    def set_progress(self, step):
        """
        Sets the current progress.

        :param step: The current progress
        :type step: int
        """
        if self._max and step > self._max:
            self._max = step
        elif step < 0:
            step = 0

        redraw_freq = (
            (self._max or 10) / 10 if self.redraw_freq is None else self.redraw_freq
        )
        prev_period = int(self._step / redraw_freq)
        curr_period = int(step / redraw_freq)

        self._step = step

        if self._max:
            self._percent = self._step / self._max
        else:
            self._percent = 0.0

        time_interval = time.time() - self._last_write_time

        # Draw regardless of other limits
        if step == self._max:
            self.display()

            return

        # Throttling
        if time_interval < self._min_seconds_between_redraws:
            return

        # Draw each step period, but not too late
        if (
            prev_period != curr_period
            or time_interval >= self._max_seconds_between_redraws
        ):
            self.display()

    def finish(self):
        """
        Finish the progress output.
        """
        if not self._max:
            self._max = self._step

        if self._step == self._max and not self._should_overwrite:
            return

        self.set_progress(self._max)

    def display(self):
        """
        Output the current progress string.
        """
        if self._io.is_quiet():
            return

        if self._format is None:
            self._set_real_format(
                self._internal_format or self._determine_best_format()
            )

        self._overwrite(
            re.sub(
                r"(?i)%([a-z\-_]+)(?::([^%]+))?%",
                self._overwrite_callback,
                self._format,
            )
        )

    def _overwrite_callback(self, matches):
        if hasattr(self, "_formatter_{}".format(matches.group(1))):
            text = str(getattr(self, "_formatter_{}".format(matches.group(1)))())
        elif matches.group(1) in self._messages:
            text = self._messages[matches.group(1)]
        else:
            return matches.group(0)

        if matches.group(2):
            if matches.group(2).startswith("-"):
                text = text.ljust(int(matches.group(2).lstrip("-").rstrip("s")))
            else:
                text = text.rjust(int(matches.group(2).rstrip("s")))

        return text

    def clear(self):
        """
        Removes the progress bar from the current line.

        This is useful if you wish to write some output
        while a progress bar is running.
        Call display() to show the progress bar again.
        """
        if not self._should_overwrite:
            return

        if self._format is None:
            self._set_real_format(
                self._internal_format or self._determine_best_format()
            )

        self._overwrite("\n" * self._format_line_count)

    def _set_real_format(self, fmt):
        """
        Sets the progress bar format.
        """
        # try to use the _nomax variant if available
        if not self._max and fmt + "_nomax" in self.formats:
            self._format = self.formats[fmt + "_nomax"]
        elif fmt in self.formats:
            self._format = self.formats[fmt]
        else:
            self._format = fmt

        self._format_line_count = self._format.count("\n")

    def _set_max_steps(self, mx):
        """
        Sets the progress bar maximal steps.
        """
        self._max = max(0, mx)

        if self._max:
            self._step_width = len(str(self._max))
        else:
            self._step_width = 4

    def _overwrite(self, message):
        """
        Overwrites a previous message to the output.
        """
        lines = message.split("\n")

        # Append whitespace to match the line's length
        if self._last_messages_length is not None:
            for i, line in enumerate(lines):
                if self._last_messages_length > len(self._io.remove_format(line)):
                    lines[i] = line.ljust(self._last_messages_length, "\x20")

        if self._should_overwrite:
            if isinstance(self._io, SectionOutput):
                lines_to_clear = (
                    int(math.floor(len(lines) / self._terminal.width))
                    + self._format_line_count
                    + 1
                )
                self._io.clear(lines_to_clear)
            else:
                # move back to the beginning of the progress bar before redrawing it
                self._io.write("\x0D")

                if self._format_line_count:
                    self._io.write("\033[{}A".format(self._format_line_count))
        elif self._step > 0:
            # move to new line
            self._io.write_line("")

        self._io.write("\n".join(lines))
        self._io.flush()

        self._last_messages_length = 0

        for line in lines:
            length = len(self._io.remove_format(line))
            if length > self._last_messages_length:
                self._last_messages_length = length

        self._last_write_time = time.time()
        self._write_count += 1

    def _determine_best_format(self):
        verbosity = self._io.verbosity

        if verbosity == VERBOSE:
            if self._max:
                return "verbose"

            return "verbose_nomax"
        elif verbosity == VERY_VERBOSE:
            if self._max:
                return "very_verbose"

            return "very_verbose_nomax"
        elif verbosity == DEBUG:
            if self._max:
                return "debug"

            return "debug_nomax"

        if self._max:
            return "normal"

        return "normal_nomax"

    @property
    def bar_offset(self):  # type: () -> int
        if self._max:
            return math.floor(self._percent * self.bar_width)
        else:
            if self.redraw_freq is None:
                return math.floor(
                    (min(5, self.get_bar_width() / 15) * self._write_count)
                    % self.bar_width
                )

            return math.floor(self._step % self.bar_width)

    def _formatter_bar(self):
        complete_bars = self.bar_offset

        display = self.get_bar_character() * int(complete_bars)

        if complete_bars < self.bar_width:
            empty_bars = (
                self.bar_width
                - complete_bars
                - len(self._io.remove_format(self.progress_char))
            )
            display += self.progress_char + self.empty_bar_char * int(empty_bars)

        return display

    def _formatter_elapsed(self):
        return format_time(time.time() - self._start_time)

    def _formatter_remaining(self):
        if not self._max:
            raise RuntimeError(
                "Unable to display the remaining time "
                "if the maximum number of steps is not set."
            )

        if not self._step:
            remaining = 0
        else:
            remaining = round(
                (time.time() - self._start_time) / self._step * (self._max - self._max)
            )

        return format_time(remaining)

    def _formatter_estimated(self):
        if not self._max:
            raise RuntimeError(
                "Unable to display the estimated time "
                "if the maximum number of steps is not set."
            )

        if not self._step:
            estimated = 0
        else:
            estimated = round((time.time() - self._start_time) / self._step * self._max)

        return estimated

    def _formatter_current(self):
        return str(self._step).rjust(self._step_width, " ")

    def _formatter_max(self):
        return self._max

    def _formatter_percent(self):
        return int(math.floor(self._percent * 100))
