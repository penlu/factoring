import subprocess
from subprocess import Popen, PIPE

ECM='/home/penlu/ecm-7.0.4/ecm'

def ecm_proc(c, b1, b2):
  return Popen([ECM, '-q', '-c', c, b1, b2], stdin=PIPE, stdout=PIPE)

def do_ecm(n, c, b1, b2):
  # run 32 parallel ECM
  procs = [ecm_proc(str((c + 31) // 32), b1, b2) for i in range(32)]
  for p in procs:
    p.stdin.write(bytes(n + '\n', encoding='utf8'))
    p.stdin.flush()

  # accumulate results
  results = set()
  for i, p in enumerate(procs):
    results = results | set(map(lambda x: x.decode('utf8'), p.communicate()[0].split()))

  # wait for subprocesses
  for p in procs:
    p.wait()

  return list(results - set([n]))

#       digits D  optimal B1   default B2           expected curves
#                                                       N(B1,B2,D)
#                                              -power 1         default poly
#          20       11e3         1.9e6             74               74 [x^1]
#          25        5e4         1.3e7            221              214 [x^2]
#          30       25e4         1.3e8            453              430 [D(3)]
#          35        1e6         1.0e9            984              904 [D(6)]
#          40        3e6         5.7e9           2541             2350 [D(6)]
#          45       11e6        3.5e10           4949             4480 [D(12)]
#          50       43e6        2.4e11           8266             7553 [D(12)]
#          55       11e7        7.8e11          20158            17769 [D(30)]
#          60       26e7        3.2e12          47173            42017 [D(30)]
#          65       85e7        1.6e13          77666            69408 [D(30)]
def ecm(n):
  result = do_ecm(n, 74, '11e3', '1.9e6')
  if result:
    return result
  result = do_ecm(n, 214, '5e4', '1.3e7')
  if result:
    return result
  result = do_ecm(n, 430, '25e4', '1.3e8')
  if result:
    return result
