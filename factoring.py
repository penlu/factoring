import asyncio
import json
import math
import os
import subprocess
from subprocess import Popen, PIPE
import sys

# ECM on number n: at least c curves at the given b1 and b2
async def do_ecm(config, n, c, b1, b2):
  ecm_path = config['ecm_path']
  j = config.get('ecm_procs', 1)
  curves_per_proc = (c + j - 1) // j

  # start j parallel ECM instances
  procs = [await asyncio.create_subprocess_exec(
    ecm_path, '-q', '-c', str(curves_per_proc), b1, b2,
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE) for i in range(j)]

  # write n to each process
  for p in procs:
    p.stdin.write(bytes(n + '\n', encoding='utf8'))
    p.stdin.close()

  running = [p.stdout.read() for p in procs]
  while running:
    done, running = await asyncio.wait(running,
      return_when=asyncio.FIRST_COMPLETED)

    results = [set(map(lambda x: x.decode('utf8'), task.result().split()))
      for task in done]
    factors = list(set.union(*results) - set([n]))

    if factors:
      break

  for p in procs:
    try:
      p.terminate()
    except ProcessLookupError:
      pass
  await asyncio.wait([p.wait() for p in procs])

  return factors

def ecm(config, n, max_t=None):
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

  if not max_t:
    # standard guidance is to run ECM to around 1/3 the digit count before NFS
    max_t = (len(n) + 14) // 15 * 5

  for t in [20, 25, 30, 35, 40, 45, 50, 55, 60, 65]:
    if t > max_t:
      break

    result = asyncio.run(do_ecm(config, n, *params[t]))
    if result:
      return result

def msieve_relations(n):
  n_bits = 0 if int(n) == 0 else math.log2(int(n))
  fb_sizes = [
    (64, 100), (128, 450), (183, 2000), (200, 3000),
    (212, 5400), (233, 10000), (249, 27000), (266, 50000),
    (283, 55000), (298, 60000), (315, 80000), (332, 100000),
    (348, 140000), (363, 210000), (379, 300000), (395, 400000),
    (415, 500000), (440, 700000), (465, 900000), (490, 1100000),
    (512, 1300000)
  ]
  for i in range(len(fb_sizes) - 1):
    if n_bits < fb_sizes[i + 1][0]:
      # weighted average of bracketing table entries
      low = fb_sizes[i]
      high = fb_sizes[i + 1]
      diff = high[0] - low[0]
      fb_size = low[1] + (n_bits - low[0]) / diff * (high[1] - low[1])
      break
  else:
    # input is unreasonable, so take maximum table entry
    fb_size = 1300000

  return int(fb_size + 0.5) + 96

async def msieve_sieve(config, n):
  # calculate relations needed
  max_relations = msieve_relations(n)

  msieve_path = config['msieve_path']
  j = config.get('msieve_procs', 1)

  # start siever processes
  rels_per_proc = (max_relations + j - 1) // j
  procs = [await asyncio.create_subprocess_exec(
    msieve_path, '-q', '-c', '-r', str(rels_per_proc), n,
    '-s', '/tmp/factoring/msieve_%d.dat' % i,
    '-l', '/tmp/factoring/msieve_%d.log' % i,
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE) for i in range(j)]

  await asyncio.wait([p.wait() for p in procs])

def msieve(config, n):
  msieve_path = config['msieve_path']
  j = config.get('msieve_procs', 1)

  # create directory for msieve data
  if not os.path.exists('/tmp/factoring'):
    os.mkdir('/tmp/factoring')

  # clear directory contents
  for i in range(j):
    f = open('/tmp/factoring/msieve_%d.dat' % i, 'w')
    f.close()

  # do sieving
  asyncio.run(msieve_sieve(config, n))

  # compile relations
  cmd = ['cat'] + ['/tmp/factoring/msieve_%d.dat' % i for i in range(j)]
  subprocess.call(cmd, stdin=PIPE,
    stdout=open('/tmp/factoring/msieve.dat', 'w'))

  # do linear algebra
  p = Popen([msieve_path, '-q', '-t', str(j), n,
    '-s', '/tmp/factoring/msieve.dat',
    '-l', '/tmp/factoring/msieve.log'],
    stdin=PIPE, stdout=PIPE)

  return list(map(lambda x: x.decode('utf8'), p.communicate()[0].split()[2::2]))

def cado(config, n):
  cado_path = config['cado_path']
  p = Popen([cado_path, n], stdin=PIPE, stdout=PIPE)
  results = set(map(lambda x: x.decode('utf8'), p.communicate()[0].split()))
  return list(results - set([n]))

if __name__ == '__main__':
  with open('config.json', 'r') as config_file:
    config = json.loads(config_file.read())

    result = ecm(config, sys.argv[1], max_t=int(sys.argv[2]))

    if result:
      print(result)
