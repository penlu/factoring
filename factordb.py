import requests
from lxml import html

# types: PRP=1, U=2, C=3, P=4
# returns a list of IDs
# factordb_list(3, 80, 100, 0)
def factordb_list(t=3, min_digits=0, number=100, offset=0):
  params = {'t': t, 'mindig': min_digits, 'perpage': number, 'start': offset, 'download': 1}
  x = requests.get('http://factordb.com/listtype.php', params=params)
  #return [a.attrib['href'].split('=')[1] for a in tree.xpath('/html/body/table[2]/tr/td[2]/a[2]')] # for download=0
  return x.text.split('\n')[:-1]

def factordb_showid(ID):
  params = {'showid': ID}
  x = requests.get('http://factordb.com/index.php', params=params)
  tree = html.fromstring(x.content)
  return tree.xpath('/html/body/form/table/tr[3]/td[2]/text()')

def factordb_showstatus(ID):
  params = {'id': ID}
  x = requests.get('http://factordb.com/index.php', params=params)
  tree = html.fromstring(x.content)
  return tree.xpath('/html/body/table[2]/tr[3]/td[1]/text()')

# expected fields: id, status, factors
def factordb_query(n):
  return requests.get('http://factordb.com/api', params={'query': n}).json()

def factordb_submit(ID, factors):
  data = {'format': 0, 'report': '\n'.join(factors)}
  x = requests.post('http://factordb.com/index.php', params={'id': ID}, data=data)
