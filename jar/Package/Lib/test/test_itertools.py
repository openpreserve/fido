import unittest
from test import test_support
from itertools import *
from weakref import proxy
import sys
import operator
import random

def onearg(x):
    'Test function of one argument'
    return 2*x

def errfunc(*args):
    'Test function that raises an error'
    raise ValueError

def gen3():
    'Non-restartable source sequence'
    for i in (0, 1, 2):
        yield i

def isEven(x):
    'Test predicate'
    return x%2==0

def isOdd(x):
    'Test predicate'
    return x%2==1

class StopNow:
    'Class emulating an empty iterable.'
    def __iter__(self):
        return self
    def next(self):
        raise StopIteration

def take(n, seq):
    'Convenience function for partially consuming a long of infinite iterable'
    return list(islice(seq, n))

class TestBasicOps(unittest.TestCase):
    def test_chain(self):
        self.assertEqual(list(chain('abc', 'def')), list('abcdef'))
        self.assertEqual(list(chain('abc')), list('abc'))
        self.assertEqual(list(chain('')), [])
        self.assertEqual(take(4, chain('abc', 'def')), list('abcd'))
        self.assertRaises(TypeError, chain, 2, 3)

    def test_count(self):
        self.assertEqual(zip('abc',count()), [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(zip('abc',count(3)), [('a', 3), ('b', 4), ('c', 5)])
        self.assertEqual(take(2, zip('abc',count(3))), [('a', 3), ('b', 4)])
        self.assertRaises(TypeError, count, 2, 3)
        self.assertRaises(TypeError, count, 'a')
        c = count(sys.maxint-2)   # verify that rollover doesn't crash
        c.next(); c.next(); c.next(); c.next(); c.next()
        c = count(3)
        self.assertEqual(repr(c), 'count(3)')
        c.next()
        self.assertEqual(repr(c), 'count(4)')

    def test_cycle(self):
        self.assertEqual(take(10, cycle('abc')), list('abcabcabca'))
        self.assertEqual(list(cycle('')), [])
        self.assertRaises(TypeError, cycle)
        self.assertRaises(TypeError, cycle, 5)
        self.assertEqual(list(islice(cycle(gen3()),10)), [0,1,2,0,1,2,0,1,2,0])

    def test_groupby(self):
        # Check whether it accepts arguments correctly
        self.assertEqual([], list(groupby([])))
        self.assertEqual([], list(groupby([], key=id)))
        self.assertRaises(TypeError, list, groupby('abc', []))
        self.assertRaises(TypeError, groupby, None)
        self.assertRaises(TypeError, groupby, 'abc', lambda x:x, 10)

        # Check normal input
        s = [(0, 10, 20), (0, 11,21), (0,12,21), (1,13,21), (1,14,22),
             (2,15,22), (3,16,23), (3,17,23)]
        dup = []
        for k, g in groupby(s, lambda r:r[0]):
            for elem in g:
                self.assertEqual(k, elem[0])
                dup.append(elem)
        self.assertEqual(s, dup)

        # Check nested case
        dup = []
        for k, g in groupby(s, lambda r:r[0]):
            for ik, ig in groupby(g, lambda r:r[2]):
                for elem in ig:
                    self.assertEqual(k, elem[0])
                    self.assertEqual(ik, elem[2])
                    dup.append(elem)
        self.assertEqual(s, dup)

        # Check case where inner iterator is not used
        keys = [k for k, g in groupby(s, lambda r:r[0])]
        expectedkeys = set([r[0] for r in s])
        self.assertEqual(set(keys), expectedkeys)
        self.assertEqual(len(keys), len(expectedkeys))

        # Exercise pipes and filters style
        s = 'abracadabra'
        # sort s | uniq
        r = [k for k, g in groupby(sorted(s))]
        self.assertEqual(r, ['a', 'b', 'c', 'd', 'r'])
        # sort s | uniq -d
        r = [k for k, g in groupby(sorted(s)) if list(islice(g,1,2))]
        self.assertEqual(r, ['a', 'b', 'r'])
        # sort s | uniq -c
        r = [(len(list(g)), k) for k, g in groupby(sorted(s))]
        self.assertEqual(r, [(5, 'a'), (2, 'b'), (1, 'c'), (1, 'd'), (2, 'r')])
        # sort s | uniq -c | sort -rn | head -3
        r = sorted([(len(list(g)) , k) for k, g in groupby(sorted(s))], reverse=True)[:3]
        self.assertEqual(r, [(5, 'a'), (2, 'r'), (2, 'b')])

        # iter.next failure
        class ExpectedError(Exception):
            pass
        def delayed_raise(n=0):
            for i in range(n):
                yield 'yo'
            raise ExpectedError
        def gulp(iterable, keyp=None, func=list):
            return [func(g) for k, g in groupby(iterable, keyp)]

        # iter.next failure on outer object
        self.assertRaises(ExpectedError, gulp, delayed_raise(0))
        # iter.next failure on inner object
        #self.assertRaises(ExpectedError, gulp, delayed_raise(1))

        # __cmp__ failure
        class DummyCmp:
            def __cmp__(self, dst):
                raise ExpectedError
        s = [DummyCmp(), DummyCmp(), None]

        # __cmp__ failure on outer object
        #self.assertRaises(ExpectedError, gulp, s, func=id)
        # __cmp__ failure on inner object
        #self.assertRaises(ExpectedError, gulp, s)

        # keyfunc failure
        def keyfunc(obj):
            if keyfunc.skip > 0:
                keyfunc.skip -= 1
                return obj
            else:
                raise ExpectedError

        # keyfunc failure on outer object
        keyfunc.skip = 0
        self.assertRaises(ExpectedError, gulp, [None], keyfunc)
        keyfunc.skip = 1
        self.assertRaises(ExpectedError, gulp, [None, None], keyfunc)

    def test_ifilter(self):
        self.assertEqual(list(ifilter(isEven, range(6))), [0,2,4])
        self.assertEqual(list(ifilter(None, [0,1,0,2,0])), [1,2])
        self.assertEqual(take(4, ifilter(isEven, count())), [0,2,4,6])
        self.assertRaises(TypeError, ifilter)
        self.assertRaises(TypeError, ifilter, lambda x:x)
        self.assertRaises(TypeError, ifilter, lambda x:x, range(6), 7)
        self.assertRaises(TypeError, ifilter, isEven, 3)
        self.assertRaises(TypeError, ifilter(range(6), range(6)).next)

    def test_ifilterfalse(self):
        self.assertEqual(list(ifilterfalse(isEven, range(6))), [1,3,5])
        self.assertEqual(list(ifilterfalse(None, [0,1,0,2,0])), [0,0,0])
        self.assertEqual(take(4, ifilterfalse(isEven, count())), [1,3,5,7])
        self.assertRaises(TypeError, ifilterfalse)
        self.assertRaises(TypeError, ifilterfalse, lambda x:x)
        self.assertRaises(TypeError, ifilterfalse, lambda x:x, range(6), 7)
        self.assertRaises(TypeError, ifilterfalse, isEven, 3)
        self.assertRaises(TypeError, ifilterfalse(range(6), range(6)).next)

    def test_izip(self):
        ans = [(x,y) for x, y in izip('abc',count())]
        self.assertEqual(ans, [('a', 0), ('b', 1), ('c', 2)])
        self.assertEqual(list(izip('abc', range(6))), zip('abc', range(6)))
        self.assertEqual(list(izip('abcdef', range(3))), zip('abcdef', range(3)))
        self.assertEqual(take(3,izip('abcdef', count())), zip('abcdef', range(3)))
        self.assertEqual(list(izip('abcdef')), zip('abcdef'))
        self.assertEqual(list(izip()), zip())
        self.assertRaises(TypeError, izip, 3)
        self.assertRaises(TypeError, izip, range(3), 3)
        # Check tuple re-use (implementation detail)
        self.assertEqual([tuple(list(pair)) for pair in izip('abc', 'def')],
                         zip('abc', 'def'))
        self.assertEqual([pair for pair in izip('abc', 'def')],
                         zip('abc', 'def'))
        # Does not apply to Jython - no tuple reuse
#         ids = map(id, izip('abc', 'def'))
#         self.assertEqual(min(ids), max(ids))
        ids = map(id, list(izip('abc', 'def')))
        self.assertEqual(len(dict.fromkeys(ids)), len(ids))

    def test_repeat(self):
        self.assertEqual(zip(xrange(3),repeat('a')),
                         [(0, 'a'), (1, 'a'), (2, 'a')])
        self.assertEqual(list(repeat('a', 3)), ['a', 'a', 'a'])
        self.assertEqual(take(3, repeat('a')), ['a', 'a', 'a'])
        self.assertEqual(list(repeat('a', 0)), [])
        self.assertEqual(list(repeat('a', -3)), [])
        self.assertRaises(TypeError, repeat)
        self.assertRaises(TypeError, repeat, None, 3, 4)
        self.assertRaises(TypeError, repeat, None, 'a')
        r = repeat(1+0j)
        self.assertEqual(repr(r), 'repeat((1+0j))')
        r = repeat(1+0j, 5)
        self.assertEqual(repr(r), 'repeat((1+0j), 5)')
        list(r)
        self.assertEqual(repr(r), 'repeat((1+0j), 0)')

    def test_imap(self):
        self.assertEqual(list(imap(operator.pow, range(3), range(1,7))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(list(imap(None, 'abc', range(5))),
                         [('a',0),('b',1),('c',2)])
        self.assertEqual(list(imap(None, 'abc', count())),
                         [('a',0),('b',1),('c',2)])
        self.assertEqual(take(2,imap(None, 'abc', count())),
                         [('a',0),('b',1)])
        self.assertEqual(list(imap(operator.pow, [])), [])
        self.assertRaises(TypeError, imap)
        self.assertRaises(TypeError, imap, operator.neg)
        self.assertRaises(TypeError, imap(10, range(5)).next)
        self.assertRaises(ValueError, imap(errfunc, [4], [5]).next)
        self.assertRaises(TypeError, imap(onearg, [4], [5]).next)

    def test_starmap(self):
        self.assertEqual(list(starmap(operator.pow, zip(range(3), range(1,7)))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(take(3, starmap(operator.pow, izip(count(), count(1)))),
                         [0**1, 1**2, 2**3])
        self.assertEqual(list(starmap(operator.pow, [])), [])
        self.assertRaises(TypeError, list, starmap(operator.pow, [[4,5]]))
        self.assertRaises(TypeError, starmap)
        self.assertRaises(TypeError, starmap, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, starmap(10, [(4,5)]).next)
        self.assertRaises(ValueError, starmap(errfunc, [(4,5)]).next)
        self.assertRaises(TypeError, starmap(onearg, [(4,5)]).next)

    def test_islice(self):
        for args in [          # islice(args) should agree with range(args)
                (10, 20, 3),
                (10, 3, 20),
                (10, 20),
                (10, 3),
                (20,)
                ]:
            self.assertEqual(list(islice(xrange(100), *args)), range(*args))

        for args, tgtargs in [  # Stop when seqn is exhausted
                ((10, 110, 3), ((10, 100, 3))),
                ((10, 110), ((10, 100))),
                ((110,), (100,))
                ]:
            self.assertEqual(list(islice(xrange(100), *args)), range(*tgtargs))

        # Test stop=None
        self.assertEqual(list(islice(xrange(10), None)), range(10))
        self.assertEqual(list(islice(xrange(10), None, None)), range(10))
        self.assertEqual(list(islice(xrange(10), None, None, None)), range(10))
        self.assertEqual(list(islice(xrange(10), 2, None)), range(2, 10))
        self.assertEqual(list(islice(xrange(10), 1, None, 2)), range(1, 10, 2))

        # Test number of items consumed     SF #1171417
        it = iter(range(10))
        self.assertEqual(list(islice(it, 3)), range(3))
        self.assertEqual(list(it), range(3, 10))

        # Test invalid arguments
        self.assertRaises(TypeError, islice, xrange(10))
        self.assertRaises(TypeError, islice, xrange(10), 1, 2, 3, 4)
        self.assertRaises(ValueError, islice, xrange(10), -5, 10, 1)
        self.assertRaises(ValueError, islice, xrange(10), 1, -5, -1)
        self.assertRaises(ValueError, islice, xrange(10), 1, 10, -1)
        self.assertRaises(ValueError, islice, xrange(10), 1, 10, 0)
        self.assertRaises(ValueError, islice, xrange(10), 'a')
        self.assertRaises(ValueError, islice, xrange(10), 'a', 1)
        self.assertRaises(ValueError, islice, xrange(10), 1, 'a')
        self.assertRaises(ValueError, islice, xrange(10), 'a', 1, 1)
        self.assertRaises(ValueError, islice, xrange(10), 1, 'a', 1)
        self.assertEqual(len(list(islice(count(), 1, 10, sys.maxint))), 1)

    def test_takewhile(self):
        data = [1, 3, 5, 20, 2, 4, 6, 8]
        underten = lambda x: x<10
        self.assertEqual(list(takewhile(underten, data)), [1, 3, 5])
        self.assertEqual(list(takewhile(underten, [])), [])
        self.assertRaises(TypeError, takewhile)
        self.assertRaises(TypeError, takewhile, operator.pow)
        self.assertRaises(TypeError, takewhile, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, takewhile(10, [(4,5)]).next)
        self.assertRaises(ValueError, takewhile(errfunc, [(4,5)]).next)
        t = takewhile(bool, [1, 1, 1, 0, 0, 0])
        self.assertEqual(list(t), [1, 1, 1])
        self.assertRaises(StopIteration, t.next)

    def test_dropwhile(self):
        data = [1, 3, 5, 20, 2, 4, 6, 8]
        underten = lambda x: x<10
        self.assertEqual(list(dropwhile(underten, data)), [20, 2, 4, 6, 8])
        self.assertEqual(list(dropwhile(underten, [])), [])
        self.assertRaises(TypeError, dropwhile)
        self.assertRaises(TypeError, dropwhile, operator.pow)
        self.assertRaises(TypeError, dropwhile, operator.pow, [(4,5)], 'extra')
        self.assertRaises(TypeError, dropwhile(10, [(4,5)]).next)
        self.assertRaises(ValueError, dropwhile(errfunc, [(4,5)]).next)

    def test_tee(self):
        n = 200
        def irange(n):
            for i in xrange(n):
                yield i

        a, b = tee([])        # test empty iterator
        self.assertEqual(list(a), [])
        self.assertEqual(list(b), [])

        a, b = tee(irange(n)) # test 100% interleaved
        self.assertEqual(zip(a,b), zip(range(n),range(n)))

        a, b = tee(irange(n)) # test 0% interleaved
        self.assertEqual(list(a), range(n))
        self.assertEqual(list(b), range(n))

        a, b = tee(irange(n)) # test dealloc of leading iterator
        for i in xrange(100):
            self.assertEqual(a.next(), i)
        del a
        self.assertEqual(list(b), range(n))

        a, b = tee(irange(n)) # test dealloc of trailing iterator
        for i in xrange(100):
            self.assertEqual(a.next(), i)
        del b
        self.assertEqual(list(a), range(100, n))

        for j in xrange(5):   # test randomly interleaved
            order = [0]*n + [1]*n
            random.shuffle(order)
            lists = ([], [])
            its = tee(irange(n))
            for i in order:
                value = its[i].next()
                lists[i].append(value)
            self.assertEqual(lists[0], range(n))
            self.assertEqual(lists[1], range(n))

        # test argument format checking
        self.assertRaises(TypeError, tee)
        self.assertRaises(TypeError, tee, 3)
        self.assertRaises(TypeError, tee, [1,2], 'x')
        self.assertRaises(TypeError, tee, [1,2], 3, 'x')

        # tee object should be instantiable
        a, b = tee('abc')
        c = type(a)('def')
        self.assertEqual(list(c), list('def'))

        # test long-lagged and multi-way split
        a, b, c = tee(xrange(2000), 3)
        for i in xrange(100):
            self.assertEqual(a.next(), i)
        self.assertEqual(list(b), range(2000))
        self.assertEqual([c.next(), c.next()], range(2))
        self.assertEqual(list(a), range(100,2000))
        self.assertEqual(list(c), range(2,2000))

        # test values of n
        self.assertRaises(TypeError, tee, 'abc', 'invalid')
        self.assertRaises(ValueError, tee, [], -1)
        for n in xrange(5):
            result = tee('abc', n)
            self.assertEqual(type(result), tuple)
            self.assertEqual(len(result), n)
            self.assertEqual(map(list, result), [list('abc')]*n)

        # tee pass-through to copyable iterator
        a, b = tee('abc')
        c, d = tee(a)
        # JYTHON TODO: we do not currently implement copy
        # self.assert_(a is c)

        # test tee_new
        t1, t2 = tee('abc')
        tnew = type(t1)
        self.assertRaises(TypeError, tnew)
        self.assertRaises(TypeError, tnew, 10)
        t3 = tnew(t1)

        # JYTHON: this tests that copy is transitive
        #self.assert_(list(t1) == list(t2) == list(t3) == list('abc'))
        self.assert_(list(t3) == list(t2) == list('abc'))
        # test that tee objects are weak referencable
        a, b = tee(xrange(10))
        p = proxy(a)
        self.assertEqual(getattr(p, '__class__'), type(b))
        del a
        # JYTHON: this depends on `a` actually going out of scope; we
        # would have to play with GC to make it so

        # self.assertRaises(ReferenceError, getattr, p, '__class__')

    def test_StopIteration(self):
        self.assertRaises(StopIteration, izip().next)

        for f in (chain, cycle, izip, groupby):
            self.assertRaises(StopIteration, f([]).next)
            self.assertRaises(StopIteration, f(StopNow()).next)

        self.assertRaises(StopIteration, islice([], None).next)
        self.assertRaises(StopIteration, islice(StopNow(), None).next)

        p, q = tee([])
        self.assertRaises(StopIteration, p.next)
        self.assertRaises(StopIteration, q.next)
        p, q = tee(StopNow())
        self.assertRaises(StopIteration, p.next)
        self.assertRaises(StopIteration, q.next)

        self.assertRaises(StopIteration, repeat(None, 0).next)

        for f in (ifilter, ifilterfalse, imap, takewhile, dropwhile, starmap):
            self.assertRaises(StopIteration, f(lambda x:x, []).next)
            self.assertRaises(StopIteration, f(lambda x:x, StopNow()).next)

class TestGC(unittest.TestCase):

    def makecycle(self, iterator, container):
        container.append(iterator)
        iterator.next()
        del container, iterator

    def test_chain(self):
        a = []
        self.makecycle(chain(a), a)

    def test_cycle(self):
        a = []
        self.makecycle(cycle([a]*2), a)

    def test_dropwhile(self):
        a = []
        self.makecycle(dropwhile(bool, [0, a, a]), a)

    def test_groupby(self):
        a = []
        self.makecycle(groupby([a]*2, lambda x:x), a)

    def test_ifilter(self):
        a = []
        self.makecycle(ifilter(lambda x:True, [a]*2), a)

    def test_ifilterfalse(self):
        a = []
        self.makecycle(ifilterfalse(lambda x:False, a), a)

    def test_izip(self):
        a = []
        self.makecycle(izip([a]*2, [a]*3), a)

    def test_imap(self):
        a = []
        self.makecycle(imap(lambda x:x, [a]*2), a)

    def test_islice(self):
        a = []
        self.makecycle(islice([a]*2, None), a)

    def test_repeat(self):
        a = []
        self.makecycle(repeat(a), a)

    def test_starmap(self):
        a = []
        self.makecycle(starmap(lambda *t: t, [(a,a)]*2), a)

    def test_takewhile(self):
        a = []
        self.makecycle(takewhile(bool, [1, 0, a, a]), a)

def R(seqn):
    'Regular generator'
    for i in seqn:
        yield i

class G:
    'Sequence using __getitem__'
    def __init__(self, seqn):
        self.seqn = seqn
    def __getitem__(self, i):
        return self.seqn[i]

class I:
    'Sequence using iterator protocol'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self
    def next(self):
        if self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        return v

class Ig:
    'Sequence using iterator protocol defined with a generator'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        for val in self.seqn:
            yield val

class X:
    'Missing __getitem__ and __iter__'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def next(self):
        if self.i >= len(self.seqn): raise StopIteration
        v = self.seqn[self.i]
        self.i += 1
        return v

class N:
    'Iterator missing next()'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self

class E:
    'Test propagation of exceptions'
    def __init__(self, seqn):
        self.seqn = seqn
        self.i = 0
    def __iter__(self):
        return self
    def next(self):
        3 // 0

class S:
    'Test immediate stop'
    def __init__(self, seqn):
        pass
    def __iter__(self):
        return self
    def next(self):
        raise StopIteration

def L(seqn):
    'Test multiple tiers of iterators'
    return chain(imap(lambda x:x, R(Ig(G(seqn)))))


class TestVariousIteratorArgs(unittest.TestCase):

    def test_chain(self):
        for s in ("123", "", range(1000), ('do', 1.2), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(chain(g(s))), list(g(s)))
                self.assertEqual(list(chain(g(s), g(s))), list(g(s))+list(g(s)))
            self.assertRaises(TypeError, chain, X(s))
            self.assertRaises(TypeError, list, chain(N(s)))
            self.assertRaises(ZeroDivisionError, list, chain(E(s)))

    def test_cycle(self):
        for s in ("123", "", range(1000), ('do', 1.2), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                tgtlen = len(s) * 3
                expected = list(g(s))*3
                actual = list(islice(cycle(g(s)), tgtlen))
                self.assertEqual(actual, expected)
            self.assertRaises(TypeError, cycle, X(s))
            self.assertRaises(TypeError, list, cycle(N(s)))
            self.assertRaises(ZeroDivisionError, list, cycle(E(s)))

    def test_groupby(self):
        for s in (range(10), range(0), range(1000), (7,11), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                self.assertEqual([k for k, sb in groupby(g(s))], list(g(s)))
            self.assertRaises(TypeError, groupby, X(s))
            self.assertRaises(TypeError, list, groupby(N(s)))
            self.assertRaises(ZeroDivisionError, list, groupby(E(s)))

    def test_ifilter(self):
        for s in (range(10), range(0), range(1000), (7,11), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(ifilter(isEven, g(s))), filter(isEven, g(s)))
            self.assertRaises(TypeError, ifilter, isEven, X(s))
            self.assertRaises(TypeError, list, ifilter(isEven, N(s)))
            self.assertRaises(ZeroDivisionError, list, ifilter(isEven, E(s)))

    def test_ifilterfalse(self):
        for s in (range(10), range(0), range(1000), (7,11), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(ifilterfalse(isEven, g(s))), filter(isOdd, g(s)))
            self.assertRaises(TypeError, ifilterfalse, isEven, X(s))
            self.assertRaises(TypeError, list, ifilterfalse(isEven, N(s)))
            self.assertRaises(ZeroDivisionError, list, ifilterfalse(isEven, E(s)))

    def test_izip(self):
        for s in ("123", "", range(1000), ('do', 1.2), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(izip(g(s))), zip(g(s)))
                self.assertEqual(list(izip(g(s), g(s))), zip(g(s), g(s)))
            self.assertRaises(TypeError, izip, X(s))
            self.assertRaises(TypeError, list, izip(N(s)))
            self.assertRaises(ZeroDivisionError, list, izip(E(s)))

    def test_imap(self):
        for s in (range(10), range(0), range(100), (7,11), xrange(20,50,5)):
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(imap(onearg, g(s))), map(onearg, g(s)))
                self.assertEqual(list(imap(operator.pow, g(s), g(s))), map(operator.pow, g(s), g(s)))
            self.assertRaises(TypeError, imap, onearg, X(s))
            self.assertRaises(TypeError, list, imap(onearg, N(s)))
            self.assertRaises(ZeroDivisionError, list, imap(onearg, E(s)))

    def test_islice(self):
        for s in ("12345", "", range(1000), ('do', 1.2), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                self.assertEqual(list(islice(g(s),1,None,2)), list(g(s))[1::2])
            self.assertRaises(TypeError, islice, X(s), 10)
            self.assertRaises(TypeError, list, islice(N(s), 10))
            self.assertRaises(ZeroDivisionError, list, islice(E(s), 10))

    def test_starmap(self):
        for s in (range(10), range(0), range(100), (7,11), xrange(20,50,5)):
            for g in (G, I, Ig, S, L, R):
                ss = zip(s, s)
                self.assertEqual(list(starmap(operator.pow, g(ss))), map(operator.pow, g(s), g(s)))
            self.assertRaises(TypeError, starmap, operator.pow, X(ss))
            self.assertRaises(TypeError, list, starmap(operator.pow, N(ss)))
            self.assertRaises(ZeroDivisionError, list, starmap(operator.pow, E(ss)))

    def test_takewhile(self):
        for s in (range(10), range(0), range(1000), (7,11), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                tgt = []
                for elem in g(s):
                    if not isEven(elem): break
                    tgt.append(elem)
                self.assertEqual(list(takewhile(isEven, g(s))), tgt)
            self.assertRaises(TypeError, takewhile, isEven, X(s))
            self.assertRaises(TypeError, list, takewhile(isEven, N(s)))
            self.assertRaises(ZeroDivisionError, list, takewhile(isEven, E(s)))

    def test_dropwhile(self):
        for s in (range(10), range(0), range(1000), (7,11), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                tgt = []
                for elem in g(s):
                    if not tgt and isOdd(elem): continue
                    tgt.append(elem)
                self.assertEqual(list(dropwhile(isOdd, g(s))), tgt)
            self.assertRaises(TypeError, dropwhile, isOdd, X(s))
            self.assertRaises(TypeError, list, dropwhile(isOdd, N(s)))
            self.assertRaises(ZeroDivisionError, list, dropwhile(isOdd, E(s)))

    def test_tee(self):
        for s in ("123", "", range(1000), ('do', 1.2), xrange(2000,2200,5)):
            for g in (G, I, Ig, S, L, R):
                it1, it2 = tee(g(s))
                self.assertEqual(list(it1), list(g(s)))
                self.assertEqual(list(it2), list(g(s)))
            self.assertRaises(TypeError, tee, X(s))
            self.assertRaises(TypeError, list, tee(N(s))[0])
            self.assertRaises(ZeroDivisionError, list, tee(E(s))[0])

class LengthTransparency(unittest.TestCase):

    def test_repeat(self):
        from test.test_iterlen import len
        self.assertEqual(len(repeat(None, 50)), 50)
        self.assertRaises(TypeError, len, repeat(None))

class RegressionTests(unittest.TestCase):

    def test_sf_793826(self):
        # Fix Armin Rigo's successful efforts to wreak havoc

        def mutatingtuple(tuple1, f, tuple2):
            # this builds a tuple t which is a copy of tuple1,
            # then calls f(t), then mutates t to be equal to tuple2
            # (needs len(tuple1) == len(tuple2)).
            def g(value, first=[1]):
                if first:
                    del first[:]
                    f(z.next())
                return value
            items = list(tuple2)
            items[1:1] = list(tuple1)
            gen = imap(g, items)
            z = izip(*[gen]*len(tuple1))
            z.next()

        def f(t):
            global T
            T = t
            first[:] = list(T)

        first = []
        mutatingtuple((1,2,3), f, (4,5,6))
        second = list(T)
        self.assertEqual(first, second)


    def test_sf_950057(self):
        # Make sure that chain() and cycle() catch exceptions immediately
        # rather than when shifting between input sources

        def gen1():
            hist.append(0)
            yield 1
            hist.append(1)
            raise AssertionError
            hist.append(2)

        def gen2(x):
            hist.append(3)
            yield 2
            hist.append(4)
            if x:
                raise StopIteration

        hist = []
        self.assertRaises(AssertionError, list, chain(gen1(), gen2(False)))
        self.assertEqual(hist, [0,1])

        hist = []
        self.assertRaises(AssertionError, list, chain(gen1(), gen2(True)))
        self.assertEqual(hist, [0,1])

        hist = []
        self.assertRaises(AssertionError, list, cycle(gen1()))
        self.assertEqual(hist, [0,1])

libreftest = """ Doctest for examples in the library reference: libitertools.tex


>>> amounts = [120.15, 764.05, 823.14]
>>> for checknum, amount in izip(count(1200), amounts):
...     print 'Check %d is for $%.2f' % (checknum, amount)
...
Check 1200 is for $120.15
Check 1201 is for $764.05
Check 1202 is for $823.14

>>> import operator
>>> for cube in imap(operator.pow, xrange(1,4), repeat(3)):
...    print cube
...
1
8
27

>>> reportlines = ['EuroPython', 'Roster', '', 'alex', '', 'laura', '', 'martin', '', 'walter', '', 'samuele']
>>> for name in islice(reportlines, 3, None, 2):
...    print name.title()
...
Alex
Laura
Martin
Walter
Samuele

# >>> from operator import itemgetter
# >>> d = dict(a=1, b=2, c=1, d=2, e=1, f=2, g=3)
# >>> di = sorted(sorted(d.iteritems()), key=itemgetter(1))
# >>> for k, g in groupby(di, itemgetter(1)):
# ...     print k, map(itemgetter(0), g)
# ...
# 1 ['a', 'c', 'e']
# 2 ['b', 'd', 'f']
# 3 ['g']

# Find runs of consecutive numbers using groupby.  The key to the solution
# is differencing with a range so that consecutive numbers all appear in
# same group.
#>>> data = [ 1,  4,5,6, 10, 15,16,17,18, 22, 25,26,27,28]
# >>> for k, g in groupby(enumerate(data), lambda (i,x):i-x):
# ...     print map(operator.itemgetter(1), g)
# ...
# [1]
# [4, 5, 6]
# [10]
# [15, 16, 17, 18]
# [22]
# [25, 26, 27, 28]

>>> def take(n, seq):
...     return list(islice(seq, n))

>>> def enumerate(iterable):
...     return izip(count(), iterable)

>>> def tabulate(function):
...     "Return function(0), function(1), ..."
...     return imap(function, count())

>>> def iteritems(mapping):
...     return izip(mapping.iterkeys(), mapping.itervalues())

>>> def nth(iterable, n):
...     "Returns the nth item"
...     return list(islice(iterable, n, n+1))

>>> def all(seq, pred=None):
...     "Returns True if pred(x) is true for every element in the iterable"
...     for elem in ifilterfalse(pred, seq):
...         return False
...     return True

>>> def any(seq, pred=None):
...     "Returns True if pred(x) is true for at least one element in the iterable"
...     for elem in ifilter(pred, seq):
...         return True
...     return False

>>> def no(seq, pred=None):
...     "Returns True if pred(x) is false for every element in the iterable"
...     for elem in ifilter(pred, seq):
...         return False
...     return True

>>> def quantify(seq, pred=None):
...     "Count how many times the predicate is true in the sequence"
...     return sum(imap(pred, seq))

>>> def padnone(seq):
...     "Returns the sequence elements and then returns None indefinitely"
...     return chain(seq, repeat(None))

>>> def ncycles(seq, n):
...     "Returns the sequence elements n times"
...     return chain(*repeat(seq, n))

>>> def dotproduct(vec1, vec2):
...     return sum(imap(operator.mul, vec1, vec2))

>>> def flatten(listOfLists):
...     return list(chain(*listOfLists))

>>> def repeatfunc(func, times=None, *args):
...     "Repeat calls to func with specified arguments."
...     "   Example:  repeatfunc(random.random)"
...     if times is None:
...         return starmap(func, repeat(args))
...     else:
...         return starmap(func, repeat(args, times))

>>> def pairwise(iterable):
...     "s -> (s0,s1), (s1,s2), (s2, s3), ..."
...     a, b = tee(iterable)
...     try:
...         b.next()
...     except StopIteration:
...         pass
...     return izip(a, b)

This is not part of the examples but it tests to make sure the definitions
perform as purported.

>>> take(10, count())
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

>>> list(enumerate('abc'))
[(0, 'a'), (1, 'b'), (2, 'c')]

>>> list(islice(tabulate(lambda x: 2*x), 4))
[0, 2, 4, 6]

>>> nth('abcde', 3)
['d']

>>> all([2, 4, 6, 8], lambda x: x%2==0)
True

>>> all([2, 3, 6, 8], lambda x: x%2==0)
False

>>> any([2, 4, 6, 8], lambda x: x%2==0)
True

>>> any([1, 3, 5, 9], lambda x: x%2==0,)
False

>>> no([1, 3, 5, 9], lambda x: x%2==0)
True

>>> no([1, 2, 5, 9], lambda x: x%2==0)
False

>>> quantify(xrange(99), lambda x: x%2==0)
50

>>> a = [[1, 2, 3], [4, 5, 6]]
>>> flatten(a)
[1, 2, 3, 4, 5, 6]

>>> list(repeatfunc(pow, 5, 2, 3))
[8, 8, 8, 8, 8]

>>> import random
>>> take(5, imap(int, repeatfunc(random.random)))
[0, 0, 0, 0, 0]

>>> list(pairwise('abcd'))
[('a', 'b'), ('b', 'c'), ('c', 'd')]

>>> list(pairwise([]))
[]

>>> list(pairwise('a'))
[]

>>> list(islice(padnone('abc'), 0, 6))
['a', 'b', 'c', None, None, None]

>>> list(ncycles('abc', 3))
['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c']

>>> dotproduct([1,2,3], [4,5,6])
32

"""

__test__ = {'libreftest' : libreftest}

def test_main(verbose=None):
    test_classes = (TestBasicOps, TestVariousIteratorArgs, TestGC,
                    RegressionTests, LengthTransparency)
    test_support.run_unittest(*test_classes)

    # verify reference counting
    if verbose and hasattr(sys, "gettotalrefcount"):
        import gc
        counts = [None] * 5
        for i in xrange(len(counts)):
            test_support.run_unittest(*test_classes)
            gc.collect()
            counts[i] = sys.gettotalrefcount()
        print counts

    # doctest the examples in the library reference
    test_support.run_doctest(sys.modules[__name__], verbose)

if __name__ == "__main__":
    test_main(verbose=True)
