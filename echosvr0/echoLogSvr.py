#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   Teach Wisedom To Machine.
#   Please Call Me Programming devil.
#
######################################################## #
import logging.config
import sys

sys.path.append("..")
import netcore.BaseService as BaseService
from   netcore.EpollServer import EpollServer
from   netcore.MsgPipe import *
from   netcore.EpollComm import *
from   netcore.ServerConfig import *

logging.config.fileConfig("../conf/echologging.conf")
logger = logging.getLogger()
statuslogger = logging.getLogger("statusLogger")
netLogger = logging.getLogger("netLogger")
managerLogger = logging.getLogger("managerLogger")


#########################################################
class EchoAcceptor(BaseService.BaseAcceptor):
    def __init__(self, client_session_id=-1, client_socket=None, client_addr=()):
        super(EchoAcceptor, self).__init__(client_session_id, client_socket, client_addr)

    # how to keep live
    def keeplive(self):
        pass

    # how to unpack a packet from buffer
    def _unpack_frombuffer(self, buffer=""):
        return (len(buffer), buffer)

    # packet_data is full packet
    def _dispatch_packet(self, head=None, packet_data=""):
        # print "dispatch:",head.packet_cmd,len(packet_data)
        print len(packet_data), packet_data
        self.sendData(packet_data)


########################################################
class EchoSvr(EpollServer):
    # listen_addr_list is list of item as (ip,port)
    def __init__(self, listen_addr_list=[]):
        super(EchoSvr, self).__init__(listen_addr_list)
        self._listen_backlog = 128
        self._epoll_time_out = 1
        self._timer_time_out = 5
        self._max_session_count = 1024
        pass

    def onTcpConnectionEnter(self, session_id, client_socket, client_address):
        acceptor = EchoAcceptor(session_id, client_socket, client_address)
        return acceptor


##########################################################
def main():
    BaseService.project_index = current_project_index()

    servers = echo_server_config["servers"]
    project_index = BaseService.project_index
    if len(servers) < project_index + 1:
        managerLogger.debug("###############config errror###################")
        return
    server = servers[project_index]
    BaseService.listen_addr_list = [(server["host"], server["port"])]
    managerLogger.debug("select project_index:%d ip:%s port:%d", BaseService.project_index, server["host"],
                        server["port"])
    serv = EchoSvr(BaseService.listen_addr_list)
    BaseService.process_entry(serv)


if __name__ == '__main__':
    BaseService.work_process_count = 1
    main()
