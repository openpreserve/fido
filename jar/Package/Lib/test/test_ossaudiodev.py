from test import test_support
test_support.requires('audio')

from test.test_support import verbose, findfile, TestFailed, TestSkipped

import errno
import fcntl
import ossaudiodev
import os
import sys
import select
import sunaudio
import time
import audioop

# Arggh, AFMT_S16_NE not defined on all platforms -- seems to be a
# fairly recent addition to OSS.
try:
    from ossaudiodev import AFMT_S16_NE
except ImportError:
    if sys.byteorder == "little":
        AFMT_S16_NE = ossaudiodev.AFMT_S16_LE
    else:
        AFMT_S16_NE = ossaudiodev.AFMT_S16_BE


SND_FORMAT_MULAW_8 = 1

def read_sound_file(path):
    fp = open(path, 'rb')
    size, enc, rate, nchannels, extra = sunaudio.gethdr(fp)
    data = fp.read()
    fp.close()

    if enc != SND_FORMAT_MULAW_8:
        print "Expect .au file with 8-bit mu-law samples"
        return

    # Convert the data to 16-bit signed.
    data = audioop.ulaw2lin(data, 2)
    return (data, rate, 16, nchannels)

# version of assert that still works with -O
def _assert(expr, message=None):
    if not expr:
        raise AssertionError(message or "assertion failed")

def play_sound_file(data, rate, ssize, nchannels):
    try:
        dsp = ossaudiodev.open('w')
    except IOError, msg:
        if msg[0] in (errno.EACCES, errno.ENOENT, errno.ENODEV, errno.EBUSY):
            raise TestSkipped, msg
        raise TestFailed, msg

    # at least check that these methods can be invoked
    dsp.bufsize()
    dsp.obufcount()
    dsp.obuffree()
    dsp.getptr()
    dsp.fileno()

    # Make sure the read-only attributes work.
    _assert(dsp.closed is False, "dsp.closed is not False")
    _assert(dsp.name == "/dev/dsp")
    _assert(dsp.mode == 'w', "bad dsp.mode: %r" % dsp.mode)

    # And make sure they're really read-only.
    for attr in ('closed', 'name', 'mode'):
        try:
            setattr(dsp, attr, 42)
            raise RuntimeError("dsp.%s not read-only" % attr)
        except TypeError:
            pass

    # Compute expected running time of sound sample (in seconds).
    expected_time = float(len(data)) / (ssize/8) / nchannels / rate

    # set parameters based on .au file headers
    dsp.setparameters(AFMT_S16_NE, nchannels, rate)
    print ("playing test sound file (expected running time: %.2f sec)"
           % expected_time)
    t1 = time.time()
    dsp.write(data)
    dsp.close()
    t2 = time.time()
    elapsed_time = t2 - t1

    percent_diff = (abs(elapsed_time - expected_time) / expected_time) * 100
    _assert(percent_diff <= 10.0, \
            ("elapsed time (%.2f sec) > 10%% off of expected time (%.2f sec)"
             % (elapsed_time, expected_time)))

def test_setparameters(dsp):
    # Two configurations for testing:
    #   config1 (8-bit, mono, 8 kHz) should work on even the most
    #      ancient and crufty sound card, but maybe not on special-
    #      purpose high-end hardware
    #   config2 (16-bit, stereo, 44.1kHz) should work on all but the
    #      most ancient and crufty hardware
    config1 = (ossaudiodev.AFMT_U8, 1, 8000)
    config2 = (AFMT_S16_NE, 2, 44100)

    for config in [config1, config2]:
        (fmt, channels, rate) = config
        if (dsp.setfmt(fmt) == fmt and
            dsp.channels(channels) == channels and
            dsp.speed(rate) == rate):
            break
    else:
        raise RuntimeError("unable to set audio sampling parameters: "
                           "you must have really weird audio hardware")

    # setparameters() should be able to set this configuration in
    # either strict or non-strict mode.
    result = dsp.setparameters(fmt, channels, rate, False)
    _assert(result == (fmt, channels, rate),
            "setparameters%r: returned %r" % (config, result))
    result = dsp.setparameters(fmt, channels, rate, True)
    _assert(result == (fmt, channels, rate),
            "setparameters%r: returned %r" % (config, result))

def test_bad_setparameters(dsp):

    # Now try some configurations that are presumably bogus: eg. 300
    # channels currently exceeds even Hollywood's ambitions, and
    # negative sampling rate is utter nonsense.  setparameters() should
    # accept these in non-strict mode, returning something other than
    # was requested, but should barf in strict mode.
    fmt = AFMT_S16_NE
    rate = 44100
    channels = 2
    for config in [(fmt, 300, rate),       # ridiculous nchannels
                   (fmt, -5, rate),        # impossible nchannels
                   (fmt, channels, -50),   # impossible rate
                  ]:
        (fmt, channels, rate) = config
        result = dsp.setparameters(fmt, channels, rate, False)
        _assert(result != config,
                "setparameters: unexpectedly got requested configuration")

        try:
            result = dsp.setparameters(fmt, channels, rate, True)
            raise AssertionError("setparameters: expected OSSAudioError")
        except ossaudiodev.OSSAudioError, err:
            print "setparameters: got OSSAudioError as expected"

def test():
    (data, rate, ssize, nchannels) = read_sound_file(findfile('audiotest.au'))
    play_sound_file(data, rate, ssize, nchannels)

    dsp = ossaudiodev.open("w")
    try:
        test_setparameters(dsp)

        # Disabled because it fails under Linux 2.6 with ALSA's OSS
        # emulation layer.
        #test_bad_setparameters(dsp)
    finally:
        dsp.close()
        _assert(dsp.closed is True, "dsp.closed is not True")

test()
