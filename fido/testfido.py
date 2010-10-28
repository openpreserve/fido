'''
Created on 28 Oct 2010

@author: AFarquha
'''
import unittest
import prepare

class Test(unittest.TestCase):
    def test_convert(self):
        "convertToRegex checking BOF/EOF/VAR with all features"
        tests = [
        (('414141', 'Little', 'Absolute from BOF', '0', ''), r'\AAAA'),
        (('4141*42', 'Little', 'Absolute from BOF', '0', ''), r'\AAA.*B'),
        (('4141[42:43]', 'Little', 'Absolute from BOF', '0', ''), r'\AAA[B-C]'),
        (('4141{0-30}41', 'Little', 'Absolute from BOF', '0', ''), r'\AAA.{0,30}A'),
        (('4142', 'Little', 'Absolute from BOF', '5', ''), r'\A.{5}AB'),
        (('4142', 'Little', 'Absolute from BOF', '5', '20'), r'\A.{5,20}AB'),
        
        (('414141', 'Little', 'Absolute from EOF', '0', ''), r'AAA\Z'),
        (('4141*42', 'Little', 'Absolute from EOF', '0', ''), r'AA.*B\Z'),
        (('4141[42:43]', 'Little', 'Absolute from EOF', '0', ''), r'AA[B-C]\Z'),
        (('4141{0-30}41', 'Little', 'Absolute from EOF', '0', ''), r'AA.{0,30}A\Z'),
        (('4142', 'Little', 'Absolute from EOF', '5', ''), r'AB.{5}\Z'),
        (('4142', 'Little', 'Absolute from EOF', '5', '20'), r'AB.{5,20}\Z'),

        (('414141', 'Little', 'Variable', '0', ''), r'AAA'),
        (('4141*42', 'Little', 'Variable', '0', ''), r'AA.*B'),
        (('4141[42:43]', 'Little', 'Variable', '0', ''), r'AA[B-C]'),
        (('4141{0-30}41', 'Little', 'Variable', '0', ''), r'AA.{0,30}A'),
        (('31[09:0B]36', 'Little', 'Variable', '', ''), '1[\\\t-\\\x0b]6'),
        (('3132(3333|343434)35??36*{250-*}37{10-20}', 'Little', 'Variable', '', ''),
         '12(?:33|444)5.?6.*.{250,}7.{10,20}'),
        (('41??', 'Little', 'Variable', '0', ''), r'A.?'),
        ]
        i = 0
        for (args, expected) in tests: 
            result = prepare.convertToRegex(*args)
            self.assertEqual(result, expected, 'Failed conversion. Item {}: Expected {!r}, got {!r}'.format(i, expected, result))
            i += 1

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
