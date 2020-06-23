import factordb
import factoring

import datetime
import json
import time

logfile = open('log.txt', 'a')

def log(s):
  ts = time.time()
  t = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
  print('[' + t + '] ' + s)
  logfile.write('[' + t + '] ' + s + '\n')
  logfile.flush()

def get_work(config):
  min_digits = config.get('min_digits', 79)
  number = config.get('number', 50)
  offset = config.get('offset', 0)
  return factordb.listtype(min_digits=min_digits, number=number, offset=offset)

def main():
  # read config file
  with open('config.json', 'r') as config_file:
    config = json.loads(config_file.read())

  while True:
    log('getting work')
    l = get_work(config)
    for n in l:
      log('working on %s' % n)

      # check whether n has already been factored
      q = factordb.query(n)
      if q['status'] != 'C':
        log('already factored')
        continue

      log('running ECM')
      ecm_result = factoring.ecm(config, n)
      if ecm_result:
        log('ECM succeeded: %s | %s' % (n, str(ecm_result)))
        factordb.submit(q['id'], ecm_result)
        continue

      log('running NFS')
      nfs_result = factoring.nfs(config, n)
      if nfs_result:
        log('NFS succeeded: %s | %s' % (n, str(nfs_result)))
        factordb.submit(q['id'], nfs_result)
        continue

main()
