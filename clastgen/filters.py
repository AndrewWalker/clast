# Jinja filters for use with clastgen
# none of this is particularly challenging to write directly in jinja, but it
# helps with clarity

__all__ = ['clast_jinja_filters']

def enum_parent(e):
    if e['parent'] is not None:
        return 'm.attr("%s")' % e['parent'].split('::')[-1] 
    else:
        return 'm'

def argpack(method, call=True):
    if call:
        return ', '.join(n for n in method['arg_names'])
    else:
        return ' '.join(', %s %s' % (t, n) for t, n in zip(method['arg_types'], method['arg_names']))

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

def clast_jinja_filters():
    d = {}
    d['argpack'] = argpack
    d['respack'] = respack
    d['retpack'] = retpack
    d['disabled'] = disabled
    d['fdeleter']  = fdeleter
    d['enum_parent'] = enum_parent
    return d


