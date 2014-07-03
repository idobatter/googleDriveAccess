#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''test_folder_hierarchy
'''

import sys, os
import socket

from oauth2client.anyjson import simplejson
import googleDriveAccess

import logging
logging.basicConfig()

FOLDER_TYPE = 'application/vnd.google-apps.folder'

def getlist(ds, q, **kwargs):
  result = None
  npt = ''
  while not npt is None:
    if npt != '': kwargs['pageToken'] = npt
    entries = ds.files().list(q=q, **kwargs).execute()
    if result is None: result = entries
    else: result['items'] += entries['items']
    npt = entries.get('nextPageToken')
  return result

def uenc(u):
  if isinstance(u, unicode): return u.encode('utf-8')
  else: return u

def walk(ds, folderId, folderName, outf, depth):
  spc = ' ' * depth
  outf.write('%s+%s\n%s  %s\n' % (spc, uenc(folderId), spc, uenc(folderName)))
  q = "'%s' in parents and mimeType='%s'" % (folderId, FOLDER_TYPE)
  entries = getlist(ds, q, **{'maxResults': 200})
  for folder in entries['items']:
    walk(ds, folder['id'], folder['title'], outf, depth + 1)
  q = "'%s' in parents and mimeType!='%s'" % (folderId, FOLDER_TYPE)
  entries = getlist(ds, q, **{'maxResults': 200})
  for f in entries['items']:
    outf.write('%s -%s\n%s   %s\n' % (spc, uenc(f['id']), spc, uenc(f['title'])))

def main(basedir):
  da = googleDriveAccess.DAClient(basedir) # clientId=None, script=False
  f = open(os.path.join(basedir, 'hierarchy.txt'), 'wb')
  walk(da.drive_service, 'root', u'root', f, 0)
  f.close()

if __name__ == '__main__':
  logging.getLogger().setLevel(getattr(logging, 'INFO')) # ERROR
  try:
    main(os.path.dirname(__file__))
  except (socket.gaierror, ), e:
    sys.stderr.write('socket.gaierror')
