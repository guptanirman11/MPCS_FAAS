import zmq
import multiprocessing
import dill
import codecs
import threading
import sys
from worker import Worker
from Dispatcher_db import Database

#Helper Functions
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

class PushWorker(Worker):
    def __init__(self, num_workers=1, dispatcher_url="tcp://localhost:5555"):
        self.pool = multiprocessing.Pool(num_workers)
        self.db = Database()
        self.task_queue = []
        self.result_queue = []

        # Initialize socket and register worker
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(dispatcher_url)
        self.socket.send_multipart([b'', b'Register'])

        # Start the threads
        threading.Thread(target=self.receive_tasks).start()
        threading.Thread(target=self.run_tasks).start()
        threading.Thread(target=self.send_results).start()

    def update_task_in_database(self, task_id, status, output):
        self.db.setResults(task_id=task_id, status=status, result=output)

    def receive_tasks(self):
        while True:
            try:
                task_data = self.socket.recv_multipart()
                task_id, task = dill.loads(task_data[1])
                self.task_queue.append((task_id, task))
            except Exception as e:
                print(f'Failed to retrieve tasks: {e}')

    def run_tasks(self):
        while True:
            if self.task_queue:
                task_id, task = self.task_queue.pop(0)
                self.run(task, task_id)

    def send_results(self):
        while True:
            if self.result_queue:
                try:
                    result = self.result_queue.pop(0)
                    self.socket.send_multipart([b'', b'Result', dill.dumps(result)])
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
        print("Usage: python3 push_worker.py <num_worker_processors> <dispatcher url>")
        sys.exit(1)
    
    num_workers = int(sys.argv[1])
    dispatcher_url = sys.argv[2]

    worker = PushWorker(num_workers, dispatcher_url)