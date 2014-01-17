import bs4
import cgi
import requests
import chardet

from pkg_resources import resource_stream
from configobj import ConfigObj, flatten_errors
from validate import Validator

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

def load_config(module_name, cfg_file=None):
    '''
    Loads a config file and returns a ConfigObj. A default configuration
    file is also loaded from the directory containing the module given
    by module_name.
    '''

    if module_name == None:
        module_name = __name__
        base_config = {}
    else:
        base_config = load_config(None, cfg_file)

    configspec = resource_stream(module_name, 'defaults.ini')
    config = ConfigObj(cfg_file, configspec=configspec)
    validator = Validator()
    valid = config.validate(validator)
    if not valid:
        for (section_list, key, _) in flatten_errors(config, valid):
            if key is not None:
                print 'The "%s" key in the section "%s" failed validation' % \
                        (key, ', '.join(section_list))
            else:
                print 'The following section was missing:%s ' % \
                        ', '.join(section_list)

    for sec, cfg in config.items():
       if sec in base_config:
           base_config[sec].update(cfg)
       else:
           base_config[sec] = cfg

    return base_config