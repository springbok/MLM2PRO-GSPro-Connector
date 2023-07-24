import logging
import sys
import time
from multiprocessing import Process


class ShotProcessingProcess(Process):

    def __init__(self, queue, settings, apps_paths):
        Process.__init__(self)
        logging.debug('Start shot processing')
        self.app_paths = apps_paths
        self.settings = settings
        self.queue = queue

    def run(self):
        logging.debug('Start process to check for a new shot and process it')
        time.sleep(2)
        exit(0)
