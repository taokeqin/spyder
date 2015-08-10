# -*- coding: utf-8 -*-
"""
    threadpool.py
    ~~~~~~~~~
    This module implements the threadpool and it's related taskqueue.
    :copyright: (c) 2015 by Tao Keqin.
    :license: BSD, see LICENSE for more details.
"""
from threading import Thread, Lock
from Queue import Queue


class TaskQueue(Queue, object):
    '''
        wraper on Queue to provide statistics function
    '''
    def __init__(self):
        Queue.__init__(self)
        self.counter = 0
        self.counterlock = Lock()

    def put(self, task):
        '''put a task to queue and increment counter for statistics use'''
        self.counterlock.acquire()
        self.counter = self.counter + 1
        super(TaskQueue, self).put(task)
        self.counterlock.release()

    def statistics(self):
        '''returen the statistics data.'''
        self.counterlock.acquire()
        totaltaskcount = self.counter
        lefttaskcount = self.qsize()
        self.counterlock.release()
        return totaltaskcount, lefttaskcount


class WorkerThread(Thread):
    '''
        Thead runing in a thread pool.
        consumer of task_queue
    '''

    def __init__(self, task_queue):
        Thread.__init__(self)
        self.task_queue = task_queue
        self.daemon = True
        self.start()

    def run(self):
        '''
            rely on duck typing method: execute on task in task_queue
        '''
        while True:
            task = self.task_queue.get()
            try:
                task.execute()
            except:
                # ignore all exception in task code, assume task done
                # should be handled correctly by task self
                pass
            self.task_queue.task_done()


class ThreadPool(object):
    '''
        produce task to a Queue, will be consumed by worker thread
    '''

    def __init__(self, task_queue, thread_number=10):
        self.thread_number = thread_number
        self.task_queue = task_queue
        self.task_counter = 0
        self.worker_threads = [WorkerThread(self.task_queue) for _ in xrange(10)]

    def run(self):
        self.task_queue.join()
