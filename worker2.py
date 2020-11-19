import factordb
import factoring

import aiohttp
from aiohttp import ClientError
import asyncio
from asyncio.exceptions import TimeoutError
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

  async def do_one(n):
    while True:
      try:
        q = await work_source.query(n)
        if q['status'] != 'C':
          return n, None
        id_, n, result = await factoring.single(config, log, q['id'], n)
        await work_source.put_work(id_, result)
        return n, result
      except (ClientError, TimeoutError) as e:
        log('factordb: query failed; retrying in 5 seconds')
        time.sleep(5)

  tasks = set([])
  while True:
    if len(tasks) < config['ecm_procs']:
      n = await work_gen.__anext__()
      tasks.add(asyncio.create_task(do_one(n)))
      continue

    done, tasks = await asyncio.wait(tasks,
      return_when=asyncio.FIRST_COMPLETED)

    for task in done:
      n, result = task.result()
      if result:
        log('succeeded: %s | %s' % (n, str(result)))
      else:
        log('%s already factored' % n)

asyncio.run(main())
