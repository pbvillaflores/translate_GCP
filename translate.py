# -*- coding: utf-8 -*-
# had to handle quoting, and quotes have to be restored when translate does not put them in 
#
# GCP translate service
# https://cloud.google.com/translate/docs/quickstart-client-libraries#client-libraries-install-python

RIYADH = 'الرياض'

import pickle
import chardet
from googletrans import Translator
from translation import baidu, google, youdao, iciba, bing
from google.cloud import translate
import os
path = r'apikey.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
import csv

import sqlite3


translator = Translator()
translate_client = translate.Client()

#incidents 
fn  = r'source_utf8.csv'
fn2  = r'translated_eng.csv'
fnsave = r'save.dat'
import time 

with open(fn, encoding='utf-8') as f:
  r=f.readlines()
  
d0 = {}

def xlate(e):
  global translator
  for j in range(5):
      try:

          a = translate_client.translate(
              e,
              target_language='en')['translatedText']
          if (len(a) > 0 and len(e)>0 ) and a[0] != '"' and (e[0] == '"'  or ',' in a ) :
                a = '"' + a + '"'
                
          return a
          #return translator.translate( e ).text
          #a =  gs.translate(e, 'en')
          #return  a

      except Exception as ex:
          print(ex)
          print('  <-- Exception at attempt ',j)
          #translator = Translator()
          #return translator.translate( e ).text
          
          time.sleep(25)
          if j == 4:
              print('saving d0... ', len(d0) )
              with open(fnsave, 'wb') as f:
                  pickle.dump( d0, f)
              exit(1)

with open(fnsave, 'rb') as f:
    d0 = pickle.load(f)

import array
with open(fn2,'w', encoding = 'utf-8') as f:
  hits_dict = 0
  requests = 0 
  no_trans = 0
  skip = 0
  for c,s in enumerate(  csv.reader(r, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)  ):
    #s = i.split(',')
    xlated_line = ''
    if s[0] == RIYADH:
      skip += 1
      continue
    for i in s:
      #b = bytearray()
      #b.extend(map(ord, i))
      enc = chardet.detect( i.encode('utf-8') )
      if enc['encoding'] != 'ascii':
      
        try:
            if i in d0: 
              xlated = d0[i]
              hits_dict+=1
            else:
              xlated =  xlate( i )
              requests+=1
              d0[i] = xlated
        except Exception as e:
          print(e)
          print('Except at line ',c)
          with open(fnsave, 'wb') as f:
              pickle.dump( d0, f)
          exit(1)
      else:
        xlated = i
        no_trans+=1
      xlated_line += ','+xlated
    f.write( xlated_line[1:] + '\n' )
    if (c % 10000==0):
      print(c,'hits_dict',hits_dict,'requests',requests,'no_trans',no_trans,'skip',skip)
  
  
with open(fnsave, 'wb') as f:
    pickle.dump( d0, f)
