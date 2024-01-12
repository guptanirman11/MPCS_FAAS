# MPCS Function as a Service (FaaS) Platform
[Worked on the project from March 2023 to May 2023]

### Goal
The aim of my project was to develop an efficient Function-as-a-Service (FaaS) platform, MPCSFaaS, allowing users to run Python functions in a serverless environment. I implemented the platform in Python using FastAPI for the REST API and ZMQ for communication with a pool of worker processes.

### Components
The project comprised two main components: MPCSFaaS service (handling REST API and Redis) and the worker pool. The FastAPI framework facilitated seamless API development, while ZMQ facilitated efficient communication between the service and workers.

### Requirements
- Implemented in Python 3.
- Team project (up to two students).
- No use of existing FaaS libraries.
- Utilized FastAPI, ZMQ, and Redis.
- Complied with the provided test suite.

### Components Description

#### MPCSFaaS Service
- Implemented REST API for registering functions, executing tasks, retrieving task status, and fetching results.
- State stored in a Redis database.
- Leveraged task lifecycle (QUEUED, RUNNING, COMPLETE, FAILURE).

#### Redis
- Used as a distributed key-value store for registered functions.
- Served as a distributed message queue for tasks throughout their lifecycle.

#### Task Dispatcher
- Launched separately to handle task distribution.
- Configured to listen to Redis for new task notifications.
- Implemented three task execution methods: local, pull, and push.

#### Worker Pool
- Implemented pull and push worker types.
- Ran a process pool with a configurable number of processes.
- Utilized ZMQ REQ/REP and DEALER/ROUTER patterns for task communication.

#### Error Handling
- Robust error handling for common failures, returning appropriate errors and error codes.

### Performance Evaluation
- Implemented a performance testing client to assess push and pull implementations.
- Conducted a weak scaling study, evaluating dimensions like latency vs throughput.
- Experimentation focused on different types of tasks, considering "no-op" and "sleep" tasks.

### Conclusion
The project aimed to create an efficient FaaS platform using modern Python technologies. The implementation and performance evaluation provided valuable insights into the effectiveness of push and pull models in handling concurrent tasks.


Please see the reports directory for information about this project. The task dispatcher and workers can be found in the Dispatcher directory. The FastAPI endpoints and Redis database implementations can be found in FAASService.py and database.py, respectively. 