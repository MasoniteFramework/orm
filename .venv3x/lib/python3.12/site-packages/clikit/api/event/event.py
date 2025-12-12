class Event(object):
    """
    Event
    """

    def __init__(self):  # type: () -> None
        self._propagation_stopped = False

    def is_propagation_stopped(self):  # type: () -> bool
        return self._propagation_stopped

    def stop_propagation(self):  # type: () -> None
        self._propagation_stopped = True
