from abc import ABC, abstractmethod

class Worker(ABC):
    @abstractmethod
    def run(self, task, task_id):
        pass