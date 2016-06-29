import collections

Page = collections.namedtuple('Page', ['idx', 'start', 'end'])

def pagination(lst, chunksize=20):
    for j, i in enumerate(xrange(0, len(lst), chunksize)):
        yield Page(j, i, i + chunksize)
 
