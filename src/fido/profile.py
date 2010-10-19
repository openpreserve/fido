'''
Created on 18 Oct 2010

@author: Adam Farquhar

Profiling for Fido.
'''
import cProfile, run
r1 = "run.main(['-r', '-z', r'e:/Code/fidotests/corpus/'])"
r2 = "run.main(['-r', r'c:\Documents and Settings\afarquha\My Documents\Proposals'])"


cProfile.run(r1, 'prof.out')
