from multiprocessing import Process
from multiprocessing.managers import BaseManager
from time import sleep
from queue import LifoQueue


# create manager that knows how to create and manage LifoQueues
class MultiprocessLifoQueueManager(BaseManager):
    pass

MultiprocessLifoQueueManager.register('LifoQueue', LifoQueue)



if __name__ == "__main__":

    manager = MyManager()
    manager.start()
    lifo = manager.LifoQueue()
    lifo.put("first")
    lifo.put("second")

    # expected order is "second", "first", "third"
    p = Process(target=run, args=[lifo])
    p.start()

    # wait for lifoqueue to be emptied
    sleep(0.25)
    lifo.put("third")

    p.join()