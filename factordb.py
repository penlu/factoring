import aiohttp
from aiohttp import ClientError, ClientSession, TCPConnector
from lxml import html
import time

# work source object for factordb
class FactorDB:
  def __init__(self, log, **config):
    self.log = log

    self.min_digits = config.get('min_digits', 79)
    self.number = config.get('number', 50)
    self.offset = config.get('offset', 0)

    # create session with limited parallel connections
    connector = TCPConnector(limit_per_host=4)
    self.session = ClientSession(connector=connector)

  # types: PRP=1, U=2, C=3, P=4
  # returns a list of IDs
  # factordb_list(t=3, min_digits=80, number=100, offset=0)
  async def listtype(self, t=3, min_digits=0, number=100, offset=0):
    params = {'t': t, 'mindig': min_digits, 'perpage': number, 'start': offset, 'download': 1}
    async with self.session.get(
        'http://factordb.com/listtype.php',
        params=params) as resp:
      text = await resp.text()
      return text.split('\n')[:-1]

  async def showid(self, ID):
    params = {'showid': ID}
    async with self.session.get(
        'http://factordb.com/index.php',
        params=params) as resp:
      tree = html.fromstring(resp.read())
      return tree.xpath('/html/body/form/table/tr[3]/td[2]/text()')

  async def showstatus(self, ID):
    params = {'id': ID}
    async with self.session.get(
        'http://factordb.com/index.php',
        params=params) as resp:
      tree = html.fromstring(resp.read())
      return tree.xpath('/html/body/table[2]/tr[3]/td[1]/text()')

  # expected fields: id, status, factors
  async def query(self, n):
    async with self.session.get(
        'http://factordb.com/api',
        params={'query': n}) as resp:
      return await resp.json()

  async def submit(self, ID, factors):
    data = {'format': 0, 'report': '\n'.join(factors)}
    await self.session.post(
        'http://factordb.com/index.php',
        params={'id': ID},
        data=data)

  # work generator
  # yields: identifier (for submission), number to factor
  async def get_work(self):
    while True:
      l = []
      while not l:
        self.log('factordb: getting work')
        try:
          l = await self.listtype(
            min_digits=self.min_digits,
            number=self.number,
            offset=self.offset)
          break
        except ClientError as e:
          self.log('factordb: listtype failed; retrying in 5 seconds')
          time.sleep(5)

      for n in l:
        yield n

  async def put_work(self, id_, result):
    while True:
      try:
        await self.submit(id_, result)
        break
      except ClientError as e:
        self.log('factordb: submit failed; retrying in 5 seconds')
        time.sleep(5)
