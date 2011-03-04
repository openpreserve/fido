# Very rudimentary test of threading module

import test.test_support
from test.test_support import verbose, is_jython
import random
import sys
import threading
import thread
import time
import unittest

# A trivial mutable counter.
class Counter(object):
    def __init__(self):
        self.value = 0
    def inc(self):
        self.value += 1
    def dec(self):
        self.value -= 1
    def get(self):
        return self.value

class TestThread(threading.Thread):
    def __init__(self, name, testcase, sema, mutex, nrunning):
        threading.Thread.__init__(self, name=name)
        self.testcase = testcase
        self.sema = sema
        self.mutex = mutex
        self.nrunning = nrunning

    def run(self):
        delay = random.random() * 2
        if verbose:
            print 'task', self.getName(), 'will run for', delay, 'sec'

        self.sema.acquire()

        self.mutex.acquire()
        self.nrunning.inc()
        if verbose:
            print self.nrunning.get(), 'tasks are running'
        self.testcase.assert_(self.nrunning.get() <= 3)
        self.mutex.release()

        time.sleep(delay)
        if verbose:
            print 'task', self.getName(), 'done'

        self.mutex.acquire()
        self.nrunning.dec()
        self.testcase.assert_(self.nrunning.get() >= 0)
        if verbose:
            print self.getName(), 'is finished.', self.nrunning.get(), \
                  'tasks are running'
        self.mutex.release()

        self.sema.release()

class ThreadTests(unittest.TestCase):

    # Create a bunch of threads, let each do some work, wait until all are
    # done.
    def test_various_ops(self):
        # This takes about n/3 seconds to run (about n/3 clumps of tasks,
        # times about 1 second per clump).
        NUMTASKS = 10

        # no more than 3 of the 10 can run at once
        sema = threading.BoundedSemaphore(value=3)
        mutex = threading.RLock()
        numrunning = Counter()

        threads = []

        for i in range(NUMTASKS):
            t = TestThread("<thread %d>"%i, self, sema, mutex, numrunning)
            threads.append(t)
            t.start()

        if verbose:
            print 'waiting for all tasks to complete'
        for t in threads:
            t.join(NUMTASKS)
            self.assert_(not t.isAlive())
        if verbose:
            print 'all tasks done'
        self.assertEqual(numrunning.get(), 0)

    # run with a small(ish) thread stack size (256kB)
    def test_various_ops_small_stack(self):
        if verbose:
            print 'with 256kB thread stack size...'
        try:
            threading.stack_size(262144)
        except thread.error:
            if verbose:
                print 'platform does not support changing thread stack size'
            return
        self.test_various_ops()
        threading.stack_size(0)

    # run with a large thread stack size (1MB)
    def test_various_ops_large_stack(self):
        if verbose:
            print 'with 1MB thread stack size...'
        try:
            threading.stack_size(0x100000)
        except thread.error:
            if verbose:
                print 'platform does not support changing thread stack size'
            return
        self.test_various_ops()
        threading.stack_size(0)

    # this test is not applicable to jython since
    # 1. Lock is equiv to RLock, so this weird sync behavior won't be seen
    # 2. We use a weak hash map to map these threads
    # 3. This behavior doesn't make sense for Jython since any foreign
    #    Java threads can use the same underlying locks, etc

    def test_foreign_thread(self):
        # Check that a "foreign" thread can use the threading module.
        def f(mutex):
            # Acquiring an RLock forces an entry for the foreign
            # thread to get made in the threading._active map.
            r = threading.RLock()
            r.acquire()
            r.release()
            mutex.release()

        mutex = threading.Lock()
        mutex.acquire()
        tid = thread.start_new_thread(f, (mutex,))
        # Wait for the thread to finish.
        mutex.acquire()
        self.assert_(tid in threading._active)
        self.assert_(isinstance(threading._active[tid],
                                threading._DummyThread))
        del threading._active[tid]

    # PyThreadState_SetAsyncExc() is a CPython-only gimmick, not (currently)
    # exposed at the Python level.  This test relies on ctypes to get at it.
    def test_PyThreadState_SetAsyncExc(self):
        try:
            import ctypes
        except ImportError:
            if verbose:
                print "test_PyThreadState_SetAsyncExc can't import ctypes"
            return  # can't do anything

        set_async_exc = ctypes.pythonapi.PyThreadState_SetAsyncExc

        class AsyncExc(Exception):
            pass

        exception = ctypes.py_object(AsyncExc)

        # `worker_started` is set by the thread when it's inside a try/except
        # block waiting to catch the asynchronously set AsyncExc exception.
        # `worker_saw_exception` is set by the thread upon catching that
        # exception.
        worker_started = threading.Event()
        worker_saw_exception = threading.Event()

        class Worker(threading.Thread):
            def run(self):
                self.id = thread.get_ident()
                self.finished = False

                try:
                    while True:
                        worker_started.set()
                        time.sleep(0.1)
                except AsyncExc:
                    self.finished = True
                    worker_saw_exception.set()

        t = Worker()
        t.setDaemon(True) # so if this fails, we don't hang Python at shutdown
        t.start()
        if verbose:
            print "    started worker thread"

        # Try a thread id that doesn't make sense.
        if verbose:
            print "    trying nonsensical thread id"
        result = set_async_exc(ctypes.c_long(-1), exception)
        self.assertEqual(result, 0)  # no thread states modified

        # Now raise an exception in the worker thread.
        if verbose:
            print "    waiting for worker thread to get started"
        worker_started.wait()
        if verbose:
            print "    verifying worker hasn't exited"
        self.assert_(not t.finished)
        if verbose:
            print "    attempting to raise asynch exception in worker"
        result = set_async_exc(ctypes.c_long(t.id), exception)
        self.assertEqual(result, 1) # one thread state modified
        if verbose:
            print "    waiting for worker to say it caught the exception"
        worker_saw_exception.wait(timeout=10)
        self.assert_(t.finished)
        if verbose:
            print "    all OK -- joining worker"
        if t.finished:
            t.join()
        # else the thread is still running, and we have no way to kill it

    def test_enumerate_after_join(self):
        # Try hard to trigger #1703448: a thread is still returned in
        # threading.enumerate() after it has been join()ed.
        enum = threading.enumerate
        old_interval = sys.getcheckinterval()
        sys.setcheckinterval(1)
        try:
            for i in xrange(1, 1000):
                t = threading.Thread(target=lambda: None)
                t.start()
                t.join()
                l = enum()
                self.assertFalse(t in l,
                    "#1703448 triggered after %d trials: %s" % (i, l))
        finally:
            sys.setcheckinterval(old_interval)

if is_jython:
    del ThreadTests.test_enumerate_after_join
    del ThreadTests.test_foreign_thread
    del ThreadTests.test_PyThreadState_SetAsyncExc

def test_main():
    test.test_support.run_unittest(ThreadTests)

if __name__ == "__main__":
    test_main()
