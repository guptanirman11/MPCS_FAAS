import sys
import dill
import codecs
import requests, logging, time
from serialize import serialize, deserialize

def test_request(function_name, function_body) :
    serialized_data = {'name':function_name,'payload':function_body}
    response = requests.post(f"http://localhost:8000/register_function",json = serialized_data)

    return response.json()

def test_execute(function_id,function_param) :
    
    payload={"function_id": function_id,
                               "payload": function_param}

    response = requests.post(f"http://localhost:8000/execute_function", json=payload)
    # response_data = dill.loads(codecs.decode(response.content.decode()[1:-2].encode(), "base64"))
    return response.json()

def test_status(task_id) :
   

    headers = {'Content-Type': 'application/octet-stream'}

    response = requests.get(f"http://localhost:8000/status/{task_id}", headers=headers)
    return response.json()['status']

def test_results(task_id) :

    response = requests.get(f"http://localhost:8000/result/{task_id}")

    return response

def sleep_function():
    import time
    time.sleep(0.1)
    return "Function executed successfully"

def square(x):
    return x ** 2

def no_op():
    return

def error_func():
    raise ValueError("This function raises a ValueError.")

def double(x):
    return x * 2

if __name__ == "__main__":
    print("welcome")

    def cum_performance_test():
        function_list = [("sleep_function",serialize(sleep_function),serialize(((), {})),"Function executed successfully"),("square",serialize(square),serialize(((5,), {})),25),("no_op",serialize(no_op),serialize(((), {})), None),("double",serialize(double),serialize(((11,), {})),22),
                         ("error_func",serialize(error_func),serialize(((), {})),"This function raises a ValueError."),]
        
        num_workers = 1
        tasks_per_worker = 5
        workers_arr = []
        function_idparam_list = []
        for function in function_list:
            function_id = test_request(function[0], function[1])['function_id']
            function_idparam_list.append((function_id,function[2]))
            print(f'function_id and parameter_list:{function_idparam_list}')
        for i in range(1, num_workers + 1):
                
                tasks_arr = []
                for j in range(i * tasks_per_worker):
                    task_id = test_execute(function_idparam_list[j%5][0], function_idparam_list[j%5][1])['task_id']
                    tasks_arr.append(task_id)
                print(f'task_id_list : {tasks_arr}')

                while True:
                    completed_count = 0
                    failed_count = 0

                    for task_id in tasks_arr:
                        resp = test_results(task_id=task_id)
                        status = resp.json()["status"]

                        if status == "COMPLETED":
                            completed_count += 1
                        elif status == "FAILED":
                            failed_count += 1

                    if completed_count + failed_count == len(tasks_arr):
                        break

                    time.sleep(0.1)

                
                workers_arr.append(i * tasks_per_worker)
                
        
    # cum_performance_test()

    def test_endpoints():
        function_list = [("sleep_function",serialize(sleep_function),serialize(((), {})),"Function executed successfully"),("square",serialize(square),serialize(((5,), {})),25),("no_op",serialize(no_op),serialize(((), {})), None),("double",serialize(double),serialize(((11,), {})),22),
                         ("error_func",serialize(error_func),serialize(((), {})),"This function raises a ValueError."),]
        time_arr = []
        num_workers = 8
        tasks_per_worker = 5
        workers_arr = []
        function_idparam_list = []
        start1 = time.time()
        for i in range(40):
            function_id = test_request(function_list[i%5][0], function_list[i%5][1])['function_id']
            function_idparam_list.append((function_id,function_list[i%5][2]))
        end1 = time.time()

        time_diff = end1 - start1
        print(time_diff)
        return function_idparam_list

    function_idparam_list = test_endpoints()
    def test_execute_endpoint():
        task_id_list = []
        start_time = time.time()
        for i in range(40):
           
                
            
            task_id = test_execute(function_idparam_list[i][0], function_idparam_list[i][1])['task_id']
            task_id_list.append(task_id)

        end_time = time.time()
        time_diff = end_time - start_time
        print(f'execute:{time_diff}')
        return task_id_list
    
    task_id_list = test_execute_endpoint()
    time.sleep(5)
    def test_status_endpoint():
        start_time = time.time()
        while True:
            count = 0

            for task_id in task_id_list:
                resp = test_status(task_id=task_id)
                status = resp

                if status in ["QUEUED", "RUNNING", "COMPLETED", "FAILED"]:
                    count += 1
                
            if count == 40:
                break

            time.sleep(0.1)
        end_time = time.time()
        time_diff = end_time - start_time
        print(f'status_endpoint:{time_diff}')
        return

    def test_result_endpoint():
        start_time = time.time()
        while True:
            completed_count = 0
            failed_count = 0

            for task_id in task_id_list:
                resp = test_results(task_id=task_id)
                status = resp.json()["status"]

                if status == "COMPLETED":
                    completed_count += 1
                elif status == "FAILED":
                    failed_count += 1

            if completed_count + failed_count == 40:
                break

            time.sleep(0.1)
        end_time = time.time()
        time_diff = end_time - start_time
        print(f'result_endpoint:{time_diff}')
        return
    test_status_endpoint()
    test_result_endpoint()

    







