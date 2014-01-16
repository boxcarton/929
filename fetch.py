from urlparse import urljoin, urlparse
import logging
import sys
import bs4
import requests
from util import guess_encoding, convert_to_unicode
from pybloomfilter import BloomFilter

def fetch_url(url):
  r = None
  html = ''
  isBase64 = False
  detected_encoding = 'UTF-8'
  unicode_content = ''

  try:
    r = requests.get(url, stream=True)
    r.raise_for_status()

    content = r.content 
    detected_encoding = guess_encoding(r)

  except requests.HTTPError, e:
    logging.info(u'%s - HTTPError %s' % (url, r.status_code))
  except requests.RequestException, e:
    err_type = e.__class__.__name__
    logging.error(u'%s - %s - %s' % (url, 
                     err_type, 
                     unicode(repr(e),
                     errors='replace')))
  except Exception, e:
    logging.exception(e)
    logging.critical(u"Critical exception %s for %s", e, url)
  finally:
    if r and r.raw:
      unicode_content = convert_to_unicode(r, detected_encoding)
      r.raw.release_conn()
    return unicode_content
   
def extract_links(page, root_url):
  link_strainer = bs4.SoupStrainer(['base', 'a'])
  soup = bs4.BeautifulSoup(page, parse_only=link_strainer)
  base = soup.find_all('base', limit=1)
  if base and base[0].has_attr('href'):
    root_url = base[0]['href'].strip()
    
  # TODO: Check for and handle invalid URLs
  try:
    links = [urljoin(root_url.strip(), l['href'].strip()) for l in soup.find_all('a')
            if isinstance(l, bs4.element.Tag) and l.has_attr('href')]
  except Exception, e:
    print e
    logging.error("Error handling %s", root_url)
    logging.exception(e)
  return links

def filter_links(links, bf):
  for link in links:
    if link.startswith('mailto'):
      bf.add(link)
    if link not in bf:
      print "New Link Found: " + link
      bf.add(link)

def main(args):
  bf = BloomFilter.open('links_filter.bloom')
  url = 'http://www.930.com/concerts/'

  fetched_links = extract_links(fetch_url(url), url)
  filtered_links = filter_links(fetched_links, bf)

if __name__ == '__main__':
  main(sys.argv[1:])