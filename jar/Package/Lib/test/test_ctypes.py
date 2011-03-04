import unittest

from test.test_support import run_suite
import ctypes.test

def test_main():
    skipped, testcases = ctypes.test.get_tests(ctypes.test, "test_*.py", verbosity=0)
    suites = [unittest.makeSuite(t) for t in testcases]
    run_suite(unittest.TestSuite(suites))

if __name__ == "__main__":
    test_main()
