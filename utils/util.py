from random import choice
import string

#return a randomized alphanumerical string with a
#number of characters equal to length
def rand_key(length=12):
    built = ''.join([choice(string.letters+string.digits) for i in range(length)])
    return built



def ordinal(n):
	"""borrowed from John Machin's python-list post.  Appends an
	ordinal suffix to a number.  For example, 1 becomes 1st,
	2 becomes 2nd, etc."""
	if 10 <= n % 100 < 20:
		return str(n) + 'th'
	else:
		return  str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, "th")



def str_to_array(str):
    arr = []
    str = str[1:len(str)-1] #strip '[' and ']'
    toks = str.split(',')
    for tok in toks:
        if tok:
            # list field is insisting on making the
            # ids "2L" rather than "2", so convert
            # through a long
            arr.append(int(long(tok.strip())))

    return arr
