from fastapi import FastAPI
from pydantic import BaseModel
from redis import Redis
from database import *
import dill, codecs

app = FastAPI()


@app.post("/register_function/")
async def register_function(func: dict):
    name = func['name']
    body = func['payload']
    function_id = register_function_db(name=name, body=body)
    
    return {'function_id': function_id['function_id']}


@app.get("/func_show/")
async def get_function(func_id):
    #deserialising
    data = dill.loads(codecs.decode(func_id.encode(), "base64"))
    response = get_function_db(uuid_str = data)
    
    return response
    

@app.post("/execute_function/")
async def execute_function(func: dict):
    id = func['function_id']
    params = func['payload']

    response = execute_function_db(function_id = id, function_parameters = params)
    return {'task_id': response['task_id']}

@app.get("/status/{task_id}")
async def get_task_status(task_id):
    task_status = get_task_status_db(task_uuid = task_id)
    return task_status

@app.get("/result/{task_id}")
def get_task_results(task_id):
    
    task_result = get_task_result_db(task_uuid = task_id)
    return task_result

if __name__ == "__main__":
    pass
