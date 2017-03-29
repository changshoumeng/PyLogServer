#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   Teach Wisedom To Machine.
#   Please Call Me Programming devil.
#   Model Name: BaseService
######################################################## #
import MultiProcessWrapper as mpw
from EpollServer import *

logger = logging.getLogger()
statuslogger = logging.getLogger("statusLogger")
netLogger = logging.getLogger("netLogger")
managerLogger = logging.getLogger("managerLogger")
listen_addr_list = [("0.0.0.0", 8554)]
work_process_count = 5
project_index = 0
from socket import *

class BaseAcceptor(ConnectionBase):
    '''Init connection
    '''

    def __init__(self, client_session_id=-1, client_socket=None, client_addr=()):
        super(BaseAcceptor, self).__init__(client_session_id, client_socket, client_addr)
        self.connection_type = CONNECT_TYPE.IS_ACCEPTOR
        self.connect_status = CONNECT_STATUS.CONNECT_SUCC
        self.max_send_buffer_size = 1024 * 2
        self.max_recv_buffer_size = 1024 * 1024 * 10
        self.max_keeplive_time = 30000  # seconds
        self.send_count = 0
        self.task_list = []

    def onDisconnectEvent(self):
        if self.connect_status == CONNECT_STATUS.CONNECT_CLOSED:
            return
            # t= "_Acceptor::onDisconnectEvent fd:{0} reason:{1}".format(self.client_socket.fileno(), self.connect_status)
            # logger.warning(t)

    def onTimerEvent(self, current_time):
	#print "========================timeout"
	#self.client_socket.shutdown( SHUT_RDWR )
	#print "11111111111111"
        #self.client_socket.close()	
	#print "22222222222"
        if not super(BaseAcceptor, self).onTimerEvent(current_time):
            return False
        self.keeplive()
        return True

    # 处理收到的数据
    def _process_recv_buffer(self):
        global serviceRunningStatus
        total_bufsize = len(self.recv_buffer)
        has_unpack_bufsize = 0
        while has_unpack_bufsize < total_bufsize:
            (unpack_size, packet_head) = self._unpack_frombuffer(self.recv_buffer[has_unpack_bufsize:])
            if unpack_size == 0:
                break
            if unpack_size < 0:
                return unpack_size
            self._dispatch_packet(packet_head, self.recv_buffer[has_unpack_bufsize:has_unpack_bufsize + unpack_size])
            has_unpack_bufsize += unpack_size
            serviceRunningStatus.recv(unpack_size)
        # else:
        #    print "process all:",has_unpack_bufsize,total_bufsize
        return has_unpack_bufsize

    # how to unpack a packet from buffer
    def _unpack_frombuffer(self, buffer=""):
        raise NotImplementedError()
        return (0, None)

    # packet_data is full packet
    def _dispatch_packet(self, head=None, packet_data=""):
        print ">>_dispatch_packet"
        raise NotImplementedError()

    # how to keep live
    def keeplive(self):
        raise NotImplementedError()


class HeavyWorker(mpw.SimpleWorker):
    def __init__(self, worker_id=0, serv=None):
        super(HeavyWorker, self).__init__()
        self._worker_id = worker_id
        self._serv = serv
        pass

    def onStart(self):
        self.task_process_count = 0
        pid = os.getpid()
        pid = str(pid)
        if self._worker_id == 0:
            self._serv.start()
            managerLogger.info("tcpservice process start,pid:%s", pid)
            with open("run/tcpservice.pid", "w") as f:
                f.write(pid)
                f.write(" ")
            return
        if self._worker_id != 0:
            managerLogger.info("worker_%d process start,pid:%s", self._worker_id, pid)
            with open("run/worker_{0}.pid".format(self._worker_id), "w") as f:
                f.write(pid)
                f.write(" ")
                # exec("from gevent import monkey; monkey.patch_all();import gevent;")
        pass

    def onEnd(self, end_code, end_reason):
        if self._worker_id == 0:
            pid = os.getpid()
            managerLogger.info("tcpservice end at pid:{0} reason:{1}".format(pid, end_reason))
        if end_code < 0:
            print end_reason
            return
        if end_code == 2:
            self.onExit()
        pass

    def onRunOnce(self):
        if self._worker_id == 0:
            self._serv.serve_once()
            return
        processNum = 0
        processMaxNum = 1000
        for i in xrange(processMaxNum):
            if self._serv.work_once():
                processNum += 1
        if processNum < processMaxNum:
            time.sleep(0.01)

    def onTimer(self):
        pass

    def onExit(self):
        if self._worker_id == 0:
            self._serv.stop()
        pass


class MasterTimer(mpw.TimerInterface):
    def __init__(self):
        pass

    def timeout(self):
        return 2

    def onTimer(self):
        pass


def process_entry(serv):
    global work_process_count
    pid = os.getpid()
    pid = str(pid)
    managerLogger.info("master process start,pid:%s,workercount:%d", pid, work_process_count)
    with open("run/master.pid", "w") as f:
        f.write(pid)
        f.write(" ")
    if work_process_count == 1:
        print "single_process_entry>> begin"
        InterruptableTaskLoop(serv).startAsForver()
        print "single_process_entry>> end"
        return
    managerLogger.debug("###############begin###################")
    worker_list = [HeavyWorker(i, serv) for i in range(work_process_count)]
    p = mpw.MultiProcessWrapper()
    p.startAsForver(worker_list, MasterTimer())
    managerLogger.debug("###############end###################")
