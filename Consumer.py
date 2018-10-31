import multiprocessing
import time
import requests
import datetime

class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue, daemon=True):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.daemon = daemon
    
    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            # --- criteria to end process ---
            if next_task is None:
                print(f'{proc_name}: received a poison pill - Terminating...')
                self.task_queue.task_done()
                break
            # --- do work ---    
            task_result = next_task()
            self.task_queue.task_done()
            self.result_queue.put(task_result)

class Task:

    def __init__(self):
        pass

    def __call__(self):
        ''' Work '''

        task_result = None # do work here

        return task_result

    def __str__(self):
        ''' tostring '''
        return f'task string representation'