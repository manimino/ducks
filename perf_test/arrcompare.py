import numpy as np
from array import array

# Fixed size numpy array
def np_fixed(n):
    q = np.empty(n)
    for i in range(n):
        q[i] = i
    return q

# Resize with np.resize
def np_class_resize(isize, n):
    q = np.empty(isize)
    for i in range(n):
        if i>=q.shape[0]:
            q = np.resize(q, q.shape[0]*2)        
        q[i] = i
    return q    

# Resize with the numpy.array method
def np_method_resize(isize, n):
    q = np.empty(isize)
    for i in range(n):
        if i>=q.shape[0]:
            q.resize(q.shape[0]*2)
        q[i] = i
    return q

# Array.array append
def arr(n):
    q = array('d')
    for i in range(n):
        q.append(i)
    return q
