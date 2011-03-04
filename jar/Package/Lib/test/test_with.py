#!/usr/bin/env python

"""Unit tests for the with statement specified in PEP 343."""

from __future__ import with_statement

__author__ = "Mike Bland"
__email__ = "mbland at acm dot org"

import sys
import unittest
import StringIO
from collections import deque
from contextlib import GeneratorContextManager, contextmanager
from test.test_support import run_unittest


class MockContextManager(GeneratorContextManager):
    def __init__(self, gen):
        GeneratorContextManager.__init__(self, gen)
        self.enter_called = False
        self.exit_called = False
        self.exit_args = None

    def __enter__(self):
        self.enter_called = True
        return GeneratorContextManager.__enter__(self)

    def __exit__(self, type, value, traceback):
        self.exit_called = True
        self.exit_args = (type, value, traceback)
        return GeneratorContextManager.__exit__(self, type,
                                                value, traceback)


def mock_contextmanager(func):
    def helper(*args, **kwds):
        return MockContextManager(func(*args, **kwds))
    return helper


class MockResource(object):
    def __init__(self):
        self.yielded = False
        self.stopped = False


@mock_contextmanager
def mock_contextmanager_generator():
    mock = MockResource()
    try:
        mock.yielded = True
        yield mock
    finally:
        mock.stopped = True


class Nested(object):

    def __init__(self, *managers):
        self.managers = managers
        self.entered = None

    def __enter__(self):
        if self.entered is not None:
            raise RuntimeError("Context is not reentrant")
        self.entered = deque()
        vars = []
        try:
            for mgr in self.managers:
                vars.append(mgr.__enter__())
                self.entered.appendleft(mgr)
        except:
            if not self.__exit__(*sys.exc_info()):
                raise
        return vars

    def __exit__(self, *exc_info):
        # Behave like nested with statements
        # first in, last out
        # New exceptions override old ones
        ex = exc_info
        for mgr in self.entered:
            try:
                if mgr.__exit__(*ex):
                    ex = (None, None, None)
            except:
                ex = sys.exc_info()
        self.entered = None
        if ex is not exc_info:
            raise ex[0], ex[1], ex[2]


class MockNested(Nested):
    def __init__(self, *managers):
        Nested.__init__(self, *managers)
        self.enter_called = False
        self.exit_called = False
        self.exit_args = None

    def __enter__(self):
        self.enter_called = True
        return Nested.__enter__(self)

    def __exit__(self, *exc_info):
        self.exit_called = True
        self.exit_args = exc_info
        return Nested.__exit__(self, *exc_info)


class FailureTestCase(unittest.TestCase):
    def testNameError(self):
        def fooNotDeclared():
            with foo: pass
        self.assertRaises(NameError, fooNotDeclared)

    def testEnterAttributeError(self):
        class LacksEnter(object):
            def __exit__(self, type, value, traceback):
                pass

        def fooLacksEnter():
            foo = LacksEnter()
            with foo: pass
        self.assertRaises(AttributeError, fooLacksEnter)

    def testExitAttributeError(self):
        class LacksExit(object):
            def __enter__(self):
                pass

        def fooLacksExit():
            foo = LacksExit()
            with foo: pass
        self.assertRaises(AttributeError, fooLacksExit)

    def assertRaisesSyntaxError(self, codestr):
        def shouldRaiseSyntaxError(s):
            compile(s, '', 'single')
        self.assertRaises(SyntaxError, shouldRaiseSyntaxError, codestr)

    def testAssignmentToNoneError(self):
        self.assertRaisesSyntaxError('with mock as None:\n  pass')
        self.assertRaisesSyntaxError(
            'with mock as (None):\n'
            '  pass')

    def testAssignmentToEmptyTupleError(self):
        self.assertRaisesSyntaxError(
            'with mock as ():\n'
            '  pass')

    def testAssignmentToTupleOnlyContainingNoneError(self):
        self.assertRaisesSyntaxError('with mock as None,:\n  pass')
        self.assertRaisesSyntaxError(
            'with mock as (None,):\n'
            '  pass')

    def testAssignmentToTupleContainingNoneError(self):
        self.assertRaisesSyntaxError(
            'with mock as (foo, None, bar):\n'
            '  pass')

    def testEnterThrows(self):
        class EnterThrows(object):
            def __enter__(self):
                raise RuntimeError("Enter threw")
            def __exit__(self, *args):
                pass

        def shouldThrow():
            ct = EnterThrows()
            self.foo = None
            with ct as self.foo:
                pass
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertEqual(self.foo, None)

    def testExitThrows(self):
        class ExitThrows(object):
            def __enter__(self):
                return
            def __exit__(self, *args):
                raise RuntimeError(42)
        def shouldThrow():
            with ExitThrows():
                pass
        self.assertRaises(RuntimeError, shouldThrow)

class ContextmanagerAssertionMixin(object):
    TEST_EXCEPTION = RuntimeError("test exception")

    def assertInWithManagerInvariants(self, mock_manager):
        self.assertTrue(mock_manager.enter_called)
        self.assertFalse(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, None)

    def assertAfterWithManagerInvariants(self, mock_manager, exit_args):
        self.assertTrue(mock_manager.enter_called)
        self.assertTrue(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args, exit_args)

    def assertAfterWithManagerInvariantsNoError(self, mock_manager):
        self.assertAfterWithManagerInvariants(mock_manager,
            (None, None, None))

    def assertInWithGeneratorInvariants(self, mock_generator):
        self.assertTrue(mock_generator.yielded)
        self.assertFalse(mock_generator.stopped)

    def assertAfterWithGeneratorInvariantsNoError(self, mock_generator):
        self.assertTrue(mock_generator.yielded)
        self.assertTrue(mock_generator.stopped)

    def raiseTestException(self):
        raise self.TEST_EXCEPTION

    def assertAfterWithManagerInvariantsWithError(self, mock_manager):
        self.assertTrue(mock_manager.enter_called)
        self.assertTrue(mock_manager.exit_called)
        self.assertEqual(mock_manager.exit_args[0], RuntimeError)
        self.assertEqual(mock_manager.exit_args[1], self.TEST_EXCEPTION)

    def assertAfterWithGeneratorInvariantsWithError(self, mock_generator):
        self.assertTrue(mock_generator.yielded)
        self.assertTrue(mock_generator.stopped)


class NonexceptionalTestCase(unittest.TestCase, ContextmanagerAssertionMixin):
    def testInlineGeneratorSyntax(self):
        with mock_contextmanager_generator():
            pass

    def testUnboundGenerator(self):
        mock = mock_contextmanager_generator()
        with mock:
            pass
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testInlineGeneratorBoundSyntax(self):
        with mock_contextmanager_generator() as foo:
            self.assertInWithGeneratorInvariants(foo)
        # FIXME: In the future, we'll try to keep the bound names from leaking
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    def testInlineGeneratorBoundToExistingVariable(self):
        foo = None
        with mock_contextmanager_generator() as foo:
            self.assertInWithGeneratorInvariants(foo)
        self.assertAfterWithGeneratorInvariantsNoError(foo)

    def testInlineGeneratorBoundToDottedVariable(self):
        with mock_contextmanager_generator() as self.foo:
            self.assertInWithGeneratorInvariants(self.foo)
        self.assertAfterWithGeneratorInvariantsNoError(self.foo)

    def testBoundGenerator(self):
        mock = mock_contextmanager_generator()
        with mock as foo:
            self.assertInWithGeneratorInvariants(foo)
            self.assertInWithManagerInvariants(mock)
        self.assertAfterWithGeneratorInvariantsNoError(foo)
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        with mock_a as foo:
            mock_b = mock_contextmanager_generator()
            with mock_b as bar:
                self.assertInWithManagerInvariants(mock_a)
                self.assertInWithManagerInvariants(mock_b)
                self.assertInWithGeneratorInvariants(foo)
                self.assertInWithGeneratorInvariants(bar)
            self.assertAfterWithManagerInvariantsNoError(mock_b)
            self.assertAfterWithGeneratorInvariantsNoError(bar)
            self.assertInWithManagerInvariants(mock_a)
            self.assertInWithGeneratorInvariants(foo)
        self.assertAfterWithManagerInvariantsNoError(mock_a)
        self.assertAfterWithGeneratorInvariantsNoError(foo)


class NestedNonexceptionalTestCase(unittest.TestCase,
    ContextmanagerAssertionMixin):
    def testSingleArgInlineGeneratorSyntax(self):
        with Nested(mock_contextmanager_generator()):
            pass

    def testSingleArgUnbound(self):
        mock_contextmanager = mock_contextmanager_generator()
        mock_nested = MockNested(mock_contextmanager)
        with mock_nested:
            self.assertInWithManagerInvariants(mock_contextmanager)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(mock_contextmanager)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    def testSingleArgBoundToNonTuple(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        with Nested(m) as foo:
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    def testSingleArgBoundToSingleElementParenthesizedList(self):
        m = mock_contextmanager_generator()
        # This will bind all the arguments to nested() into a single list
        # assigned to foo.
        with Nested(m) as (foo):
            self.assertInWithManagerInvariants(m)
        self.assertAfterWithManagerInvariantsNoError(m)

    def testSingleArgBoundToMultipleElementTupleError(self):
        def shouldThrowValueError():
            with Nested(mock_contextmanager_generator()) as (foo, bar):
                pass
        self.assertRaises(ValueError, shouldThrowValueError)

    def testSingleArgUnbound(self):
        mock_contextmanager = mock_contextmanager_generator()
        mock_nested = MockNested(mock_contextmanager)
        with mock_nested:
            self.assertInWithManagerInvariants(mock_contextmanager)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(mock_contextmanager)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    def testMultipleArgUnbound(self):
        m = mock_contextmanager_generator()
        n = mock_contextmanager_generator()
        o = mock_contextmanager_generator()
        mock_nested = MockNested(m, n, o)
        with mock_nested:
            self.assertInWithManagerInvariants(m)
            self.assertInWithManagerInvariants(n)
            self.assertInWithManagerInvariants(o)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithManagerInvariantsNoError(m)
        self.assertAfterWithManagerInvariantsNoError(n)
        self.assertAfterWithManagerInvariantsNoError(o)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)

    def testMultipleArgBound(self):
        mock_nested = MockNested(mock_contextmanager_generator(),
            mock_contextmanager_generator(), mock_contextmanager_generator())
        with mock_nested as (m, n, o):
            self.assertInWithGeneratorInvariants(m)
            self.assertInWithGeneratorInvariants(n)
            self.assertInWithGeneratorInvariants(o)
            self.assertInWithManagerInvariants(mock_nested)
        self.assertAfterWithGeneratorInvariantsNoError(m)
        self.assertAfterWithGeneratorInvariantsNoError(n)
        self.assertAfterWithGeneratorInvariantsNoError(o)
        self.assertAfterWithManagerInvariantsNoError(mock_nested)


class ExceptionalTestCase(unittest.TestCase, ContextmanagerAssertionMixin):
    def testSingleResource(self):
        cm = mock_contextmanager_generator()
        def shouldThrow():
            with cm as self.resource:
                self.assertInWithManagerInvariants(cm)
                self.assertInWithGeneratorInvariants(self.resource)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource)

    def testNestedSingleStatements(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        def shouldThrow():
            with mock_a as self.foo:
                with mock_b as self.bar:
                    self.assertInWithManagerInvariants(mock_a)
                    self.assertInWithManagerInvariants(mock_b)
                    self.assertInWithGeneratorInvariants(self.foo)
                    self.assertInWithGeneratorInvariants(self.bar)
                    self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithManagerInvariantsWithError(mock_b)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)
        self.assertAfterWithGeneratorInvariantsWithError(self.bar)

    def testMultipleResourcesInSingleStatement(self):
        cm_a = mock_contextmanager_generator()
        cm_b = mock_contextmanager_generator()
        mock_nested = MockNested(cm_a, cm_b)
        def shouldThrow():
            with mock_nested as (self.resource_a, self.resource_b):
                self.assertInWithManagerInvariants(cm_a)
                self.assertInWithManagerInvariants(cm_b)
                self.assertInWithManagerInvariants(mock_nested)
                self.assertInWithGeneratorInvariants(self.resource_a)
                self.assertInWithGeneratorInvariants(self.resource_b)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(cm_a)
        self.assertAfterWithManagerInvariantsWithError(cm_b)
        self.assertAfterWithManagerInvariantsWithError(mock_nested)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource_a)
        self.assertAfterWithGeneratorInvariantsWithError(self.resource_b)

    def testNestedExceptionBeforeInnerStatement(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        self.bar = None
        def shouldThrow():
            with mock_a as self.foo:
                self.assertInWithManagerInvariants(mock_a)
                self.assertInWithGeneratorInvariants(self.foo)
                self.raiseTestException()
                with mock_b as self.bar:
                    pass
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)

        # The inner statement stuff should never have been touched
        self.assertEqual(self.bar, None)
        self.assertFalse(mock_b.enter_called)
        self.assertFalse(mock_b.exit_called)
        self.assertEqual(mock_b.exit_args, None)

    def testNestedExceptionAfterInnerStatement(self):
        mock_a = mock_contextmanager_generator()
        mock_b = mock_contextmanager_generator()
        def shouldThrow():
            with mock_a as self.foo:
                with mock_b as self.bar:
                    self.assertInWithManagerInvariants(mock_a)
                    self.assertInWithManagerInvariants(mock_b)
                    self.assertInWithGeneratorInvariants(self.foo)
                    self.assertInWithGeneratorInvariants(self.bar)
                self.raiseTestException()
        self.assertRaises(RuntimeError, shouldThrow)
        self.assertAfterWithManagerInvariantsWithError(mock_a)
        self.assertAfterWithManagerInvariantsNoError(mock_b)
        self.assertAfterWithGeneratorInvariantsWithError(self.foo)
        self.assertAfterWithGeneratorInvariantsNoError(self.bar)

    def testRaisedStopIteration1(self):
        # From bug 1462485
        @contextmanager
        def cm():
            yield

        def shouldThrow():
            with cm():
                raise StopIteration("from with")

        self.assertRaises(StopIteration, shouldThrow)

    def testRaisedStopIteration2(self):
        # From bug 1462485
        class cm(object):
            def __enter__(self):
                pass
            def __exit__(self, type, value, traceback):
                pass

        def shouldThrow():
            with cm():
                raise StopIteration("from with")

        self.assertRaises(StopIteration, shouldThrow)

    def testRaisedStopIteration3(self):
        # Another variant where the exception hasn't been instantiated
        # From bug 1705170
        @contextmanager
        def cm():
            yield

        def shouldThrow():
            with cm():
                raise iter([]).next()

        self.assertRaises(StopIteration, shouldThrow)

    def testRaisedGeneratorExit1(self):
        # From bug 1462485
        @contextmanager
        def cm():
            yield

        def shouldThrow():
            with cm():
                raise GeneratorExit("from with")

        self.assertRaises(GeneratorExit, shouldThrow)

    def testRaisedGeneratorExit2(self):
        # From bug 1462485
        class cm (object):
            def __enter__(self):
                pass
            def __exit__(self, type, value, traceback):
                pass

        def shouldThrow():
            with cm():
                raise GeneratorExit("from with")

        self.assertRaises(GeneratorExit, shouldThrow)

    def testErrorsInBool(self):
        # issue4589: __exit__ return code may raise an exception
        # when looking at its truth value.

        class cm(object):
            def __init__(self, bool_conversion):
                class Bool:
                    def __nonzero__(self):
                        return bool_conversion()
                self.exit_result = Bool()
            def __enter__(self):
                return 3
            def __exit__(self, a, b, c):
                return self.exit_result

        def trueAsBool():
            with cm(lambda: True):
                self.fail("Should NOT see this")
        trueAsBool()

        def falseAsBool():
            with cm(lambda: False):
                self.fail("Should raise")
        self.assertRaises(AssertionError, falseAsBool)

        def failAsBool():
            with cm(lambda: 1//0):
                self.fail("Should NOT see this")
        self.assertRaises(ZeroDivisionError, failAsBool)


class NonLocalFlowControlTestCase(unittest.TestCase,
                                  ContextmanagerAssertionMixin):

    def testWithBreak(self):
        mock = mock_contextmanager_generator()
        counter = 0
        while True:
            counter += 1
            with mock:
                counter += 10
                break
            counter += 100 # Not reached
        self.assertEqual(counter, 11)
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testWithContinue(self):
        mock = mock_contextmanager_generator()
        counter = 0
        while True:
            counter += 1
            if counter > 2:
                break
            with mock:
                counter += 10
                continue
            counter += 100 # Not reached
        self.assertEqual(counter, 12)
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testWithReturn(self):
        mock = mock_contextmanager_generator()
        def foo():
            counter = 0
            while True:
                counter += 1
                with mock:
                    counter += 10
                    return counter
                counter += 100 # Not reached
        self.assertEqual(foo(), 11)
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testWithYield(self):
        mock = mock_contextmanager_generator()
        def gen():
            with mock:
                yield 12
                yield 13
        x = list(gen())
        self.assertEqual(x, [12, 13])
        self.assertAfterWithManagerInvariantsNoError(mock)

    def testWithRaise(self):
        mock = mock_contextmanager_generator()
        counter = 0
        try:
            counter += 1
            with mock:
                counter += 10
                raise RuntimeError
            counter += 100 # Not reached
        except RuntimeError:
            self.assertEqual(counter, 11)
            self.assertAfterWithManagerInvariants(mock, sys.exc_info())
        else:
            self.fail("Didn't raise RuntimeError")


class AssignmentTargetTestCase(unittest.TestCase):

    def testSingleComplexTarget(self):
        targets = {1: [0, 1, 2]}
        with mock_contextmanager_generator() as targets[1][0]:
            self.assertEqual(targets.keys(), [1])
            self.assertEqual(targets[1][0].__class__, MockResource)
        with mock_contextmanager_generator() as targets.values()[0][1]:
            self.assertEqual(targets.keys(), [1])
            self.assertEqual(targets[1][1].__class__, MockResource)
        with mock_contextmanager_generator() as targets[2]:
            keys = targets.keys()
            keys.sort()
            self.assertEqual(keys, [1, 2])
        class C: pass
        blah = C()
        with mock_contextmanager_generator() as blah.foo:
            self.assertEqual(hasattr(blah, "foo"), True)

    def testMultipleComplexTargets(self):
        class C:
            def __enter__(self): return 1, 2, 3
            def __exit__(self, t, v, tb): pass
        targets = {1: [0, 1, 2]}
        with C() as (targets[1][0], targets[1][1], targets[1][2]):
            self.assertEqual(targets, {1: [1, 2, 3]})
        with C() as (targets.values()[0][2], targets.values()[0][1], targets.values()[0][0]):
            self.assertEqual(targets, {1: [3, 2, 1]})
        with C() as (targets[1], targets[2], targets[3]):
            self.assertEqual(targets, {1: 1, 2: 2, 3: 3})
        class B: pass
        blah = B()
        with C() as (blah.one, blah.two, blah.three):
            self.assertEqual(blah.one, 1)
            self.assertEqual(blah.two, 2)
            self.assertEqual(blah.three, 3)


class ExitSwallowsExceptionTestCase(unittest.TestCase):

    def testExitTrueSwallowsException(self):
        class AfricanSwallow:
            def __enter__(self): pass
            def __exit__(self, t, v, tb): return True
        try:
            with AfricanSwallow():
                1/0
        except ZeroDivisionError:
            self.fail("ZeroDivisionError should have been swallowed")

    def testExitFalseDoesntSwallowException(self):
        class EuropeanSwallow:
            def __enter__(self): pass
            def __exit__(self, t, v, tb): return False
        try:
            with EuropeanSwallow():
                1/0
        except ZeroDivisionError:
            pass
        else:
            self.fail("ZeroDivisionError should have been raised")


class NewKeywordsWarningTestCase(unittest.TestCase):

    def check(self, code, word=None):
        save = sys.stderr
        sys.stderr = stream = StringIO.StringIO()
        try:
            compile(code, "<string>", "exec", 0, True)
        finally:
            sys.stderr = save
        if word:
            self.assert_("Warning: %r will become a reserved keyword in Python 2.6" % word
                         in stream.getvalue())
        else:
            self.assertEqual(stream.getvalue(), "")

    def test_basic(self):
        self.check("as = 4", "as")
        self.check("with = 4", "with")
        self.check("class as: pass", "as")
        self.check("class with: pass", "with")
        self.check("obj.as = 4", "as")
        self.check("with.obj = 4", "with")
        self.check("def with(): pass", "with")
        self.check("do(); with = 23", "with")

    def test_after_import(self):
        # issue 3936
        self.check("import sys\nas = 4", "as")
        self.check("import sys\nwith = 4", "with")


def test_main():
    run_unittest(FailureTestCase, NonexceptionalTestCase,
                 NestedNonexceptionalTestCase, ExceptionalTestCase,
                 NonLocalFlowControlTestCase,
                 AssignmentTargetTestCase,
                 ExitSwallowsExceptionTestCase,
                 )
                 #XXX: punting NewKeywordsWarningTestCase at least for the
                 #     short term making "with" and "as" anything but true
                 #     keywords is not easy with the antlr parser though it is
                 #     probably doable.  Just not a high priority compared to
                 #     other problems and in 2.6+ it is a non-problem since
                 #     these become true keywords in CPython.
                 #
                 #NewKeywordsWarningTestCase)


if __name__ == '__main__':
    test_main()
