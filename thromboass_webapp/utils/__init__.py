from os import urandom
import logging

from thromboass_webapp.settings import BASE_URL

def generate_random_sequence(length=10):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join([chars[ord(c) % len(chars)] for c in urandom(length)])
    
 
def get_preview(self, text):
    MAX_LEN = 100
    if len(text) > MAX_LEN:
        return '{}...'.format(text[:MAX_LEN - len('...')])
    return text
 
        
def log(**kwargs):
    logger = logging.getLogger('DEFAULT')
    log_func = getattr(logger, kwargs.get('level', 'debug'))
    log_func(logger, kwargs.get('message'))
    
def generate_url(*steps, **args):
    query = ''
    if args:
        query = '?' + '&'.join(map(lambda x: '{}={}'.format(x, args.get(x)), args.keys()))
    return  '/'.join(['', ] + [unicode(step) for step in steps]) + query

def generate_email_url(*steps, **args):
    return BASE_URL + generate_url(*steps, **args)
