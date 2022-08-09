## How It Works, Concurrent Edition

It contains a mutable FilterBox, and wraps each method in `with read_lock()` or `with write_lock()`.

There's a [performance test notebook](/examples/concurrent_perf.ipynb) showing the impact of locking
on single-threaded operation. Each lock operation adds about 5µs. Not huge, but enough to add up when doing
many operations in a row.

For this reason, the `read_lock()` and `write_lock()` methods are exposed. This allows patterns like:
```
cfb = ConcurrentFilterBox(...)
with cfb.write_lock()
    for item in a_million_items:
        cfb.box.add(item)  # cfb.box is the underlying FilterBox.
```
which are faster than calling `cfb.add` many times.

Concurrency bugs are notoriously tricky to find. ConcurrentFilterBox is unlikely to have them because:
 - It uses a very simple, coarse-grained concurrency that locks the whole object for every read and write
 - It's built on a widely-used [lock library](https://github.com/elarivie/pyReaderWriterLock)
 - There are concurrent operation tests that succeed on ConcurrentFilterBox and fail on FilterBox, proving the
  locks are working properly (see `tests/concurrent`).
