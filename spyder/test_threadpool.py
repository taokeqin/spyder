import unittest
import threadpool

class TaskMock:
    
    def __init__(self, pool=None):
        self.complete = False
        self.pool = pool

    def execute(self):
        self.complete = True
        subtask = TaskMock(self.pool)       


class ThreadPoolTests(unittest.TestCase):

    def test_empty_pool(self):
        queue = threadpool.TaskQueue()
        tp = threadpool.ThreadPool(queue)
        tp.run()
        total, left = queue.statistics()
        self.assertEqual(total, 0)
        self.assertEqual(left, 0)
    
    def test_add_task(self):
        queue = threadpool.TaskQueue()
        tp = threadpool.ThreadPool(queue)
        queue.put(TaskMock(queue))
        tp.run()
        total, left = queue.statistics()
        self.assertEqual(total, 1)
        self.assertEqual(left, 0)

        
    def test_task_complete(self):
        queue = threadpool.TaskQueue()
        tp = threadpool.ThreadPool(queue)
        task = TaskMock(queue)
        queue.put(task)
        tp.run()
        total, left = queue.statistics()
        self.assertEqual(total, 1)
        self.assertEqual(left, 0)
        self.assertTrue(task.complete)
        