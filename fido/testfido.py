'''
Created on 28 Oct 2010

@author: AFarquha
'''
import unittest
import cStringIO

 
class Test(unittest.TestCase):
    def stash_ids(self, fido):
        self.results = []
        def stash(name, matches, delta_t):
            self.results.append((name, [x[0].find('puid').text for x in matches]))
        fido.handle_matches = stash
        
    def test_convert(self):
        import prepare
        "convertToRegex checking BOF/EOF/VAR with all features"
        tests = [
        (('414141', 'Little', 'Absolute from BOF', '0', ''), r'(?s)\AAAA'),
        (('4141*42', 'Little', 'Absolute from BOF', '0', ''), r'(?s)\AAA.*B'),
        (('4141[42:43]', 'Little', 'Absolute from BOF', '0', ''), r'(?s)\AAA[B-C]'),
        (('4141{0-30}41', 'Little', 'Absolute from BOF', '0', ''), r'(?s)\AAA.{0,30}A'),
        (('4142', 'Little', 'Absolute from BOF', '5', ''), r'(?s)\A.{5}AB'),
        (('4142', 'Little', 'Absolute from BOF', '5', '20'), r'(?s)\A.{5,20}AB'),
        
        (('414141', 'Little', 'Absolute from EOF', '0', ''), r'(?s)AAA\Z'),
        (('4141*42', 'Little', 'Absolute from EOF', '0', ''), r'(?s)AA.*B\Z'),
        (('4141[42:43]', 'Little', 'Absolute from EOF', '0', ''), r'(?s)AA[B-C]\Z'),
        (('4141{0-30}41', 'Little', 'Absolute from EOF', '0', ''), r'(?s)AA.{0,30}A\Z'),
        (('4142', 'Little', 'Absolute from EOF', '5', ''), r'(?s)AB.{5}\Z'),
        (('4142', 'Little', 'Absolute from EOF', '5', '20'), r'(?s)AB.{5,20}\Z'),

        (('414141', 'Little', 'Variable', '0', ''), r'(?s)AAA'),
        (('4141*42', 'Little', 'Variable', '0', ''), r'(?s)AA.*B'),
        (('4141[42:43]', 'Little', 'Variable', '0', ''), r'(?s)AA[B-C]'),
        (('4141{0-30}41', 'Little', 'Variable', '0', ''), r'(?s)AA.{0,30}A'),
        (('31[09:0B]36', 'Little', 'Variable', '', ''), '(?s)1[\\x09-\\x0b]6'),
        (('3132(3333|343434)35??36*{250-*}37{10-20}', 'Little', 'Variable', '', ''),
         '(?s)12(?:33|444)5.?6.*.{250,}7.{10,20}'),
        (('41??', 'Little', 'Variable', '0', ''), r'(?s)A.?'),
        ]
        i = 0
        for (args, expected) in tests: 
            result = prepare.convert_to_regex(*args)
            self.assertEqual(result, expected, 'Failed conversion. Item {0}: Expected {1!r}, got {2!r}'.format(i, expected, result))
            i += 1

    def test_identify_stream(self):
        import fido
        fido = fido.Fido()
        self.stash_ids(fido)
        tests = [("%PDF-1.0\n\n some stuff %%EOF\n", 14, ["fmt/14"]),
                 ("%PDF-1.0\n\n some stuff %%EOF\n", 10, ["fmt/14"]),
                 ("%PDF-1.0\n\n some stuff %%EOF\n", 25, ["fmt/14"]),
                 ("%PDF-1.0\n\n some stuff %%EOF\n", 100, ["fmt/14"]),
                 ]
        for (string, bufsize, expected) in tests:
            stream = cStringIO.StringIO(string)
            self.results = []
            fido.bufsize = bufsize
            fido.identify_stream(stream)
            self.assertEqual(len(self.results), 1)
            self.assertTrue(set(self.results[0][1]) == set(expected))
        
    def test_identify_stream_with_header(self):
        import fido
        fido = fido.Fido()
        self.stash_ids(fido)
        self.results = []
        fido.bufsize = 25
        tests = [("%PDF-1.0\n\n some stuff %%EOF\n", ["fmt/14"]),
                 ("%PDF-1.0\n\n" + "some stuff" * 10 + "%%EOF\n", ["fmt/14"]),
                 ("%PDF-1.0\n\n " + "some stuff" * 15 + " %%EOF\n", ["fmt/14"]),
                 ("%PDF-1.0\n\n " + "some stuff" * 20 + " %%EOF\n", ["fmt/14"]),
                 ]
        buf = cStringIO.StringIO()
        for (string, expected) in tests:
            buf.write("header1:value1\n")
            buf.write("header2:value2\n")
            buf.write("Content-length:" + str(len(string)))
            buf.write("\n\n")
            buf.write(string)
        buf.seek(0)   
        fido.identify_multi_object_stream(buf)
        self.assertEqual(len(self.results), len(tests))
        for ((unused_name, ids), (unused_string, expected)) in zip(self.results, tests):
            self.assertTrue(set(ids) == set(expected))
 
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
