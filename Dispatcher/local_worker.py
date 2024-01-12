from worker import Worker
import multiprocessing
import dill
import codecs
from Dispatcher_db import Database

#Helper Functions
def serialize(obj) -> str:
    return codecs.encode(dill.dumps(obj), "base64").decode()

def deserialize(obj: str):
    return dill.loads(codecs.decode(obj.encode(), "base64"))

def execute_task(func_id, function_payload, params_payload):

     # Deserialize the function and input arguments
    function = deserialize(function_payload['body'])
    params = deserialize(params_payload)
    print(f"Executing function {func_id} with function {function} and parameters {params}")
    try:
        # Execute function
        result = function(*params[0],**params[1])
        status = "success"
    except Exception as e:
        # Handle exceptions
        result = str(e)
        status = "failure"
    
    print(f'OUTPUT:{result}')
    
    # Return task result
    return func_id, status, serialize(result)



class LocalWorker(Worker):
    def __init__(self, num_workers=1):
        print(f'Initializing LocalWorker with {num_workers} workers')
        self.pool = multiprocessing.Pool(num_workers)
        self.db = Database()

    def update_task_in_database(self, task_id, status, output):
        # This function should update the status and output of the task in the database
        self.db.setResults(task_id=task_id, status=status, result=output)

    def run(self, task, task_id):
        func_id, fn_payload, param_payload = task['func_uuid'], task['function'], task['params']
        
        # Define a callback function for the asynchronous task
        def callback(result):
            _, status, result = result
            self.update_task_in_database(task_id, status, result)

        # Execute function with input arguments
        self.pool.apply_async(execute_task,(func_id, fn_payload, param_payload), callback=callback)

    def close(self):
        # Ensure all processes in the pool have completed
        self.pool.close()
        self.pool.join()