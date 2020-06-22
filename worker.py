import factordb
import factoring
import time
import datetime

logfile = open('log.txt', 'a')

def log(s):
  ts = time.time()
  t = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')
  print('[' + t + '] ' + s)
  logfile.write('[' + t + '] ' + s + '\n')
  logfile.flush()

def main():
  while True:
    log('getting work')
    l = factordb.factordb_list(min_digits=80)
    for n in l:
      log('working on %s' % n)

      q = factordb.factordb_query(n)
      if q['status'] != 'C':
        log('already factored')
        continue

      log('running ECM')
      ecm_result = factoring.ecm(n)
      if ecm_result:
        log('success on %s' % n)
        factordb.factordb_submit(q['id'], ecm_result)
        continue

      #print('running GFS')
      #gfs_result = factoring.gfs(n)
      #if gfs_result:
      #  factordb_submit(q['id'], gfs_result)
      #  continue

    exit(0)

main()
