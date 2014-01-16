import bs4
import cgi
import requests
import chardet

def convert_to_unicode(r, detected_encoding):

  content = r.content

  encoding_guess = detected_encoding
  if content == '':
    return u''
  elif type(content) == unicode:
    return content
  else:
    return bs4.UnicodeDammit(content, [encoding_guess]).unicode_markup

def guess_encoding(response):
  '''
  Guesses the encoding for a document in the following order:
  1. content-type header
  2. content type from <meta..> tags
  3. content-type from chardet
  '''
  if 'content-type' in response.headers:
    content_type, params = cgi.parse_header(response.headers['content-type'])

    if 'charset' in params:
      return params['charset'].strip("'\"")
      
  meta_encodings = requests.utils.get_encodings_from_content(response.content[:min(len(response.content), 65536)])
  for charset in meta_encodings:
    return charset

  detected = chardet.detect(response.content)
  if detected:
    return detected['encoding']