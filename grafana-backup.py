#!/usr/bin/env python
#
# grafana-backup.py
#
# Author: Matteo Cerutti <matteo.cerutti@hotmail.co.uk>
#

import argparse
import time
import yaml
import json
import requests
import sys
import tempfile
import os
import shutil
import tarfile
import logging

class GrafanaBackup:
  def __init__(self, **kwargs):
    if (('api_key' not in kwargs or kwargs['api_key'] is None) and \
       ('username' not in kwargs or kwargs['username'] is None or 'password' not in kwargs or kwargs['password'] is None)) or \
       (('api_key' in kwargs and kwargs['api_key'] is not None) and \
       ('username' in kwargs and kwargs['username'] is not None or 'password' in kwargs and kwargs['password'] is not None)):
      raise ValueError("Either API key or username/password must be given")

    if 'api_host' not in kwargs or 'api_host' is None:
      raise ValueError("API host must be given")

    if 'api_port' not in kwargs or 'api_port' is None:
      raise ValueError("API port must be given")

    if 'output_file' not in kwargs or 'output_file' is None:
      raise ValueError("Output tarball must be given")

    self.opts = kwargs

    logger = logging.getLogger("Grafana")
    if kwargs['loglevel']:
      logger.setLevel(getattr(logging, kwargs['loglevel']))
    else:
      logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s [%(filename)s:%(lineno)s %(funcName)s()]: %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    self.logger = logger

    # set up temporary dir
    self.tmpdir = tempfile.mkdtemp() + '/' + os.path.splitext(os.path.basename(self.opts['output_file']))[0]

  def api_read(self, query):
    try:
      uri = []
      path = []

      uri.append("http://")
      if self.opts['api_key'] is not None:
        headers = {'Authorization':'Bearer ' + self.opts['api_key']}
      else:
        headers = {}
        uri.append(self.opts['username'] + ':' + self.opts['password'])
        uri.append('@')

      uri.append(self.opts['api_host'])
      uri.append(':')
      uri.append(str(self.opts['api_port']))

      path.append("api")
      path.append(query)

      data = requests.get(''.join(uri) + '/' + '/'.join(path), headers=headers).json()

      if 'message' in data:
        raise Exception("failed to run query against " + '/'.join(path) + ": " + data['message'])

      return data
    except Exception, e:
      self.logger.error("Caught exception: %s" % str(e))

  def list_datasources(self):
    return self.api_read('datasources')

  def list_dashboards(self):
    return self.api_read('search')

  def list_orgs(self):
    return self.api_read('orgs')

  def list_users(self):
    return self.api_read('users')

  def get_dashboard(self, uri):
    return self.api_read("dashboards/" + uri)

  def dump_dashboards(self):
    output_dir = self.tmpdir + "/dashboards"

    # create output directory if doesn't exist
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    dashboards = self.list_dashboards()
    if dashboards is not None:
      dashboards.append({'title': 'Home dashboard', 'uri': 'home'})
      for dash in dashboards:
        data = self.get_dashboard(dash['uri'])
        # later needed to import it
        data['dashboard']['id'] = None
        uri = dash['uri']
        if uri != 'home':
          uri = dash['uri'].split('/')[1] 
        file = output_dir + "/" + uri.replace(' ', '_') + ".json"
        with open(file, 'w') as fd:
          self.logger.info("Saving dashboard '" + dash['title'] + "' to " + file)
          json.dump(data, fd)

  def dump_datasources(self):
    output_dir = self.tmpdir + "/datasources"

    # create output directory if doesn't exist
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    datasources = self.list_datasources()
    if datasources is not None:
      for ds in datasources:
        file = output_dir + "/" + ds['name'].replace(' ', '_') + ".json"
        with open(file, 'w') as fd:
          self.logger.info("Saving datasource '" + ds['name'] + "' to " + file)
          json.dump(ds, fd)

  def dump_orgs(self):
    output_dir = self.tmpdir + "/orgs"

    # create output directory if doesn't exist
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    orgs = self.list_orgs()
    if orgs is not None:
      for org in orgs:
        file = output_dir + "/" + org['name'].replace(' ', '_') + ".json"
        with open(file, 'w') as fd:
          self.logger.info("Saving organization '" + org['name'] + "' to " + file)
          json.dump(org, fd)

  def dump_users(self):
    output_dir = self.tmpdir + "/users"

    # create output directory if doesn't exist
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    users = self.list_users()
    if users is not None:
      for user in users:
        file = output_dir + "/" + user['login'].replace(' ', '_') + ".json"
        with open(file, 'w') as fd:
          self.logger.info("Saving user '" + user['login'] + "' to " + file)
          json.dump(user, fd)

  def dump_frontend(self):
    frontend_settings = self.api_read("frontend/settings")
    if frontend_settings is not None:
      file = self.tmpdir + "/frontend_settings.json"
      with open(file, 'w') as fd:
        self.logger.info("Saving frontend settings to " + file)
        json.dump(frontend_settings, fd)

  def dump_admin(self):
    admin_settings = self.api_read("admin/settings")
    if admin_settings is not None:
      file = self.tmpdir + "/admin_settings.json"
      with open(file, 'w') as fd:
        self.logger.info("Saving admin settings to " + file)
        json.dump(admin_settings, fd)

  def do_archive(self, dst, src):
    with tarfile.open(dst, "w:gz") as tar:
      self.logger.info("Archiving " + src + " into " + dst)
      tar.add(src, arcname = os.path.basename(src))

  def run(self):
    if os.path.exists(self.opts['output_file']):
      raise StandardError("Output tarball already exists, remove it first")

    self.dump_dashboards()
    self.dump_datasources()
    self.dump_orgs()
    self.dump_users()
    self.dump_frontend()
    self.dump_admin()

    # archive temporary dir
    try:
      self.do_archive(self.opts['output_file'], self.tmpdir)
      self.logger.info("Completed")
    except Exception, e:
      self.logger.info("Caught exception: " + str(e))
      return False

    return True

  def __del__(self):
    # delete temporary dir
    shutil.rmtree(self.tmpdir)

def parse_opts():
  parser = argparse.ArgumentParser(description='Grafana Backup Tool')
  parser.add_argument("-H", "--host", action="store", dest="api_host", default="127.0.0.1", help="API host (default: %(default)s)")
  parser.add_argument("-P", "--port", action="store", dest="api_port", default=3001, help="API port (default: %(default)s)")
  parser.add_argument("-k", "--key", action="store", dest="api_key", help="API key")
  parser.add_argument("-u", "--user", action="store", dest="username", help="User for basic authentication")
  parser.add_argument("-p", "--password", action="store", dest="password", help="Password for basic authentication")
  parser.add_argument("-o", "--output", action="store", dest="output_file", default="./grafana-backup-" + time.strftime("%Y%m%d%H%M%S") + ".tgz", help="Output tarball (default: %(default)s)")
  parser.add_argument("-c", "--config", action="store", dest="config_file", default="./grafana-backup.yaml", help="Optional configuration file to read options from (default: %(default)s)")
  parser.add_argument("-l", "--log-level", action="store", dest="loglevel", default="INFO", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level (default: %(default)s)")
  opts = parser.parse_args()

  if os.path.isfile(opts.config_file):
    try:
      with open(opts.config_file, 'r') as stream:
        data = yaml.load(stream)
        if data is not None:
          for k, v in data.iteritems():
            setattr(opts, k, v)
    except Exception, e:
      print("Caught exception: " + str(e))
      sys.exit(1)

  if (opts.api_key is None and opts.username is None and opts.password is None) or (opts.api_key is not None and (opts.username is not None or opts.password is not None)):
    parser.error("You must specify either an API key for token authentication or an username/password for basic authentication")

  return opts

if __name__ == "__main__":
  # convert to dict
  app = GrafanaBackup(**vars(parse_opts()))
  sys.exit(app.run())
