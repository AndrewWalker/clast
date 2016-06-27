import contextlib
import os


def npages(n, sz):
    if n % sz == 0:
        return n/sz
    else:
        return n/sz+1

def pagination(lst, chunksize):
    for j, i in enumerate(xrange(0, len(lst), chunksize)):
        yield j, i, i + chunksize
 
