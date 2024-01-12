# Performance Report
## Pull Workers Efficiency and Performance
![Pull Workers Graph](https://github.com/mpcs-52040/project-nirman-john/blob/main/graphs/pull_worker.png)

Plotting the number of tasks versus time taken and varying the number of services, we obtained the above graph. From this plot, a few inferences can be drawn as follows:
* Firstly, checking for an increase in both, the number of workers and the number of tasks, the above plot shows the trends in increase/decrease in time taken. This confirms that there is parallelism and concurrency taking place amongst the pull workers with the help of multi-processing module. 
* We find that given a particular number of tasks, in general, the time taken reduces with an increase in number of services.
* For a particular number of services, the time taken increases with an increase in the number of tasks, barring a few exceptions which can be observed in the above plot. 

## Push Workers Efficiency and Performance 
![Push Workers Graph](https://github.com/mpcs-52040/project-nirman-john/blob/main/graphs/push_worker.png)

Plotting the number of tasks versus time taken and varying the number of services, we obtained the above graph. From this plot, a few inferences can be drawn as follows:
* Firstly, checking for an increase in both, the number of workers and the number of tasks, the above plot shows the trends in increase/decrease in time taken. This confirms that there is parallelism and concurrency taking place amongst the pull workers with the help of multi-processing module. 
* We find that given a particular number of tasks, in general, the time taken reduces with an increase in number of services.
* For a particular number of services, the time taken increases with an increase in the number of tasks, barring a few exceptions which can be observed in the above plot. 
* However, a deviation is observed when the number of services is 8 (red line in the plot). We attribute this anomalous behavior to the constraints created by system limitations, based on our observations while running various tests continuously for a long period of time. 

## Local Worker Efficiency and Performance 
![Local Worker Graph](https://github.com/mpcs-52040/project-nirman-john/blob/main/graphs/local_worker.png)

Plotting the number of tasks versus time taken and varying the number of services, we obtained the above graph. From this plot, a few inferences can be drawn as follows:
* In case of the local worker, there seems to be limited improvement as we increase the number of services as observed in the plot. 

## Endpoints versus Time Taken
![Local Worker Graph](https://github.com/mpcs-52040/project-nirman-john/blob/main/graphs/endpoints_time.png)

This plot showcases the time taken by each endpoint in carrying out the specified task for 40 functions. 
* The register function endpoint takes the maximum amount of time. This is because we are setting a value in the Redis database.
* The least time is taken by the status function. We are just fetching the status value of the corresponding task.
* We also observed similar time taken by the status and results functions since both are only fetching from the Redis database, corresponding to the task. This makes sense intutively, as well. When fetching data from Redis, the operation involves retrieving the data based on a given key directly from memory, which is a very fast process.
* The execute function takes more time relatively because we are fetching the function with the corresponding function ID and registering the task of that corresponding function, which is certainly more time consuming than simply fetching as described for the above two functions.
