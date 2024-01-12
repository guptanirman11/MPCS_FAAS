# Testing Report
In this report, we outline the testing process that we followed to ensure the correctness and robustness of our distributed task execution system. The system consists of a FastAPI web server, a task dispatcher, and three types of workers: local, push, and pull. We focused on testing the functionality of the task dispatcher and its ability to interact correctly with each type of worker.

Once we had verified that each part of the task dispatcher was functioning correctly, we employed integration testing to verify that different parts of the system worked together correctly. We tested the dispatcher's ability to interact with the FastAPI server, to receive tasks from the server and to send results back. We also tested the dispatcher's interaction with the Redis database, ensuring that it could correctly retrieve tasks and update their status and results.


## Local Worker Testing

**Initial Integration Testing**: We tested the local worker's ability to execute tasks locally and send results back to the dispatcher. We verified that the worker correctly executed a single task and updated the task's status in the database.

**Concurrency Testing**: We then tested the local worker's ability to handle multiple tasks concurrently. We confirmed that it correctly executed multiple tasks in parallel and updated their status in the database.


## Pull Worker Testing

**Initial Integration Testing**: We began with functional tests to verify that the pull worker could correctly pull tasks from the task dispatcher. We set up a single pull worker and a dispatcher with a single task in its queue. We then verified that the worker could pull the task, execute it, and send the result back to the dispatcher.

**Concurrency Testing**: We then tested the pull worker's ability to handle multiple tasks concurrently. We set up a pull worker with a pool of multiple threads and verified that it could execute multiple tasks in parallel. The pull worker was modified to take take in the number of worker threads as a command line argument.

**Edge Cases**: We also tested the pull worker's ability to adapt to being run before and after the execution of the task dispatcher. Both the task dispatcher and the pull worker were implemented with queues to handle a backlog of tasks. We verified that the pull worker could correctly handle tasks that were added to the queue before it was started, as well as tasks that were added to the queue after it was started.


### Push Worker Testing

We verified the push worker's functionality by setting up a dispatcher that pushes tasks to the worker. We confirmed that the worker correctly received the task, executed it, and sent the result back to the dispatcher. The concurrency testing and error handling were roughly the same as for the pull worker.


### Test Suite

Our test suite consists of a set of functions designed to ensure the robustness and correctness of our system by testing the main features and components.

1. **Function Registration Test**: This test checks if a function can be successfully registered to the FastAPI server. The server should return a status code of 200 and a JSON response containing a unique function_id.

2. **Function Execution Test**: This test validates if a registered function can be correctly executed. The test first registers a simple doubling function, then it makes a request to execute the function with a specific set of parameters. The server should return a status code of 200 and a JSON response containing a unique task_id. The test then checks the status of the task to ensure it's one of the valid statuses: "QUEUED", "RUNNING", "COMPLETED", or "FAILED".

3. **Roundtrip Test**: This comprehensive test checks the full life cycle of a task - from function registration, function execution, checking task status, to fetching the result. It registers a simple doubling function, executes it with a random input, and then checks the task status. If the status is either "COMPLETED" or "FAILED", it fetches the result and asserts that it's the expected output. This test also validates the system's ability to handle multiple tasks concurrently and to correctly update the status and results in the database.

4. **Failure Test**: It is important to handle failures properly. This test validates if the system can correctly handle functions that raise exceptions. It registers a function that raises an exception, then executes it and verifies the task status. The server should return a status code of 200 and a JSON response containing a unique task_id for the execution request. The test then repeatedly checks the status of the task until it changes to "FAILED". If the task status becomes "COMPLETED", it asserts a failure because the task was expected to fail.

5. **Factorial Test**: This test checks if a recursive function (in this case, a factorial function) can be correctly executed and the correct result returned. It registers the factorial function, then executes it with a random integer input and verifies the task status. The server should return a status code of 200 and a JSON response containing a unique task_id for the execution request. The test then repeatedly checks the result of the task until the status changes to either "COMPLETED" or "FAILED". If the task is completed, it asserts that the returned result matches the expected factorial value of the input. This test is also useful for checking the system's ability to handle more complex functions than the simple doubling function.

6. **Array of Test in Client**: The list contains various types of functions such as no-operation functions, functions raising exceptions, functions going to sleep or doing calculations requiring parameters. We checked if the result matches the expected output and also then performed the performance testing with the array of tests instead of just checking with function. Moreover, we added checks for different endpoints to ensure that were returning the correct responses, which can be status, task ID, or function ID. 

These tests help to ensure that our distributed task execution system is working correctly and efficiently, which allowed us to identify and fix any issues or bottlenecks that arose during development.