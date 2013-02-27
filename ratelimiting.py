import collections
import functools
import time


class RateLimiting(object):
    """Provides rate limiting for an operation with a configurable number of
    requests for a time period.
    """

    def __init__(self, max_calls, period=1.0):
        """Initialze a RateLimiting objects which enforces as much as max_calls
        operations on period (eventually floating) number of seconds.
        """
        if period <= 0:
            raise ValueError('Rate limiting period should be > 0')
        if max_calls <= 0:
            raise ValueError('Rate limiting number of calls should be > 0')

        # We're using a deque to store the last execution timestamps, not for
        # its maxlen attribute, but to allow constant time front removal.
        self.calls = collections.deque()

        self.period = period
        self.max_calls = max_calls

    def __call__(self, f):
        """The __call__ function allows the RateLimiting object to be used as a
        regular function decorator.
        """
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with self:
                return f(*args, **kwargs)
        return wrapped

    def __enter__(self):
        # We want to ensure that no more than max_calls were run in the allowed
        # period. For this, we store the last timestamps of each call and run
        # the rate verification upon each __enter__ call.
        if len(self.calls) >= self.max_calls:
            time.sleep(self.period - self._timespan)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Store the last operation timestamp.
        self.calls.append(time.time())

        # Pop the timestamp list front (ie: the older calls) until the sum goes
        # back below the period. This is our 'sliding period' window.
        while self._timespan >= self.period:
            self.calls.popleft()

    @property
    def _timespan(self):
        return self.calls[-1] - self.calls[0]
