import zmq
import json
import dill
import redis
import codecs
from multiprocessing import Pool
from local_worker import LocalWorker
from push_worker import PushWorker
from pull_worker import PullWorker
from Dispatcher_db import Database
import argparse
import sys
import os
import threading

# Add the parent directory to the system path
sys.path.append(os.path.dirname(os.getcwd()))

# Helper Functions
def serialize(obj) -> str:
    return codecs.encode(dill.dumps(obj), "base64").decode()

def deserialize(obj: str):
    return dill.loads(codecs.decode(obj.encode(), "base64"))

class TaskDispatcher:
    def __init__(self, mode='local', num_workers=1, port=5555):
        self.db_client = Database()
        self.worker_dict = {
            'local': LocalWorker,
            'push': PushWorker,
            'pull': PullWorker,
        }
        self.mode = mode
        self.context = zmq.Context()
        self.local_worker = LocalWorker(num_workers) if self.mode == 'local' else None
        self.router = self.context.socket(zmq.ROUTER) if self.mode == 'push' else None
        self.rep_socket = self.context.socket(zmq.REP) if self.mode == 'pull' else None
        self.workers = []
        self.task_queue = []
        self.port = port

    def dispatch_task(self):
        while True:
            if self.mode != 'pull':
                if self.task_queue:
                    task, task_id = self.task_queue.pop(0)
                    worker_class = self.worker_dict.get(self.mode)
                    if worker_class is None:
                        raise ValueError(f'Invalid mode: {self.mode}')

                    if self.mode == 'local':
                        # Run the task locally
                        self.local_worker.run(task, task_id)

                    elif self.mode == 'push':
                        # Push the task to workers
                        if self.workers:
                            print(f'Sending task {task_id} to worker {self.workers[0]}')
                            worker_address = self.workers.pop(0)
                            serialized_task = dill.dumps((task_id, task))
                            self.router.send_multipart([worker_address, b'', serialized_task])                       
                            self.workers.append(worker_address)
                        else:
                            print("No available workers.")

            else:
                # Wait for a pull request
                result = self.rep_socket.recv()
                data = dill.loads(result)
                
                if data == 'Request':
                    #print('Request received')
                    if self.task_queue:
                        # Send the task if one is available
                        task, task_id = self.task_queue.pop(0)
                        print(f'Sending task {task_id} to pull worker')
                        serialized_task = dill.dumps({'task':(task_id, task)})
                        self.rep_socket.send(serialized_task)
                    else:
                        # There are no available tasks in the queue
                        response = dill.dumps({'task':None})
                        self.rep_socket.send(response)
                else:
                    # Other message type
                    response = dill.dumps({'task':None})
                    self.rep_socket.send(response)



    def register_workers(self):
        while True:
            try:
                frames = self.router.recv_multipart(zmq.NOBLOCK)
                worker_address = frames[0]
                data = frames[-1]
                #print(f'Received message from worker {worker_address}: {data}')
                if data == b'Register':
                    print(f'Registering worker: {worker_address}')
                    self.workers.append(worker_address)
                else:
                    msg = dill.loads(data)
                    if msg[1] == 'success':
                        print('TASK COMPLETED')
            except zmq.ZMQError:
                pass

    def subscribe_tasks(self):
        task_generator = self.db_client.create_subscription('tasks')
        while True:
            message = next(task_generator)
            if message and message['type'] == 'message':
                print(f'Received task: {message["data"]}')
                task_id = message['data']
                task = self.db_client.get_task(task_id)
                task['status'] = 'RUNNING'
                self.task_queue.append((task, task_id))

    def run_pull(self):
        self.rep_socket.bind("tcp://*:" + str(self.port))
        print(f'Dispatcher listening on port {self.port}...')
        threading.Thread(target=self.subscribe_tasks).start()
        threading.Thread(target=self.dispatch_task).start()

    def run_push(self):
        self.router.bind("tcp://*:" + str(self.port))
        print(f'Dispatcher listening on port {self.port}..."')
        threading.Thread(target=self.subscribe_tasks).start()
        threading.Thread(target=self.register_workers).start()
        threading.Thread(target=self.dispatch_task).start()

    def run_local(self):
        threading.Thread(target=self.subscribe_tasks).start()
        threading.Thread(target=self.dispatch_task).start()

    def run(self):
        if self.mode == 'pull':
            self.run_pull()
        elif self.mode == 'push':
            self.run_push()
        else:
            self.run_local()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', choices=['local', 'push', 'pull'], default='local', help='worker type')
    parser.add_argument('-p', type=int, default=5555, help='port number')
    parser.add_argument('-w', type=int, default=1, help='number of threads for local worker (only for local worker processes)')
    args = parser.parse_args()
    dispatcher = TaskDispatcher(mode=args.m, num_workers=args.w, port=args.p)
    print(f'Using task dispatcher for {args.m} workers')
    print(f'Listening for tasks on port {args.p}...')
    dispatcher.run()
