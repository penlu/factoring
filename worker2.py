import factordb
import factoring

import asyncio
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

async def main():
  # read config file
  with open('config.json', 'r') as config_file:
    config = json.loads(config_file.read())

  work_source = get_work_source(config)
  work_gen = work_source.get_work()

  tasks = set([])
  while True:
    if len(tasks) < config['ecm_procs']:
      id_, n = next(work_gen)
      tasks.add(asyncio.create_task(
        factoring.single(config, log, id_, n)))
      continue

    done, tasks = await asyncio.wait(tasks,
      return_when=asyncio.FIRST_COMPLETED)

    for task in done:
      id_, n, result = task.result()
      log('succeeded: %s | %s' % (n, str(result)))
      work_source.submit(id_, result)

asyncio.run(main())
