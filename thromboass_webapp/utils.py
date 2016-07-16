from os import urandom

def generate_random_sequence(length=10):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join([chars[ord(c) % len(chars)] for c in urandom(length)])
    
 
def get_preview(self, text):
    MAX_LEN = 100
    if len(text) > MAX_LEN:
        return '{}...'.format(text[:MAX_LEN - len('...')])
    return text
