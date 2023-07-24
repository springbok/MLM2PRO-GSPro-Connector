from multiprocessing import Process
from multiprocessing.managers import BaseManager
from time import sleep
from queue import LifoQueue


def run(lifo):
    """Wait for three messages and print them out"""
    num_msgs = 0
    while num_msgs < 3:
        # get next message or wait until one is available
        s = lifo.get()
        print(s)
        num_msgs += 1


# create manager that knows how to create and manage LifoQueues
class MyManager(BaseManager):
    pass
MyManager.register('LifoQueue', LifoQueue)


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