from test.test_support import TestFailed, TESTFN
import os
import wave

def check(t, msg=None):
    if not t:
        raise TestFailed, msg

nchannels = 2
sampwidth = 2
framerate = 8000
nframes = 100

f = wave.open(TESTFN, 'wb')
f.setnchannels(nchannels)
f.setsampwidth(sampwidth)
f.setframerate(framerate)
f.setnframes(nframes)
output = '\0' * nframes * nchannels * sampwidth
f.writeframes(output)
f.close()

f = wave.open(TESTFN, 'rb')
check(nchannels == f.getnchannels(), "nchannels")
check(sampwidth == f.getsampwidth(), "sampwidth")
check(framerate == f.getframerate(), "framerate")
check(nframes == f.getnframes(), "nframes")
input = f.readframes(nframes)
check(input == output, "data")
f.close()

os.remove(TESTFN)
