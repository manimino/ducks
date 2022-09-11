### Multicolumn indexing idea

User supplies a tuple of fields, like [a, b, c].

We don't simply store the tuple of values, no no. We store a class, with like __slots__ or something to make it ram 
efficient.

The key here is that the class has __gt__ defined, like so:

```
class MultiObject():

    def __init__(self, tuple):
        self.tuple = tuple  # holds a value for each field
    
    def __gt__(self, tuple):
        # TODO: this is possible totally wrong, just wanted to jot down the idea real quick. 
        # Will evaluate it more srsly later.
        return tuple[0] > self.tuple[0] and tuple[1] > self.tuple[1] and tuple[2] > self.tuple[2]
```

Then you can use an ordinary BTree or numpy array to compare these objects. 

Update works intuitively, you've got add / remove, EZPZ.

I think you can define __gt__ in such a way as it allows prefix queries. Not sure if that's a good design choice.
 
