import factordb
import factoring

def main():
  while True:
    print('getting work')
    l = factordb_list(min_digits=80)
    for n in l:
      print('working on %s' % n)

      q = factordb_query(n)
      if q['status'] != 'C':
        print('already factored')
        continue

      print('running ECM')
      ecm_result = factoring.ecm(n)
      if ecm_result:
        factordb_submit(q['id'], ecm_result)
        continue

      print('running GFS')
      gfs_result = factoring.gfs(n)
      if gfs_result:
        factordb_submit(q['id'], gfs_result)
        continue
