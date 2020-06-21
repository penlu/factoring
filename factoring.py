import subprocess
from subprocess import Popen, PIPE

ECM='/home/penlu/ecm-7.0.4/ecm'

def ecm_proc(c, b1, b2):
  return Popen([ECM, '-q', '-c', c, b1, b2], stdin=PIPE, stdout=PIPE)

def ecm(n):
  # run 32 parallel ECM
  procs = [ecm_proc('2', '11e3', '1.9e6') for i in range(32)]
  for p in procs:
    p.stdin.write(n + '\n')
    p.stdin.flush()

  # accumulate results
  results = set()
  for i, p in enumerate(procs):
    results = results + set(p.communicate().split())

  # wait for subprocesses
  for p in procs:
    print(p.wait())

  return results - n
