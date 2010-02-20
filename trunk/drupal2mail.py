#!/usr/bin/env python

import logging
import logging.handlers
import re
import MySQLdb
import xmlrpclib
import yaml

CONFIG_FILE = 'drupal2mail.yaml'
DRY_RUN = True

# Global variables
cfg = None
log = None

def _ReadConfig():
  global cfg
  cfg = yaml.load(open(CONFIG_FILE, 'r'))

def _InitLog():
  global log
  log = logging.getLogger('drupal2mail')
  log.setLevel(logging.DEBUG)
  handler = logging.FileHandler(cfg['logs']['filename'])
  fmt = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s", '%Y-%m-%d %H:%M:%S')
  handler.setFormatter(fmt)
  log.addHandler(handler)

def Init():
  _ReadConfig()
  _InitLog()

def _GetAPI():
  """Returns a pointer to a server object and a session id for the API."""
  global cfg
  if not '__sid__' in cfg['api']:
    cfg['api']['__server__'] = xmlrpclib.ServerProxy(cfg['api']['endpoint'])
    sid, account = cfg['api']['__server__'].login(
        cfg['api']['login'], cfg['api']['password'])
    cfg['api']['__sid__'] = sid
  return cfg['api']['__server__'], cfg['api']['__sid__']


def GetTargets():
  """Reads current email mappings from the mail server.
  Returns:
    A dict of the form {username@domain.com: registered email address}
    where: 
      'username' is a Drupal's username;
      'domain.com' is as configured in drupal2mail.yaml
      'registered email address' is the email address used by 'username' upon
      registration in Drupal
  """
  log.debug('Reading target emails...')
  pattern = re.compile('^(.*)(%s)$' % cfg['mail']['domain'])
  server, sid = _GetAPI()
  target_list = [(x['email_address'], x['targets'])
      for x in server.list_emails(sid)
      if re.match(pattern, x['email_address'])]
  targets = {}
  for email, target in target_list:
    targets[email] = target
  log.debug('Target emails: %s', targets)
  return targets


def GetSources(role='%'):
  """Reads current email mappings from Drupal's database.
  Args:
    role: (optional) A role from the 'role' Drupal's table.
  Returns:
    A dict that maps 'drupal-username@maildomain' to a target email address.
  """
  db = MySQLdb.connect(
      host=cfg['database']['host'], user=cfg['database']['user'],
      passwd=cfg['database']['pass'], db=cfg['database']['name'])
  cursor = db.cursor()
  cursor.execute('SELECT users.name, users.mail '
      'FROM users '
      'LEFT JOIN users_roles USING (uid) '
      'LEFT JOIN role USING (rid) '
      'WHERE role.name LIKE "%s"' % role)
  data = cursor.fetchall()
  sources = {}
  for row in data:
    sources[row[0].lower()] = row[1].lower()
  db.close()
  log.debug('Source emails: %s', sources)
  return sources


def CreateEmailEntry(source, target):
  log.info('Creating %s -> %s redirection' % (source, target))
  if not DRY_RUN:
    server, sid = _GetAPI()
    server.create_email(sid, source, target)


def UpdateEmailEntry(source, target):
  log.info('Updating %s -> %s redirection' % (source, target))
  if not DRY_RUN:
    server, sid = _GetAPI()
    server.update_email(sid, source, target)


def UpdateEmails(sources, targets):
  """Updates targets with sources."""
  for username, email in sources.items():
    username = '%s@%s' % (username, cfg['mail']['domain'])
    if username in targets:
      target = targets[username]
      if target != email:
        UpdateEmailEntry(username, email)
    else:
      CreateEmailEntry(username, email)


def Main(argv=None):
  sources = GetSources()
  targets = GetTargets()
  UpdateEmails(sources, targets)

if __name__ == '__main__':
  Init()
  Main()
