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

def ecm(config, n):
  # please don't actually run a t65 with this script
  params = {
    20: (74, '11e3', '1.9e6'),
    25: (214, '5e4', '1.3e7'),
    30: (430, '25e4', '1.3e8'),
    35: (904, '1e6', '1.0e9'),
    40: (2350, '3e6', '5.7e9'),
    45: (4480, '11e6', '3.5e10'),
    50: (7553, '43e6', '2.4e11'),
    55: (17769, '11e7', '7.8e11'),
    60: (42017, '26e7', '3.2e12'),
    65: (69408, '85e7', '1.6e13')
  }

  # standard guidance is to run ECM to around 1/3 the digit count before NFS
  max_t = (len(n) + 14) // 15 * 5
  for t in [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]:
    if t > max_t:
      break

    result = do_ecm(config, n, *params[t])
    if result:
      return result

def nfs(config, n):
  nfs_path = config['nfs_path']
  p = Popen([nfs_path, n], stdout=PIPE)
  results = set(map(lambda x: x.decode('utf8'), p.communicate()[0].split()))
  return list(results - set([n]))
