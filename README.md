RateLimiting
=======

Simple Python utility for rate limiting.

Overview
-------------

This package provides the `rate_limiting` module, which ensures that an
operation will not be execute more than a given number of times on a given
period. This can prove useful when working with third parties APIs which
require for example a maximum of 10 requests per second.

Usage
-------------

Decorator flavor:

    >>> from rate_limiting import RateLimiting
    >>> @RateLimiting(max_calls=10, period=1.0)
    ... def do_something():
    ...     pass
    ...

Context manager flavor:

    >>> from rate_limiting import RateLimiting
    >>> rate_limiter = RateLimiting(max_calls=10, period=1.0)
    >>> for i in range(100):
    ...     with rate_limiter:
    ...         do_something()
    ...
