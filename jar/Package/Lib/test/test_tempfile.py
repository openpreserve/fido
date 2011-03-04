# From Python 2.5.1
# tempfile.py unit tests.
from __future__ import with_statement
import tempfile
import os
import sys
import re
import errno
import warnings

import unittest
from test import test_support

warnings.filterwarnings("ignore",
                        category=RuntimeWarning,
                        message="mktemp", module=__name__)

if hasattr(os, 'stat'):
    import stat
    has_stat = 1
else:
    has_stat = 0

has_textmode = (tempfile._text_openflags != tempfile._bin_openflags)
has_spawnl = hasattr(os, 'spawnl')

# TEST_FILES may need to be tweaked for systems depending on the maximum
# number of files that can be opened at one time (see ulimit -n)
if sys.platform == 'mac':
    TEST_FILES = 32
elif sys.platform in ('openbsd3', 'openbsd4'):
    TEST_FILES = 48
else:
    TEST_FILES = 100

# This is organized as one test for each chunk of code in tempfile.py,
# in order of their appearance in the file.  Testing which requires
# threads is not done here.

# Common functionality.
class TC(unittest.TestCase):

    str_check = re.compile(r"[a-zA-Z0-9_-]{6}$")

    def failOnException(self, what, ei=None):
        if ei is None:
            ei = sys.exc_info()
        self.fail("%s raised %s: %s" % (what, ei[0], ei[1]))

    def nameCheck(self, name, dir, pre, suf):
        (ndir, nbase) = os.path.split(name)
        npre  = nbase[:len(pre)]
        nsuf  = nbase[len(nbase)-len(suf):]

        # check for equality of the absolute paths!
        self.assertEqual(os.path.abspath(ndir), os.path.abspath(dir),
                         "file '%s' not in directory '%s'" % (name, dir))
        self.assertEqual(npre, pre,
                         "file '%s' does not begin with '%s'" % (nbase, pre))
        self.assertEqual(nsuf, suf,
                         "file '%s' does not end with '%s'" % (nbase, suf))

        nbase = nbase[len(pre):len(nbase)-len(suf)]
        self.assert_(self.str_check.match(nbase),
                     "random string '%s' does not match /^[a-zA-Z0-9_-]{6}$/"
                     % nbase)

test_classes = []

class test_exports(TC):
    def test_exports(self):
        # There are no surprising symbols in the tempfile module
        dict = tempfile.__dict__

        expected = {
            "NamedTemporaryFile" : 1,
            "TemporaryFile" : 1,
            "mkstemp" : 1,
            "mkdtemp" : 1,
            "mktemp" : 1,
            "TMP_MAX" : 1,
            "gettempprefix" : 1,
            "gettempdir" : 1,
            "tempdir" : 1,
            "template" : 1
        }

        unexp = []
        for key in dict:
            if key[0] != '_' and key not in expected:
                unexp.append(key)
        self.failUnless(len(unexp) == 0,
                        "unexpected keys: %s" % unexp)

test_classes.append(test_exports)


class test__RandomNameSequence(TC):
    """Test the internal iterator object _RandomNameSequence."""

    def setUp(self):
        self.r = tempfile._RandomNameSequence()

    def test_get_six_char_str(self):
        # _RandomNameSequence returns a six-character string
        s = self.r.next()
        self.nameCheck(s, '', '', '')

    def test_many(self):
        # _RandomNameSequence returns no duplicate strings (stochastic)

        dict = {}
        r = self.r
        for i in xrange(TEST_FILES):
            s = r.next()
            self.nameCheck(s, '', '', '')
            self.failIf(s in dict)
            dict[s] = 1

    def test_supports_iter(self):
        # _RandomNameSequence supports the iterator protocol

        i = 0
        r = self.r
        try:
            for s in r:
                i += 1
                if i == 20:
                    break
        except:
            failOnException("iteration")

test_classes.append(test__RandomNameSequence)


class test__candidate_tempdir_list(TC):
    """Test the internal function _candidate_tempdir_list."""

    def test_nonempty_list(self):
        # _candidate_tempdir_list returns a nonempty list of strings

        cand = tempfile._candidate_tempdir_list()

        self.failIf(len(cand) == 0)
        for c in cand:
            self.assert_(isinstance(c, basestring),
                         "%s is not a string" % c)

    def test_wanted_dirs(self):
        # _candidate_tempdir_list contains the expected directories

        # Make sure the interesting environment variables are all set.
        added = []
        try:
            for envname in 'TMPDIR', 'TEMP', 'TMP':
                dirname = os.getenv(envname)
                if not dirname:
                    os.environ[envname] = os.path.abspath(envname)
                    added.append(envname)

            cand = tempfile._candidate_tempdir_list()

            for envname in 'TMPDIR', 'TEMP', 'TMP':
                dirname = os.getenv(envname)
                if not dirname: raise ValueError
                self.assert_(dirname in cand)

            try:
                dirname = os.getcwd()
            except (AttributeError, os.error):
                dirname = os.curdir

            self.assert_(dirname in cand)

            # Not practical to try to verify the presence of OS-specific
            # paths in this list.
        finally:
            for p in added:
                del os.environ[p]

test_classes.append(test__candidate_tempdir_list)


# We test _get_default_tempdir by testing gettempdir.


class test__get_candidate_names(TC):
    """Test the internal function _get_candidate_names."""

    def test_retval(self):
        # _get_candidate_names returns a _RandomNameSequence object
        obj = tempfile._get_candidate_names()
        self.assert_(isinstance(obj, tempfile._RandomNameSequence))

    def test_same_thing(self):
        # _get_candidate_names always returns the same object
        a = tempfile._get_candidate_names()
        b = tempfile._get_candidate_names()

        self.assert_(a is b)

test_classes.append(test__get_candidate_names)


class test__mkstemp_inner(TC):
    """Test the internal function _mkstemp_inner."""

    class mkstemped:
        _bflags = tempfile._bin_openflags
        _tflags = tempfile._text_openflags

        def __init__(self, dir, pre, suf, bin):
            if bin: flags = self._bflags
            else:   flags = self._tflags

            # XXX: CPython assigns _close/_unlink as class vars but this
            # would rebind Jython's close/unlink (to be classmethods)
            # because they're not built-in functions (unfortunately
            # built-in functions act differently when binding:
            # http://mail.python.org/pipermail/python-dev/2003-April/034749.html)
            self._close = os.close
            self._unlink = os.unlink
            (self.fd, self.name) = tempfile._mkstemp_inner(dir, pre, suf, flags)

        def write(self, str):
            os.write(self.fd, str)
            # XXX: self.test_choose_directory expects the file to have been deleted
            # (via __del__) by the time it's called, which is CPython specific
            # garbage collection behavior. We need to delete it now in Jython
            self._close(self.fd)
            self._unlink(self.name)

        def __del__(self):
            self._close(self.fd)
            if os.path.exists(self.name):
                self._unlink(self.name)

    def do_create(self, dir=None, pre="", suf="", bin=1):
        if dir is None:
            dir = tempfile.gettempdir()
        try:
            file = self.mkstemped(dir, pre, suf, bin)
        except:
            self.failOnException("_mkstemp_inner")

        self.nameCheck(file.name, dir, pre, suf)
        return file

    def test_basic(self):
        # _mkstemp_inner can create files
        self.do_create().write("blat")
        self.do_create(pre="a").write("blat")
        self.do_create(suf="b").write("blat")
        self.do_create(pre="a", suf="b").write("blat")
        self.do_create(pre="aa", suf=".txt").write("blat")

    def test_basic_many(self):
        # _mkstemp_inner can create many files (stochastic)
        extant = range(TEST_FILES)
        for i in extant:
            extant[i] = self.do_create(pre="aa")
        # XXX: Ensure mkstemped files are deleted (can't rely on Java's
        # GC)
        for i in extant:
            i.__del__()

    def test_choose_directory(self):
        # _mkstemp_inner can create files in a user-selected directory
        dir = tempfile.mkdtemp()
        try:
            self.do_create(dir=dir).write("blat")
        finally:
            os.rmdir(dir)

    # XXX: Jython can't set the write mode yet
    def _test_file_mode(self):
        # _mkstemp_inner creates files with the proper mode
        if not has_stat:
            return            # ugh, can't use TestSkipped.

        file = self.do_create()
        mode = stat.S_IMODE(os.stat(file.name).st_mode)
        expected = 0600
        if sys.platform in ('win32', 'os2emx', 'mac'):
            # There's no distinction among 'user', 'group' and 'world';
            # replicate the 'user' bits.
            user = expected >> 6
            expected = user * (1 + 8 + 64)
        self.assertEqual(mode, expected)

    def test_noinherit(self):
        # _mkstemp_inner file handles are not inherited by child processes
        if not has_spawnl:
            return            # ugh, can't use TestSkipped.

        if test_support.verbose:
            v="v"
        else:
            v="q"

        file = self.do_create()
        fd = "%d" % file.fd

        try:
            me = __file__
        except NameError:
            me = sys.argv[0]

        # We have to exec something, so that FD_CLOEXEC will take
        # effect.  The core of this test is therefore in
        # tf_inherit_check.py, which see.
        tester = os.path.join(os.path.dirname(os.path.abspath(me)),
                              "tf_inherit_check.py")

        # On Windows a spawn* /path/ with embedded spaces shouldn't be quoted,
        # but an arg with embedded spaces should be decorated with double
        # quotes on each end
        if sys.platform in ('win32',):
            decorated = '"%s"' % sys.executable
            tester = '"%s"' % tester
        else:
            decorated = sys.executable

        retval = os.spawnl(os.P_WAIT, sys.executable, decorated, tester, v, fd)
        self.failIf(retval < 0,
                    "child process caught fatal signal %d" % -retval)
        self.failIf(retval > 0, "child process reports failure %d"%retval)

    def test_textmode(self):
        # _mkstemp_inner can create files in text mode
        if not has_textmode:
            return            # ugh, can't use TestSkipped.

        self.do_create(bin=0).write("blat\n")
        # XXX should test that the file really is a text file

test_classes.append(test__mkstemp_inner)


class test_gettempprefix(TC):
    """Test gettempprefix()."""

    def test_sane_template(self):
        # gettempprefix returns a nonempty prefix string
        p = tempfile.gettempprefix()

        self.assert_(isinstance(p, basestring))
        self.assert_(len(p) > 0)

    def test_usable_template(self):
        # gettempprefix returns a usable prefix string

        # Create a temp directory, avoiding use of the prefix.
        # Then attempt to create a file whose name is
        # prefix + 'xxxxxx.xxx' in that directory.
        p = tempfile.gettempprefix() + "xxxxxx.xxx"
        d = tempfile.mkdtemp(prefix="")
        try:
            p = os.path.join(d, p)
            try:
                fd = os.open(p, os.O_RDWR | os.O_CREAT)
            except:
                self.failOnException("os.open")
            os.close(fd)
            os.unlink(p)
        finally:
            os.rmdir(d)

test_classes.append(test_gettempprefix)


class test_gettempdir(TC):
    """Test gettempdir()."""

    def test_directory_exists(self):
        # gettempdir returns a directory which exists

        dir = tempfile.gettempdir()
        self.assert_(os.path.isabs(dir) or dir == os.curdir,
                     "%s is not an absolute path" % dir)
        self.assert_(os.path.isdir(dir),
                     "%s is not a directory" % dir)

    def test_directory_writable(self):
        # gettempdir returns a directory writable by the user

        # sneaky: just instantiate a NamedTemporaryFile, which
        # defaults to writing into the directory returned by
        # gettempdir.
        try:
            file = tempfile.NamedTemporaryFile()
            file.write("blat")
            file.close()
        except:
            self.failOnException("create file in %s" % tempfile.gettempdir())

    def test_same_thing(self):
        # gettempdir always returns the same object
        a = tempfile.gettempdir()
        b = tempfile.gettempdir()

        self.assert_(a is b)

test_classes.append(test_gettempdir)


class test_mkstemp(TC):
    """Test mkstemp()."""

    def do_create(self, dir=None, pre="", suf=""):
        if dir is None:
            dir = tempfile.gettempdir()
        try:
            (fd, name) = tempfile.mkstemp(dir=dir, prefix=pre, suffix=suf)
            (ndir, nbase) = os.path.split(name)
            adir = os.path.abspath(dir)
            self.assertEqual(adir, ndir,
                "Directory '%s' incorrectly returned as '%s'" % (adir, ndir))
        except:
            self.failOnException("mkstemp")

        try:
            self.nameCheck(name, dir, pre, suf)
        finally:
            os.close(fd)
            os.unlink(name)

    def test_basic(self):
        # mkstemp can create files
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")
        self.do_create(dir=".")

    def test_choose_directory(self):
        # mkstemp can create directories in a user-selected directory
        dir = tempfile.mkdtemp()
        try:
            self.do_create(dir=dir)
        finally:
            os.rmdir(dir)

test_classes.append(test_mkstemp)


class test_mkdtemp(TC):
    """Test mkdtemp()."""

    def do_create(self, dir=None, pre="", suf=""):
        if dir is None:
            dir = tempfile.gettempdir()
        try:
            name = tempfile.mkdtemp(dir=dir, prefix=pre, suffix=suf)
        except:
            self.failOnException("mkdtemp")

        try:
            self.nameCheck(name, dir, pre, suf)
            return name
        except:
            os.rmdir(name)
            raise

    def test_basic(self):
        # mkdtemp can create directories
        os.rmdir(self.do_create())
        os.rmdir(self.do_create(pre="a"))
        os.rmdir(self.do_create(suf="b"))
        os.rmdir(self.do_create(pre="a", suf="b"))
        os.rmdir(self.do_create(pre="aa", suf=".txt"))

    def test_basic_many(self):
        # mkdtemp can create many directories (stochastic)
        extant = range(TEST_FILES)
        try:
            for i in extant:
                extant[i] = self.do_create(pre="aa")
        finally:
            for i in extant:
                if(isinstance(i, basestring)):
                    os.rmdir(i)

    def test_choose_directory(self):
        # mkdtemp can create directories in a user-selected directory
        dir = tempfile.mkdtemp()
        try:
            os.rmdir(self.do_create(dir=dir))
        finally:
            os.rmdir(dir)

    def test_mode(self):
        # mkdtemp creates directories with the proper mode
        if not has_stat:
            return            # ugh, can't use TestSkipped.
        if os.name == 'java':
            # Java doesn't support stating files for permissions
            return

        dir = self.do_create()
        try:
            mode = stat.S_IMODE(os.stat(dir).st_mode)
            mode &= 0777 # Mask off sticky bits inherited from /tmp
            expected = 0700
            if sys.platform in ('win32', 'os2emx', 'mac'):
                # There's no distinction among 'user', 'group' and 'world';
                # replicate the 'user' bits.
                user = expected >> 6
                expected = user * (1 + 8 + 64)
            self.assertEqual(mode, expected)
        finally:
            os.rmdir(dir)

test_classes.append(test_mkdtemp)


class test_mktemp(TC):
    """Test mktemp()."""

    # For safety, all use of mktemp must occur in a private directory.
    # We must also suppress the RuntimeWarning it generates.
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.dir:
            os.rmdir(self.dir)
            self.dir = None

    class mktemped:
        _bflags = tempfile._bin_openflags

        def __init__(self, dir, pre, suf):
            # XXX: Assign _unlink here, instead of as a class var. See
            # mkstemped.__init__ for an explanation
            self._unlink = os.unlink

            self.name = tempfile.mktemp(dir=dir, prefix=pre, suffix=suf)
            # Create the file.  This will raise an exception if it's
            # mysteriously appeared in the meanwhile.
            os.close(os.open(self.name, self._bflags, 0600))
            # XXX: test_mktemp.tearDown expects the file to have been deleted
            # (via __del__) by the time it's called, which is CPython specific
            # garbage collection behavior. We need to delete it now in Jython
            self._unlink(self.name)

        #def __del__(self):
        #    self._unlink(self.name)

    def do_create(self, pre="", suf=""):
        try:
            file = self.mktemped(self.dir, pre, suf)
        except:
            self.failOnException("mktemp")

        self.nameCheck(file.name, self.dir, pre, suf)
        return file

    def test_basic(self):
        # mktemp can choose usable file names
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")

    def test_many(self):
        # mktemp can choose many usable file names (stochastic)
        extant = range(TEST_FILES)
        for i in extant:
            extant[i] = self.do_create(pre="aa")

##     def test_warning(self):
##         # mktemp issues a warning when used
##         warnings.filterwarnings("error",
##                                 category=RuntimeWarning,
##                                 message="mktemp")
##         self.assertRaises(RuntimeWarning,
##                           tempfile.mktemp, dir=self.dir)

test_classes.append(test_mktemp)


# We test _TemporaryFileWrapper by testing NamedTemporaryFile.


class test_NamedTemporaryFile(TC):
    """Test NamedTemporaryFile()."""

    def do_create(self, dir=None, pre="", suf=""):
        if dir is None:
            dir = tempfile.gettempdir()
        try:
            file = tempfile.NamedTemporaryFile(dir=dir, prefix=pre, suffix=suf)
        except:
            self.failOnException("NamedTemporaryFile")

        self.nameCheck(file.name, dir, pre, suf)
        return file


    def test_basic(self):
        # NamedTemporaryFile can create files
        self.do_create()
        self.do_create(pre="a")
        self.do_create(suf="b")
        self.do_create(pre="a", suf="b")
        self.do_create(pre="aa", suf=".txt")

    def test_creates_named(self):
        # NamedTemporaryFile creates files with names
        f = tempfile.NamedTemporaryFile()
        self.failUnless(os.path.exists(f.name),
                        "NamedTemporaryFile %s does not exist" % f.name)

    def test_del_on_close(self):
        # A NamedTemporaryFile is deleted when closed
        dir = tempfile.mkdtemp()
        try:
            f = tempfile.NamedTemporaryFile(dir=dir)
            f.write('blat')
            f.close()
            self.failIf(os.path.exists(f.name),
                        "NamedTemporaryFile %s exists after close" % f.name)
        finally:
            os.rmdir(dir)

    def test_multiple_close(self):
        # A NamedTemporaryFile can be closed many times without error
        f = tempfile.NamedTemporaryFile()
        f.write('abc\n')
        f.close()
        try:
            f.close()
            f.close()
        except:
            self.failOnException("close")

    def test_context_manager(self):
        # A NamedTemporaryFile can be used as a context manager
        with tempfile.NamedTemporaryFile() as f:
            self.failUnless(os.path.exists(f.name))
        self.failIf(os.path.exists(f.name))
        def use_closed():
            with f:
                pass
        self.failUnlessRaises(ValueError, use_closed)

    # How to test the mode and bufsize parameters?

test_classes.append(test_NamedTemporaryFile)


class test_TemporaryFile(TC):
    """Test TemporaryFile()."""

    def test_basic(self):
        # TemporaryFile can create files
        # No point in testing the name params - the file has no name.
        try:
            tempfile.TemporaryFile()
        except:
            self.failOnException("TemporaryFile")

    def test_has_no_name(self):
        # TemporaryFile creates files with no names (on this system)
        dir = tempfile.mkdtemp()
        f = tempfile.TemporaryFile(dir=dir)
        f.write('blat')

        # Sneaky: because this file has no name, it should not prevent
        # us from removing the directory it was created in.
        try:
            os.rmdir(dir)
        except:
            ei = sys.exc_info()
            # cleanup
            f.close()
            os.rmdir(dir)
            self.failOnException("rmdir", ei)

    def test_multiple_close(self):
        # A TemporaryFile can be closed many times without error
        f = tempfile.TemporaryFile()
        f.write('abc\n')
        f.close()
        try:
            f.close()
            f.close()
        except:
            self.failOnException("close")

    # How to test the mode and bufsize parameters?


if tempfile.NamedTemporaryFile is not tempfile.TemporaryFile:
    test_classes.append(test_TemporaryFile)

def test_main():
    test_support.run_unittest(*test_classes)

if __name__ == "__main__":
    test_main()
    # XXX: Nudge Java's GC in an attempt to trigger any temp file's
    # __del__ (cause them to be deleted) that hasn't been called
    from java.lang import System
    System.gc()
