import redis
import uuid
import dill
import codecs

#Helper Functions
def serialize(obj) -> str:
    return codecs.encode(dill.dumps(obj), "base64").decode()

def deserialize(obj: str):
    return dill.loads(codecs.decode(obj.encode(), "base64"))

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def register_function_db(name, body):
    """
    Registers a function and returns a UUID to be used for invocation
    """
    uuid_str = str(uuid.uuid4())
    function_data = {
        'id': uuid_str,
        'name': name,
        'body': body,
        'parameters': None
    }
    #print(f'Registering function {name} with id {uuid_str} with Redis')
    redis_client.set(uuid_str, dill.dumps(function_data))
    return {'function_id': uuid_str}


def execute_function_db(function_id: uuid.UUID, function_parameters: str):
    funct = dill.loads(redis_client.get(function_id))
    print(f'funct: {funct}')
    #print(f'Function {function_id} with parameters {function_parameters} is being executed')
    newtask_uuid = create_task(funct=funct, params=function_parameters)
    return {'task_id': newtask_uuid}


def get_function_db( uuid_str):
    """
    Retrieves a registered function by UUID
    """
    function_data = dill.loads(redis_client.get(uuid_str))
    #print(function_data)
    return function_data['body']

def create_task(funct, params):
    """
    Creates a new task and returns a UUID for the task
    """
    task_uuid = str(uuid.uuid4())
    task_data = {
        'func_uuid': funct["id"],
        "function": funct,
        'params': params,
        'status': 'QUEUED',
        'result': None
    }
    redis_client.set(task_uuid, dill.dumps(task_data))
    redis_client.publish('tasks', task_uuid)
    return task_uuid


def get_task_status_db(task_uuid):
    """
    Retrieves the status of a task by UUID
    """
    task_data = dill.loads(redis_client.get(task_uuid))
    result = {"task_id": task_uuid, "status": task_data["status"]}
    return result


def get_task_result_db(task_uuid):
    """
    Retrieves the result of a task by UUID
    """
    task_data = dill.loads(redis_client.get(task_uuid))
    result = {"status": get_task_status_db(task_uuid=task_uuid)['status'],"result":task_data["result"],"task_id": task_uuid}
    return result


def update_task_result( task_uuid, status, result):
    """
    Updates the result of a task by UUID
    """
    task_data = dill.loads(redis_client.get(task_uuid))
    
    if(status == 'success') :
            task_data['result'] = result
            task_data['status'] = "COMPLETED"
    else :
        task_data['result'] = result
        task_data['status'] = "FAILED"
    return task_data
    


