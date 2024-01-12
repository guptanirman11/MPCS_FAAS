import zmq
import multiprocessing as mp
import dill
import codecs
import threading
import sys
import time
from worker import Worker
from Dispatcher_db import Database

# Helper Functions
def serialize(obj) -> str:
    return codecs.encode(dill.dumps(obj), "base64").decode()

def deserialize(obj: str):
    return dill.loads(codecs.decode(obj.encode(), "base64"))

def execute_task(func_id, function_payload, params_payload):
    fn = deserialize(function_payload['body'])
    params = deserialize(params_payload)

    print(f'Executing function {func_id} with function {fn} and parameters {params}')
    try:
        output = fn(*params[0], **params[1])
        status = "success"
    except Exception as e:
        output = str(e)
        status = "failure"

    print(f'OUTPUT: {output}')

    # Return task result
    return func_id, status, serialize(output)

class PullWorker(Worker):
    def __init__(self, num_workers=1, dispatcher_url="tcp://localhost:5555"):
        self.pool = mp.Pool(num_workers)
        self.db = Database()
        self.task_queue = []
        self.result_queue = []

        # Initialize socket
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(dispatcher_url)
        self.socket_lock = threading.Lock()

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        # Start the threads
        threading.Thread(target=self.request_tasks).start()
        threading.Thread(target=self.run_tasks).start()
        threading.Thread(target=self.send_results).start()

    def update_task_in_database(self, task_id, status, output):
        self.db.setResults(task_id=task_id, status=status, result=output)

    def request_tasks(self):
        while True:
            #print('Requesting tasks')
            with self.socket_lock:
                try:
                    # Request a task
                    self.socket.send(dill.dumps('Request'))
                    socks = dict(self.poller.poll(timeout=1000))
                    if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                        response = dill.loads(self.socket.recv())
                        if ('task'in response and response['task']!=None):
                                self.task_queue.append(response['task'])
                except Exception as e:
                    print(f'Failed to request tasks: {e}')
                    print('Please make sure the dispatcher is running, then restart the worker.')
                    time.sleep(1)

    def run_tasks(self):
        while True:
            if self.task_queue:
                task_id, task = self.task_queue.pop(0)
                self.run(task, task_id)

    def send_results(self):
        while True:
            if self.result_queue:
                #print('RESULT FOUND, SENDING')
                result = self.result_queue.pop(0)
                data = dill.dumps(result)
                with self.socket_lock:
                    try:
                        self.socket.send(data)
                        socks = dict(self.poller.poll(timeout=1000))
                        if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                            self.socket.recv()
                        else:
                            self.result_queue.append(result)
                    except Exception as e:
                        print(f'Failed to send results: {e}')

    def run(self, task, task_id):
        func_id, fn_payload, param_payload = task['func_uuid'], task['function'], task['params']

        # Execute function with input arguments
        _ ,status, result = self.pool.apply_async(execute_task,(func_id, fn_payload, param_payload)).get()

        # Update the task status and output in the database
        self.update_task_in_database(task_id, status, result)
        self.result_queue.append((task_id, status, serialize(result)))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 pull_worker.py <num_worker_processors> <dispatcher url>")
        sys.exit(1)
    
    num_workers = int(sys.argv[1])
    dispatcher_url = sys.argv[2]

    worker = PullWorker(num_workers, dispatcher_url)
