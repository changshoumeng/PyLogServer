#!/usr/bin/env python
# -*- coding: utf-8 -*-
##########################################################
#   Teach Wisedom To Machine.
#   Please Call Me Programming devil.
#   Model Name: MsgPipe
######################################################## #
import Queue
import logging
import MultiProcessWrapper as mpw
statuslogger = logging.getLogger("statusLogger")


class PipeOutput(object):
    def out(self, msgnode):
        raise NotImplementedError()


class FeedbackPipe(object):
    callback = PipeOutput()
    warning_qsize=2000
    refuse_qsize=10000
    @staticmethod
    def push(msgnode):
        qsize=mpw.mp_feedback_queue.qsize()
        if qsize >= FeedbackPipe.refuse_qsize:
            statuslogger.critical("FeedbackPipe refuse;too long;qsize is %d",qsize)
            return
        mpw.mp_feedback_queue.put(msgnode)
        qsize = mpw.mp_feedback_queue.qsize()
        if qsize >= FeedbackPipe.warning_qsize:
            statuslogger.warning("FeedbackPipe warning;qsize is %d", qsize)

    @staticmethod
    def pop():
        try:
            msgnode = mpw.mp_feedback_queue.get_nowait()
            mpw.mp_feedback_queue.task_done()
            FeedbackPipe.callback.out(msgnode)
            return True
        except Queue.Empty:
            pass
        return False

    @staticmethod
    def size():
      return mpw.mp_feedback_queue.qsize()



class MsgPipe(object):
    callback = PipeOutput()
    warning_qsize=2000
    refuse_qsize=10000
    msgid = 0
    @staticmethod
    def push(sessionid=0,fileno=0, msgdata=""):
        msgid = MsgPipe.msgid
        MsgPipe.msgid += 1
        msgnode = (fileno, sessionid, msgid, msgdata)
        qsize=mpw.mp_message_queue.qsize()
        if qsize >= MsgPipe.refuse_qsize:
            statuslogger.critical("MsgPipe refuse;too long;qsize is %d;msgid is %d",qsize,msgid)
            return
        mpw.mp_message_queue.put(msgnode)
        qsize = mpw.mp_message_queue.qsize()
        if qsize >= MsgPipe.warning_qsize:
            statuslogger.warning("MsgPipe warning;qsize is %d", qsize)

    @staticmethod
    def pop():
        try:
            msgnode = mpw.mp_message_queue.get_nowait()
            mpw.mp_message_queue.task_done()
            MsgPipe.callback.out(msgnode)
            return True
        except Queue.Empty:
            pass
        return False

    @staticmethod
    def size():
      return mpw.mp_message_queue.qsize()


