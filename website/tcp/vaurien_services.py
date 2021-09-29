# -*- coding: utf-8 -*-
"""
    website.tcp.services
    ~~~~~~~~~~~~~~~~

    TCP Proxy services api.
"""

import os
import sys
import subprocess

from website import db
from website.tcp.models import Connection


tmp_file_path = "%s/flex_vaurien" % os.path.dirname(sys.executable)
connection_command = u"%s --protocol-tcp-keep-alive --stay-connected --protocol tcp --proxy 0.0.0.0:{local_port} --backend {dest_ip}:{dest_port}" % tmp_file_path

vaurien_code = '''#!%s
import re
import sys

import vaurien
from vaurien.run import main

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
''' % sys.executable


def get_connections():
  connections = Connection.query.all()
  return connections


def create_connection(local_port, dest_ip, dest_port):
  pid = open_connection(local_port, dest_ip, dest_port)
  connection = Connection(dest_ip, dest_port, local_port, pid)
  db.session.add(connection)
  db.session.commit()
  return connection


def open_connection(local_port, dest_ip, dest_port):
  with os.fdopen(os.open(tmp_file_path, os.O_WRONLY | os.O_CREAT, 0700), 'w') as f:
    f.write(vaurien_code)
  command = connection_command.format(local_port=local_port, dest_ip=dest_ip, dest_port=dest_port)
  print command
  result = execute_command(command)
  return result.pid


def delete_connection(connection_id):
  connection = Connection.query.get(connection_id)
  if connection is not None:
    execute_command("kill %d" % connection.pid)
    Connection.query.filter(Connection.id == connection_id).delete()
    db.session.commit()


def execute_command(command):
  return subprocess.Popen(command.split())
