"Test posix functions"

from test import test_support

try:
    import posix
except ImportError:
    raise test_support.TestSkipped, "posix is not available"

import time
import os
import pwd
import sys
import unittest
import warnings
warnings.filterwarnings('ignore', '.* potential security risk .*',
                        RuntimeWarning)

class PosixTester(unittest.TestCase):

    def setUp(self):
        # create empty file
        fp = open(test_support.TESTFN, 'w+')
        fp.close()

    def tearDown(self):
        os.unlink(test_support.TESTFN)

    def testNoArgFunctions(self):
        # test posix functions which take no arguments and have
        # no side-effects which we need to cleanup (e.g., fork, wait, abort)
        NO_ARG_FUNCTIONS = [ "ctermid", "getcwd", "getcwdu", "uname",
                             "times", "getloadavg", "tmpnam",
                             "getegid", "geteuid", "getgid", "getgroups",
                             "getpid", "getpgrp", "getppid", "getuid",
                           ]

        for name in NO_ARG_FUNCTIONS:
            posix_func = getattr(posix, name, None)
            if posix_func is not None:
                posix_func()
                self.assertRaises(TypeError, posix_func, 1)

    def test_statvfs(self):
        if hasattr(posix, 'statvfs'):
            self.assert_(posix.statvfs(os.curdir))

    def test_fstatvfs(self):
        if hasattr(posix, 'fstatvfs'):
            fp = open(test_support.TESTFN)
            try:
                self.assert_(posix.fstatvfs(fp.fileno()))
            finally:
                fp.close()

    def test_ftruncate(self):
        if hasattr(posix, 'ftruncate'):
            fp = open(test_support.TESTFN, 'w+')
            try:
                # we need to have some data to truncate
                fp.write('test')
                fp.flush()
                posix.ftruncate(fp.fileno(), 0)
            finally:
                fp.close()

    def test_dup(self):
        if hasattr(posix, 'dup'):
            fp = open(test_support.TESTFN)
            try:
                fd = posix.dup(fp.fileno())
                self.assert_(isinstance(fd, int))
                os.close(fd)
            finally:
                fp.close()

    def test_confstr(self):
        if hasattr(posix, 'confstr'):
            self.assertRaises(ValueError, posix.confstr, "CS_garbage")
            self.assertEqual(len(posix.confstr("CS_PATH")) > 0, True)

    def test_dup2(self):
        if hasattr(posix, 'dup2'):
            fp1 = open(test_support.TESTFN)
            fp2 = open(test_support.TESTFN)
            try:
                posix.dup2(fp1.fileno(), fp2.fileno())
            finally:
                fp1.close()
                fp2.close()

    def fdopen_helper(self, *args):
        fd = os.open(test_support.TESTFN, os.O_RDONLY)
        fp2 = posix.fdopen(fd, *args)
        fp2.close()

    def test_fdopen(self):
        if hasattr(posix, 'fdopen'):
            self.fdopen_helper()
            self.fdopen_helper('r')
            self.fdopen_helper('r', 100)

    def test_osexlock(self):
        if hasattr(posix, "O_EXLOCK"):
            fd = os.open(test_support.TESTFN,
                         os.O_WRONLY|os.O_EXLOCK|os.O_CREAT)
            self.assertRaises(OSError, os.open, test_support.TESTFN,
                              os.O_WRONLY|os.O_EXLOCK|os.O_NONBLOCK)
            os.close(fd)

            if hasattr(posix, "O_SHLOCK"):
                fd = os.open(test_support.TESTFN,
                             os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
                self.assertRaises(OSError, os.open, test_support.TESTFN,
                                  os.O_WRONLY|os.O_EXLOCK|os.O_NONBLOCK)
                os.close(fd)

    def test_osshlock(self):
        if hasattr(posix, "O_SHLOCK"):
            fd1 = os.open(test_support.TESTFN,
                         os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
            fd2 = os.open(test_support.TESTFN,
                          os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
            os.close(fd2)
            os.close(fd1)

            if hasattr(posix, "O_EXLOCK"):
                fd = os.open(test_support.TESTFN,
                             os.O_WRONLY|os.O_SHLOCK|os.O_CREAT)
                self.assertRaises(OSError, os.open, test_support.TESTFN,
                                  os.O_RDONLY|os.O_EXLOCK|os.O_NONBLOCK)
                os.close(fd)

    def test_fstat(self):
        if hasattr(posix, 'fstat'):
            fp = open(test_support.TESTFN)
            try:
                self.assert_(posix.fstat(fp.fileno()))
            finally:
                fp.close()

    def test_stat(self):
        if hasattr(posix, 'stat'):
            self.assert_(posix.stat(test_support.TESTFN))

    if hasattr(posix, 'chown'):
        def test_chown(self):
            # raise an OSError if the file does not exist
            os.unlink(test_support.TESTFN)
            self.assertRaises(OSError, posix.chown, test_support.TESTFN, -1, -1)

            # re-create the file
            open(test_support.TESTFN, 'w').close()
            if os.getuid() == 0:
                try:
                    # Many linux distros have a nfsnobody user as MAX_UID-2
                    # that makes a good test case for signedness issues.
                    #   http://bugs.python.org/issue1747858
                    # This part of the test only runs when run as root.
                    # Only scary people run their tests as root.
                    ent = pwd.getpwnam('nfsnobody')
                    posix.chown(test_support.TESTFN, ent.pw_uid, ent.pw_gid)
                except KeyError:
                    pass
            else:
                # non-root cannot chown to root, raises OSError
                self.assertRaises(OSError, posix.chown,
                                  test_support.TESTFN, 0, 0)

            # test a successful chown call
            posix.chown(test_support.TESTFN, os.getuid(), os.getgid())

    def test_chdir(self):
        if hasattr(posix, 'chdir'):
            posix.chdir(os.curdir)
            self.assertRaises(OSError, posix.chdir, test_support.TESTFN)

    def test_lsdir(self):
        if hasattr(posix, 'lsdir'):
            self.assert_(test_support.TESTFN in posix.lsdir(os.curdir))

    def test_access(self):
        if hasattr(posix, 'access'):
            self.assert_(posix.access(test_support.TESTFN, os.R_OK))

    def test_umask(self):
        if hasattr(posix, 'umask'):
            old_mask = posix.umask(0)
            self.assert_(isinstance(old_mask, int))
            posix.umask(old_mask)

    def test_strerror(self):
        if hasattr(posix, 'strerror'):
            self.assert_(posix.strerror(0))

    def test_pipe(self):
        if hasattr(posix, 'pipe'):
            reader, writer = posix.pipe()
            os.close(reader)
            os.close(writer)

    def test_tempnam(self):
        if hasattr(posix, 'tempnam'):
            self.assert_(posix.tempnam())
            self.assert_(posix.tempnam(os.curdir))
            self.assert_(posix.tempnam(os.curdir, 'blah'))

    def test_tmpfile(self):
        if hasattr(posix, 'tmpfile'):
            fp = posix.tmpfile()
            fp.close()

    def test_utime(self):
        if hasattr(posix, 'utime'):
            now = time.time()
            posix.utime(test_support.TESTFN, None)
            self.assertRaises(TypeError, posix.utime, test_support.TESTFN, (None, None))
            self.assertRaises(TypeError, posix.utime, test_support.TESTFN, (now, None))
            self.assertRaises(TypeError, posix.utime, test_support.TESTFN, (None, now))
            posix.utime(test_support.TESTFN, (int(now), int(now)))
            posix.utime(test_support.TESTFN, (now, now))

def test_main():
    test_support.run_unittest(PosixTester)

if __name__ == '__main__':
    test_main()
