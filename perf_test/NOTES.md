### 


### Object ids in a Python set() when large, tuple() when small

=== MatchIndex Test: 100000 items, 1 indices ===
MatchIndex Make: 0.08395
Linear Find:  2e-06
MatchIndex Find: 0.003461
List mem size:    48001856
MatchIndex mem size: 60889736
=== MatchIndex Test: 1000000 items, 10 indices ===
MatchIndex Make: 5.753338
Linear Find:  2e-06
MatchIndex Find: 0.005257
List mem size:    480452480
MatchIndex mem size: 1070498472

### After changing to cykhash

=== MatchIndex Test: 100000 items, 1 indices ===
MatchIndex Make: 0.07586
Linear Find:  2e-06
MatchIndex Find: 0.004796
List mem size:    48001856
MatchIndex mem size: 55645016
=== MatchIndex Test: 1000000 items, 10 indices ===
MatchIndex Make: 4.949894
Linear Find:  2e-06
MatchIndex Find: 0.021131
List mem size:    480452480

Interesting that lookups got slower on the large set but not the small.
