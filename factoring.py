import subprocess
from subprocess import Popen, PIPE

NFS='/home/penlu/cado-nfs-2.3.0/cado-nfs.py'

def ecm_proc(config, c, b1, b2):
  ecm_path = config['ecm_path']
  return Popen([ecm_path, '-q', '-c', c, b1, b2], stdin=PIPE, stdout=PIPE)

# ECM on number n
# at least c curves at given b1 and b2
def do_ecm(config, n, c, b1, b2):
  # run j parallel ECM
  j = config.get('ecm_cores', 1)
  procs = [ecm_proc(config, str((c + j - 1) // j), b1, b2) for i in range(j)]
  for p in procs:
    p.stdin.write(bytes(n + '\n', encoding='utf8'))
    p.stdin.flush()

  # accumulate results
  # TODO asynchronous wait
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
# TODO generalize for n
def ecm(config, n):
  result = do_ecm(config, n, 74, '11e3', '1.9e6')
  if result:
    return result
  result = do_ecm(config, n, 214, '5e4', '1.3e7')
  if result:
    return result
  result = do_ecm(config, n, 430, '25e4', '1.3e8')
  if result:
    return result

def nfs(config, n):
  nfs_path = config['nfs_path']
  p = Popen([nfs_path, n], stdout=PIPE)
  results = set(map(lambda x: x.decode('utf8'), p.communicate()[0].split()))
  return list(results - set([n]))
