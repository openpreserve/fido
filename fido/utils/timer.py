from time import perf_counter


class PerfTimer:
    """Utility class that carries out simple process timings."""

    def __init__(self):
        """New instance with start time running."""
        self.start_time = perf_counter()

    def start(self):
        """Start new timer."""
        self.start_time = perf_counter()

    def duration(self):
        """Return the duration since instantiation or start() was last called."""
        return perf_counter() - self.start_time
