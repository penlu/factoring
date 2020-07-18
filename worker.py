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

def get_work_source(config):
  source_type = config['work_source'].get('type', 'factordb')
  if source_type == 'factordb':
    return factordb.FactorDB(log, **config['work_source'])
  else:
    log('unrecognized source type: %s' % source_type)

def main():
  # read config file
  with open('config.json', 'r') as config_file:
    config = json.loads(config_file.read())

  work_source = get_work_source(config)

  for id_, n in work_source.get_work():
    log('working on %s' % n)

    log('running ECM')
    result = factoring.ecm(config, n)
    if result:
      log('ECM succeeded: %s | %s' % (n, str(result)))
      work_source.submit(id_, result)
      continue

    log('running GNFS')
    result = factoring.cado(config, n)
    if result:
      log('GNFS succeeded: %s | %s' % (n, str(result)))
      work_source.submit(id_, result)
      continue

if __name__ == '__main__':
  main()
