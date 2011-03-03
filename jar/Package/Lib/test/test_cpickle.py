import cPickle
import unittest
from cStringIO import StringIO
from test.pickletester import AbstractPickleTests, AbstractPickleModuleTests
from test import test_support

class cPickleTests(AbstractPickleTests, AbstractPickleModuleTests):

    def setUp(self):
        self.dumps = cPickle.dumps
        self.loads = cPickle.loads

    error = cPickle.BadPickleGet
    module = cPickle

class cPicklePicklerTests(AbstractPickleTests):

    def dumps(self, arg, proto=0):
        f = StringIO()
        p = cPickle.Pickler(f, proto)
        p.dump(arg)
        f.seek(0)
        return f.read()

    def loads(self, buf):
        f = StringIO(buf)
        p = cPickle.Unpickler(f)
        return p.load()

    error = cPickle.BadPickleGet

class cPickleListPicklerTests(AbstractPickleTests):

    def dumps(self, arg, proto=0):
        p = cPickle.Pickler(proto)
        p.dump(arg)
        return p.getvalue()

    def loads(self, *args):
        f = StringIO(args[0])
        p = cPickle.Unpickler(f)
        return p.load()

    error = cPickle.BadPickleGet

class cPickleFastPicklerTests(AbstractPickleTests):

    def dumps(self, arg, proto=0):
        f = StringIO()
        p = cPickle.Pickler(f, proto)
        p.fast = 1
        p.dump(arg)
        f.seek(0)
        return f.read()

    def loads(self, *args):
        f = StringIO(args[0])
        p = cPickle.Unpickler(f)
        return p.load()

    error = cPickle.BadPickleGet

    def test_recursive_list(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_list,
                          self)

    def test_recursive_inst(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_inst,
                          self)

    def test_recursive_dict(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_dict,
                          self)

    def test_recursive_multi(self):
        self.assertRaises(ValueError,
                          AbstractPickleTests.test_recursive_multi,
                          self)

    def test_nonrecursive_deep(self):
        # If it's not cyclic, it should pickle OK even if the nesting
        # depth exceeds PY_CPICKLE_FAST_LIMIT.  That happens to be
        # 50 today.  Jack Jansen reported stack overflow on Mac OS 9
        # at 64.
        a = []
        for i in range(60):
            a = [a]
        b = self.loads(self.dumps(a))
        self.assertEqual(a, b)

def test_main():
    tests = [
        cPickleTests,
        cPicklePicklerTests,
        cPickleListPicklerTests,
        cPickleFastPicklerTests
    ]
    if test_support.is_jython:
        # XXX: Jython doesn't support list based picklers
        tests.remove(cPickleListPicklerTests)
        # XXX: These don't cause exceptions on Jython
        del cPickleFastPicklerTests.test_recursive_list
        del cPickleFastPicklerTests.test_recursive_inst
        del cPickleFastPicklerTests.test_recursive_dict
        del cPickleFastPicklerTests.test_recursive_multi
    test_support.run_unittest(*tests)

if __name__ == "__main__":
    test_main()
