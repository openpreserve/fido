from test.test_support import TestFailed, have_unicode

class base_set:

    def __init__(self, el):
        self.el = el

class set(base_set):

    def __contains__(self, el):
        return self.el == el

class seq(base_set):

    def __getitem__(self, n):
        return [self.el][n]

def check(ok, *args):
    if not ok:
        raise TestFailed, " ".join(map(str, args))

a = base_set(1)
b = set(1)
c = seq(1)

check(1 in b, "1 not in set(1)")
check(0 not in b, "0 in set(1)")
check(1 in c, "1 not in seq(1)")
check(0 not in c, "0 in seq(1)")

try:
    1 in a
    check(0, "in base_set did not raise error")
except TypeError:
    pass

try:
    1 not in a
    check(0, "not in base_set did not raise error")
except TypeError:
    pass

# Test char in string

check('c' in 'abc', "'c' not in 'abc'")
check('d' not in 'abc', "'d' in 'abc'")

check('' in '', "'' not in ''")
check('' in 'abc', "'' not in 'abc'")

try:
    None in 'abc'
    check(0, "None in 'abc' did not raise error")
except TypeError:
    pass


if have_unicode:

    # Test char in Unicode

    check('c' in unicode('abc'), "'c' not in u'abc'")
    check('d' not in unicode('abc'), "'d' in u'abc'")

    check('' in unicode(''), "'' not in u''")
    check(unicode('') in '', "u'' not in ''")
    check(unicode('') in unicode(''), "u'' not in u''")
    check('' in unicode('abc'), "'' not in u'abc'")
    check(unicode('') in 'abc', "u'' not in 'abc'")
    check(unicode('') in unicode('abc'), "u'' not in u'abc'")

    try:
        None in unicode('abc')
        check(0, "None in u'abc' did not raise error")
    except TypeError:
        pass

    # Test Unicode char in Unicode

    check(unicode('c') in unicode('abc'), "u'c' not in u'abc'")
    check(unicode('d') not in unicode('abc'), "u'd' in u'abc'")

    # Test Unicode char in string

    check(unicode('c') in 'abc', "u'c' not in 'abc'")
    check(unicode('d') not in 'abc', "u'd' in 'abc'")

# A collection of tests on builtin sequence types
a = range(10)
for i in a:
    check(i in a, "%r not in %r" % (i, a))
check(16 not in a, "16 not in %r" % (a,))
check(a not in a, "%s not in %r" % (a, a))

a = tuple(a)
for i in a:
    check(i in a, "%r not in %r" % (i, a))
check(16 not in a, "16 not in %r" % (a,))
check(a not in a, "%r not in %r" % (a, a))

class Deviant1:
    """Behaves strangely when compared

    This class is designed to make sure that the contains code
    works when the list is modified during the check.
    """

    aList = range(15)

    def __cmp__(self, other):
        if other == 12:
            self.aList.remove(12)
            self.aList.remove(13)
            self.aList.remove(14)
        return 1

check(Deviant1() not in Deviant1.aList, "Deviant1 failed")

class Deviant2:
    """Behaves strangely when compared

    This class raises an exception during comparison.  That in
    turn causes the comparison to fail with a TypeError.
    """

    def __cmp__(self, other):
        if other == 4:
            raise RuntimeError, "gotcha"

try:
    check(Deviant2() not in a, "oops")
except TypeError:
    pass
