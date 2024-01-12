## Technical Report
### Introduction
This document outlines the design and development of an asynchronous, distributed, and scalable Microservices for Function as a Service (FaaS) system. The system is architected to efficiently handle remote function executions and deliver results to users using a variety of worker types: local, push, and pull workers, all coordinated by a central task dispatcher.

### Architecture
The architecture comprises three principal components:

* The FastAPI web server that processes incoming function registration and execution requests.
* The task dispatcher that creates tasks based on these requests, assigns unique task IDs, and stores all required parameters for each task. Each task includes a task ID, function ID, function body, status, result, and parameters.
* The workers (local, push, or pull) that receive tasks from the task dispatcher, execute them, and return the results.

The Task Dispatcher listens for tasks from a Redis message queue and dispatches these tasks to different types of workers depending on the system configuration. After the execution of tasks, the status and result of each task are updated in the database using the task ID. To retrieve the results, users can send a GET request to the API at http://localhost:8000/result/{task_id} with the unique task ID. The system will then fetch the serialized result from the database, indicate whether the task execution was successful or not, and return the deserialized result to the client.

### Task Execution Workers
The system employs three types of workers - local workers, pull workers and push workers - to efficiently execute tasks both locally on the machine and in a distributed format. These workers run in separate processes, fetching tasks from the dispatcher, executing them, and then returning the results. To run the push worker, use `python3 push_worker.py <num_threads> <dispatcher_url>` to initialize one push worker with num_threads threads (default is one). The pull worker is run in the same way. To run the corresponding task dispatcher, run `python3 task_dispatcher.py -m [local/pull/push] -w [num_workers]`. The local-workers argument is only used when running the dispatcher in local mode and determines how many threads are available to the local worker. The default mode is local, and the default number of local workers is 1. For example, to run the push worker, open a terminal and run `python3 push_worker.py <num_threads> <dispatcher_url>`. More terminals can be opened to run more push workers. Then, run the task dispatcher in push mode with `python3 task_dispatcher.py -m push`. The dispatcher will then distribute tasks to available push workers as they come in.

#### Local Workers
The local worker is the simplest worker implementation. It runs locally on the host machine and employs a worker pool to execute tasks in parallel. If the task dispatcher is run in local mode, whenever it receives a task, it calls the local worker to execute it. This worker is used as a baseline to compare the performance of the distributed workers.

#### Pull Workers
Pull workers actively request tasks from the dispatcher. They are built using REQ sockets, which follow a strict Request-Reply pattern, meaning that the full send/receive cycle must occur before another message is sent. Upon startup, the pull worker spawns three threads: request_tasks, run_tasks, and send_results, as well as a worker pool for executing tasks in parallel. 

The request_tasks loop sends a request to the dispatcher for a new task. If none is available, it sleeps for a bit and tries again. Otherwise, the task is added to the pull worker's task_queue. The run_tasks thread is responsible for dequeueing tasks and executing them within the process pool. As tasks are completed, the execution results are added to a result_queue, and the send_results thread sends these results back to the dispatcher. This design allows pull workers to control their workload, as they only request tasks when they are ready to process them.

#### Push Workers
On the other hand, push workers passively receive tasks from the dispatcher. They are built using DEALER sockets, which follow an Asynchronous Request-Reply pattern. Upon startup, a push worker also spawns three threads: receive_tasks, run_tasks, and send_results. The latter two operate in the same way as the corresponding functions in the pull worker. The receive_tasks thread is responsible for receiving tasks from the dispatcher and adding them to the push worker's task_queue. This design allows push workers to receive tasks as soon as they are available, without having to request them. 

In this worker architecture, the task dispatcher is responsible for load-balancing tasks as they come in. Whenever a new push_worker is created, it first sends a registration message to register it with the task dispatcher. The task dispatcher keeps track of the registered push workers and evenly dsitributeds work among them. This design allows push workers to be easily scaled up or down depending on the workload.

### Function Execution
Functions are executed by sending a HTTP POST request to the FastAPI web server with the function ID and input arguments. The Task Dispatcher retrieves the function from Redis, creates a task, and submits it to the Redis message queue for asynchronous execution.

### Result Retrieval
The status of a task can be checked by sending a HTTP GET request to the FastAPI web server with the task ID.

### Serialization
The system uses the 'dill' serialization library for the serialization and deserialization of Python functions.

### Running the System
To fully operate the system, you need to run several components: the FastAPI application, the Redis server, the workers, and the task dispatcher. Here are the instructions to run each of them.

#### Redis Server
Redis is used as a message broker for communication between the task dispatcher and the workers by storing registered tasks and functions. To start the Redis server, open a new terminal and run `redis-server` if not already running.

#### FastAPI Application
The FastAPI application can be run using the Uvicorn ASGI server. Open a terminal, navigate to the project directory, and run `uvicorn FAASService:app`. This will start the server on http://localhost:8000.

#### Task Dispatcher and Workers
Please refer to the Task Execution Workers section for instructions on how to run the task dispatcher and each individual worker. Please ensure that all these components are running in separate terminals or background processes as they need to operate concurrently.

### Conclusion
The distributed computing system described in this report provides an efficient and scalable way to execute remote functions asynchronously. The use of Redis as a message queue and the dill library for serialization allows for easy distribution of computation across multiple machines.
