#!/usr/bin/env python

import ConfigParser
import os
import re
import sys

from ravel.log import logger

class ConnectionType:
    Ovs = 0
    Rpc = 1
    Mq = 2
    Name = { "ovs" : Ovs,
             "rpc" : Rpc,
             "mq" : Mq
         }

def _libpath(path=None):
    install_path = os.path.dirname(os.path.abspath(__file__))
    install_path = os.path.normpath(
        os.path.join(install_path, ".."))

    if not path:
        return install_path

    return os.path.normpath(os.path.join(install_path, path))

def update_trigger_path(filename, path):
    path = os.path.expanduser(path)
    if not os.path.isfile(filename):
        logger.warning("cannot find sql file %s", filename)
        return

    with open(filename, 'r') as f:
        lines = []
        content = f.read()

    newstr = "sys.path.append('{0}')".format(path)
    pattern = re.compile(r"sys.path.append\(\S+\)")
    content = re.sub(pattern, newstr, content)

    open(filename, 'w').write(content)

def append_path(path):
    path = os.path.expanduser(path)
    if 'PYTHONPATH' not in os.environ:
        os.environ['PYTHONPATH'] = ""

    sys.path = os.environ['PYTHONPATH'].split(':') + sys.path

    if path is None or path == "":
        path = "."

    if path not in sys.path:
        sys.path.append(path)

def resource_string(name):
    path = os.path.join(_libpath(), name)
    print path
    if os.path.isfile(name):
        return open(path, 'r').read()
    else:
        logger.error("cannot read file %s", path)

def resource_file(name=None):
    if name is None:
        return _libpath()
    return os.path.join(_libpath(), name)

class ConfigParameters(object):
    def __init__(self):
        self.RpcHost = None
        self.RpcPort = None
        self.QueueId = None
        self.Connection = None
        self.PoxDir = None
        self.read(resource_file("ravel.cfg"))

    def read(self, cfg):
        parser = ConfigParser.SafeConfigParser()
        parser.read(cfg)

        if parser.has_option("of_manager", "poxdir"):
            self.PoxDir = parser.get("of_manager", "poxdir")

        if parser.has_option("of_manager", "connection"):
            name = parser.get("of_manager", "connection").lower()
            self.Connection = ConnectionType.Name[name]

        if parser.has_option("rpc", "rpchost"):
            self.RpcHost = parser.get("rpc", "rpchost")
        if parser.has_option("rpc", "rpcport"):
            self.RpcPort = parser.getint("rpc", "rpcport")

        if parser.has_option("mq", "queueid"):
            self.QueueId = parser.getint("mq", "queueid")

Config = ConfigParameters()
