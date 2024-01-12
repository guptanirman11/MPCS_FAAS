import sys
sys.path.append('.././')
import redis
import dill
from database import update_task_result


class Database:
    def __init__(self, host = 'localhost', port=6379, db=0) :
        self.__redis_client = redis.Redis(host=host, port=port, db=db)

    def __subscribe(self, channel) :
        __pubsub  = self.__redis_client.pubsub()
        __pubsub.subscribe('tasks')
        return __pubsub.listen()
    
    def __get (self, id):
        return dill.loads(self.__redis_client.get(id))
    
    def __set(self,id,data) :
        self.__redis_client.set(id, dill.dumps(data))

    def create_subscription(self, channel) :
        return self.__subscribe(channel)
    
    def get_task(self, task_id) :
        task = self.__get(task_id)
        self.__set(task_id, task)
        return task
    
    def setResults(self, task_id, status, result) :
        task = update_task_result(task_uuid=task_id, status=status, result=result)
        self.__set(task_id,task)