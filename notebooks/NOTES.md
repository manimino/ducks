
## RAM use of different object ID collections

Each index in a hashbox is a dict of {key: collection of integer object IDs}.

We need RAM-efficient collections of integers. Let's look at the options...

Bytes per integer, by collection size

|              | 1     | 10   | 50   | 100  | 1000 | 10000  |
|--------------|-------|------|------|------|------|--------|
| Python tuple | 56.8  | 14.0 | 9.3  | 8.6  | 32.2 | 39.7   |
| Python set   | 235.6 | 82.1 | 46.0 | 84.5 | 57.2 | 84.6   |
| cykhash set  | 168.5 | 26.5 | 23.6 | 22.3 | 17.0 | 13.6   |
| numpy array  | 169.6 | 23.4 | 11.1 | 9.6  | 8.2  | 8.0    |


So, storing integers in **Python tuples** of **size 1** costs 56.8 bytes / integer. Storing the same integers
in numpy arrays of size 10,000 costs 8 bytes / integer.

RAM usage was measured at the process level using `psutil.Process(os.getpid()).memory_info().rss`.

It's worth noting that Python tuples and numpy arrays have worse mutability. Removing an item from either one takes
O(n). So `cykhash set` is the best general-case answer. If we remove the mutability requirement,
numpy arrays are the most space-efficient.

In practice, some keys will have many objects (high cardinality) while many keys will have
few objects (low cardinality). We need efficiency in both.

----

## Handling low cardinality

It's possible to pack several low-cardinality keys into a single container.

We could have a bucket for every 100 items, and hash each key to land in one of those buckets. 
Consistent hashing would prevent needing to rehash everything as the HashBox grows.

Any one bucket would contain several keys. During lookup, we'd fetch the whole bucket, and 
do an equality check on each of the objects to find just the key we want.

This is the method used by [Postgres's HashBox](https://www.postgresql.org/docs/current/hash-intro.html).

It can backfire: suppose we have a few large keys that together make up 90% of the values.
If any two of them hash to the same bucket, untangling them would be very inefficient. We could avert this problem by
storing each high-cardinality key (say, >1% of the dataset) in its own devoted location.

----

## Freeze

Numpy arrays are up to 10x faster than Python sets or cykash sets. They also use less RAM. The downside is that 
mutability is worse; removes and updates become very slow.

The `freeze()` method of hashbox converts the containers from cykhash sets to numpy arrays, and prevents future
changes to the data structure. 

Making the index immutable also helps in multithreaded situations. With no writes, multiple threads
can access the hashbox simultaneously with no risk of concurrency bugs.
