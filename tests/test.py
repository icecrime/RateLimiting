import random
import time
import unittest

from rate_limiting import RateLimiting


class Timer(object):

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop = time.time()
        self.duration = self.stop - self.start


class TestBasic(unittest.TestCase):

    period = 0.1
    max_calls = 10

    def setUp(self):
        random.seed()

    def validate_call_times(self, ts, max_calls, period):
        # Overall verification: total call duration should span over more than
        # the corresponding number of periods.
        self.assertGreaterEqual(ts[-1] - ts[0], (len(ts) % max_calls) * period)

        # Sliding verification: no group of 'max_calls' items should span over
        # less than a period.
        for i in range(len(ts) - max_calls):
            self.assertGreaterEqual(ts[i + max_calls] - ts[i], period)

    def test_bad_args(self):
        self.assertRaises(ValueError, RateLimiting, -1, self.period)
        self.assertRaises(ValueError, RateLimiting, +1, -self.period)

    def test_limit_1(self):
        with Timer() as timer:
            obj = RateLimiting(self.max_calls, self.period)
            for i in range(11):
                with obj:
                    pass
        self.assertGreaterEqual(timer.duration, self.period)

    def test_limit_2(self):
        calls = []
        obj = RateLimiting(self.max_calls, self.period)
        for i in range(3 * self.max_calls):
            with obj:
                calls.append(time.time())

        self.assertEqual(len(calls), 3 * self.max_calls)
        self.validate_call_times(calls, self.max_calls, self.period)

    def test_decorator_1(self):
        @RateLimiting(self.max_calls, self.period)
        def f():
            pass

        with Timer() as timer:
            [f() for i in range(11)]

        self.assertGreaterEqual(timer.duration, self.period)

    def test_decorator_2(self):
        @RateLimiting(self.max_calls, self.period)
        def f():
            f.calls.append(time.time())
        f.calls = []

        [f() for i in range(3 * self.max_calls)]

        self.assertEqual(len(f.calls), 3 * self.max_calls)
        self.validate_call_times(f.calls, self.max_calls, self.period)

    def test_random(self):
        calls = []
        obj = RateLimiting(self.max_calls, self.period)
        for i in range(random.randint(10, 50)):
            with obj:
                time.sleep(random.random())
                calls.append(time.time())

        self.validate_call_times(calls, self.max_calls, self.period)


if __name__ == "__main__":
    unittest.main()
