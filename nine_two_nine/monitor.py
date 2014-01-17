from urlparse import urljoin, urlparse
import logging
import sys
import bs4
import requests
from util import guess_encoding, convert_to_unicode
import time
import smtplib

class Monitor(object):
  def __init__(self, sites, from_email, to_email, username, password,
               bloom_filter, sleeptime=300):
    self.sites = sites
    self.email = email
    self.username = username
    self.password = password
    self.sleeptime = sleeptime
    self.bf = bloom_filter

  def run(self):
    while True:
      for url in sites:
        html = scrape_url(url)
        fetched_links = self.extract_links(html, url)
        filtered_links = self.filter_links(fetched_links)
        for link in filtered_links:
          self.notify_via_email(link)

  def scrape_url(self, url):
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
     
  def extract_links(self, page, root_url):
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

  def filter_links(self, links):
    new_links = []
    for link in links:
      if link.startswith('mailto'):
        self.bf.add(link)
      if link not in bf:
        new_links.append(link)
        self.bf.add(link)
    return new_links

  def notify_via_email(self, link):
    subject = "New link found by nine_two_nine"
    message = """\From: %s\n
                  To: %s\n
                  Subject: %s\n\n
                  %s
              """ % (FROM, ", ".join([self.to_email]), subject, link)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465
        server.ehlo()
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.from_email, self.to_email, message)
        server.close()
        logging.info("Email successfully sent.")
    except:
        logging.error("Email failed to send.")
