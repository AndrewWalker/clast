# Jinja filters for use with clastgen
# none of this is particularly challenging to write directly in jinja, but it
# helps with clarity

__all__ = ['clast_jinja_filters']

def enum_parent(e):
    """Return the name of the parent type of the enumeration.

    If the enum doesn't have a parent, this will be the module, 
    otherwise it will be the exported name of the Python class
    the values need to be added to
    """
    if e['parent'] is not None:
        return 'm.attr("%s")' % e['parent'].split('::')[-1] 
    else:
        return 'm'

def argpack(args, call=True):
    if call:
        return ', '.join(n or '' for _, n in args)
    else:
        return ' '.join(', %s %s' % (t, n or '') for t, n in args)

def respack(method):
    if method['result_type'] == 'void':
        return ''
    else:
        return '-> %s' % method['result_type']

def retpack(method):
    if method['result_type'] == 'void':
        return ''
    else:
        return 'return' 

def disabled(o):
    return '//' if o['is_disabled'] else ''

def fdeleter(c):
    if 'deleter' in c:
        return ', %s' % c['deleter']
    else:
        return ''

def baseclass(c):
    if len(c['supers']) > 0:
        return ', py::base<%s>()' % c['supers'][0]
    else:
        return ''

def mthd_const(m):
    if m['const']:
        return 'const'
    else:
        return ''

def clast_jinja_filters():
    d = {}
    d['argpack'] = argpack
    d['respack'] = respack
    d['retpack'] = retpack
    d['disabled'] = disabled
    d['fdeleter']  = fdeleter
    d['enum_parent'] = enum_parent
    d['baseclass'] = baseclass
    d['mthd_const'] = mthd_const 
    return d


