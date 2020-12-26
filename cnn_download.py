from requests import get
from bs4 import BeautifulSoup as bs
from sqlite3 import connect
from os.path import exists
DB = 'test.db'

if not exists(DB):
  db = connect(DB)
  cur = db.cursor()
  cur.execute('CREATE TABLE articles (url,title,body,year,month)')
  db.commit()
  db.close()

sitemap_url = 'https://www.cnn.com/article/sitemap'

def get_cursor():
  db = connect(DB)
  return db.cursor()

def get_year(year):
  cur = get_cursor()
  for m in range(1,13):
    print('------------------------------------------')
    print("Downloading article links for {1} {0}".format(year,m))
    r = get("{}-{}-{}.html".format(sitemap_url,year,m))
    try:
      soup = bs(r.content,features="lxml")
      links = [(i.get('href'),i.text,'',year,m) for i in soup.findAll('a') if not i.get('class')]
    except:
      pass  
    count = len(links)
    sql = 'INSERT INTO articles VALUES(?,?,?,?,?)'
    if cur.executemany(sql,links):
      print("Links for {} articles.".format(count,m))
    else:
      print('Database error!!!')
    db.commit()
    db.close()

def pop_body(max_amount):
  cur = get_cursor() 
  for i in range(max_amount):
    url = cur.execute('SELECT url FROM articles WHERE body="" LIMIT 1;').fetchone()[0]
    text = get_article(url)
    cur.execute('UPDATE articles SET body=? WHERE url=?',(text,url))
    print("Added {} word article to database".format(len(text.split(' '))))
    db.commit()
    db.close()
    
def get_article(url):
  r = get(url)
  soup = bs(r.content)
  return soup.find('article').text

if __name__ == '__main__':
  get_year(2020)

db.close()
