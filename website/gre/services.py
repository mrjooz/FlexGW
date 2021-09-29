# -*- coding: utf-8 -*-
"""
    website.tcp.services
    ~~~~~~~~~~~~~~~~

    TCP Proxy services api.
"""

import subprocess
import commands

from website import db
from website.gre.models import GRETunnel

create_tunnel_command = "ip tunnel add {tunnel_id} mode gre remote {remote_router_ip} local {local_router_ip} ttl {ttl}"
delete_tunnel_command = "ip tunnel del {tunnel_id}"
tunnel_up_command = "ip link set {tunnel_id} up"
tunnel_down_command = "ip link set {tunnel_id} down"
add_route_command = "ip route add {subnet} dev {tunnel_id}"


def create_tunnel(local_router_ip, remote_router_ip, subnet):
  max_tunnel_id = db.session.query(db.func.max(GRETunnel.tunnel_id)).scalar()
  if max_tunnel_id is None:
    max_tunnel_id = 0
  tunnel = GRETunnel(local_router_ip, remote_router_ip, subnet, max_tunnel_id + 1)
  try:
    db.session.add(tunnel)
    db.session.commit()
  except:
    db.session.rollback()
    raise
  open_tunnel(tunnel)
  return tunnel


def delete_tunnel(id):
  tunnel = GRETunnel.query.get(id)
  if tunnel is not None:
    close_tunnel(tunnel.tunnel_id)
    try:
      GRETunnel.query.filter(GRETunnel.id == id).delete(False)
      db.session.commit()
    except:
      db.session.rollback()
      ensure_all_tunnels()
      raise


def get_tunnels():
  tunnels = GRETunnel.query.all()
  return tunnels


def reset_all_tunnels():
  tunnels = GRETunnel.query.all()
  for tunnel in tunnels:
    close_tunnel(tunnel.tunnel_id)
    open_tunnel(tunnel)


def ensure_all_tunnels():
  tunnels_in_db = GRETunnel.query.all()
  tunnels = commands.getoutput("ip tunnel show |grep -F 'gre/ip'")
  tunnels_in_system = {}
  for tunnel_line in tunnels.split("\n"):
    # gre1: gre/ip  remote 123.125.97.122  local 139.196.193.125  ttl 255
    tunnel_id, tunnel_body = tuple(tunnel_line.split(":"))
    tunnel_parts = tunnel_body.split()
    tunnel = {
        "remote": tunnel_parts[2],
        "local": tunnel_parts[4],
        "ttl": tunnel_parts[6]
    }
    tunnels_in_system[tunnel_id] = tunnel

  for tunnel in tunnels_in_db:
    tunnel_id = "gre%d" % tunnel.tunnel_id
    if tunnel_id not in tunnels_in_system:
      open_tunnel(tunnel)


def open_tunnel(tunnel):
  tunnel_id = "gre%d" % tunnel.tunnel_id
  execute_command(create_tunnel_command.format(tunnel_id=tunnel_id,
                                               remote_router_ip=tunnel.remote_router_ip,
                                               local_router_ip=tunnel.local_router_ip,
                                               ttl=tunnel.ttl))
  execute_command(tunnel_up_command.format(tunnel_id=tunnel_id))
  execute_command(add_route_command.format(subnet=tunnel.subnet, tunnel_id=tunnel_id))


def close_tunnel(tunnel_id):
  tunnel_id = "gre%d" % tunnel_id
  execute_command(tunnel_down_command.format(tunnel_id=tunnel_id))
  execute_command(delete_tunnel_command.format(tunnel_id=tunnel_id))


def execute_command(command, retris=3):
  if retris < 0:
    return None

  sp = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
  data = sp.communicate()[0]
  if sp.returncode != 0:
    return execute_command(command, retris - 1)

  return data
