from contextlib import contextmanager

from clikit.api.io import IO
from clikit.ui import Component
from clikit.ui.alignment import LabelAlignment
from clikit.ui.components import LabeledParagraph


class BlockLayout:
    """
    Renders renderable objects in indented blocks.
    """

    def __init__(self):  # type: () -> None
        self._current_indentation = 0
        self._elements = []
        self._indentations = []
        self._alignment = LabelAlignment()

    def add(self, element):  # type: (Component) -> BlockLayout
        self._elements.append(element)
        self._indentations.append(self._current_indentation)

        if isinstance(element, LabeledParagraph):
            self._alignment.add(element, self._current_indentation)
            element.set_alignment(self._alignment)

        return self

    @contextmanager
    def block(self):  # type: () -> BlockLayout
        self._current_indentation += 2

        yield self

        self._current_indentation -= 2

    def render(self, io, indentation=0):  # type: (IO, int) -> None
        self._alignment.align(io, indentation)

        for i, element in enumerate(self._elements):
            element.render(io, self._indentations[i] + indentation)

        self._elements = []
