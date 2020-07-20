from json.decoder import JSONDecodeError
from lxml import html
import requests
from requests.exceptions import RequestException
import time

# types: PRP=1, U=2, C=3, P=4
# returns a list of IDs
# factordb_list(t=3, min_digits=80, number=100, offset=0)
def listtype(t=3, min_digits=0, number=100, offset=0):
  params = {'t': t, 'mindig': min_digits, 'perpage': number, 'start': offset, 'download': 1}
  x = requests.get('http://factordb.com/listtype.php', params=params)
  return x.text.split('\n')[:-1]

def showid(ID):
  params = {'showid': ID}
  x = requests.get('http://factordb.com/index.php', params=params)
  tree = html.fromstring(x.content)
  return tree.xpath('/html/body/form/table/tr[3]/td[2]/text()')

def showstatus(ID):
  params = {'id': ID}
  x = requests.get('http://factordb.com/index.php', params=params)
  tree = html.fromstring(x.content)
  return tree.xpath('/html/body/table[2]/tr[3]/td[1]/text()')

# expected fields: id, status, factors
def query(n):
  return requests.get('http://factordb.com/api', params={'query': n}).json()

def submit(ID, factors):
  data = {'format': 0, 'report': '\n'.join(factors)}
  x = requests.post('http://factordb.com/index.php', params={'id': ID}, data=data)

# work source object for factordb
class FactorDB:
  def __init__(self, log, **config):
    self.log = log

    self.min_digits = config.get('min_digits', 79)
    self.number = config.get('number', 50)
    self.offset = config.get('offset', 0)

  # work generator
  # yields: identifier (for submission), number to factor
  def get_work(self):
    while True:
      l = []
      while not l:
        self.log('factordb: getting work')
        try:
          l = listtype(
            min_digits=self.min_digits,
            number=self.number,
            offset=self.offset)
          break
        except RequestException as e:
          self.log('factordb: listtype failed; retrying in 5 seconds')
          time.sleep(5)

      for n in l:
        try:
          q = query(n)
          if q['status'] != 'C':
            self.log('%s already factored' % n)
            continue
        except (JSONDecodeError, RequestException) as e:
          self.log('factordb: query failed; retrying in 5 seconds')
          time.sleep(5)

        yield q['id'], n

  def submit(self, id_, result):
    while True:
      try:
        submit(id_, result)
        break
      except RequestException as e:
        self.log('factordb: submit failed; retrying in 5 seconds')
        time.sleep(5)
