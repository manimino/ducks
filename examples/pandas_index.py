"""
Demo - Using Ducks as an indexer for Pandas

Pandas allows index columns and even supports multi-column indexing.
https://pandas.pydata.org/pandas-docs/stable/user_guide/advanced.html
However, its use is not very intuitive. If you'd rather use a Dex, here's how.
"""

import random

import pandas as pd
from ducks import FrozenDex

# make some objects
objs = [
    {
        'fruit': random.choice(['apple', 'banana', 'cherry', 'kiwi', 'lime', 'watermelon']),
        'size': i % 10
    }
    for i in range(1000)
]

# put them in a dataframe
df = pd.DataFrame(objs)


# make lookup functions that match attributes to dataframe rows
def get_fruit(i):
    """Get the fruit for this position in the df"""
    return df.iloc[i]['fruit']


def get_size(i):
    return df.iloc[i]['size']


# Build index
dex = FrozenDex(list(range(len(df))), [get_fruit, get_size])


# Perform index lookups
rows = df.iloc[
    dex[
        {
            get_fruit: 'apple',
            get_size: {'>=': 8}
        }
    ]
]
print(rows)
