import logging


class ProcessManager:

    def __init__(self, max_processes=5):
        self.max_processes = max_processes
        self.processes = []


    def add(self, process):
        self.__clean()
        if len(self.processes) < self.max_processes:
            self.processes.append(process)
            process.start()
        else:
            logging.debug("Too many processes in the queue, ignoring new processes")

    def __clean(self):
        i = 0
        for process in self.processes:
            if not process.exitcode is None:
                logging.debug("Delete complete process")
                self.processes.pop(i)
                del process
            i = i + 1

    def shutdown(self):
        for process in self.processes:
            process.join()

