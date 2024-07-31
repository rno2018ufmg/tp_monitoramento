from time import sleep
import time
from typing import List
from threading import Lock

from tqdm import tqdm

class Logger:
    def __init__(self):
        self.RAMUsage: List[float] = []
        self.DiskUsage: List[float] = []
        self.mutex = Lock()
        self.active = True

    def shutdown(self):
        self.mutex.acquire()
        self.active = False
        self.mutex.release()

    def push_ram(self, value: float):
        self.mutex.acquire()
        self.RAMUsage.insert((len(self.RAMUsage)),value)
        if(len(self.RAMUsage) > 8):
            self.RAMUsage.pop(0)
        self.mutex.release()

    def push_disk(self, value: float):
        self.mutex.acquire()
        self.DiskUsage.insert((len(self.DiskUsage)),value)
        if(len(self.DiskUsage) > 8):
            self.DiskUsage.pop(0)
        self.mutex.release()

    def print_infos(self):
        with tqdm(total=100, desc='disk%', position=1) as diskbar, tqdm(total=100, desc='ram%', position=0) as rambar:
            while self.active:
                start: float = time.time()
                ram_percent: float = 0.0
                for i in self.RAMUsage:
                    ram_percent += i
                if(len(self.RAMUsage) == 0):
                    ram_percent = 0.0
                else:
                    ram_percent = (ram_percent * 100)/len(self.RAMUsage)
                rambar.n=ram_percent
                disk_percent: float = 0.0
                for i in self.DiskUsage:
                    disk_percent += i
                if(len(self.DiskUsage) == 0):
                    disk_percent = 0.0
                else:
                    disk_percent = (disk_percent * 100)/len(self.DiskUsage)
                diskbar.n=disk_percent
                rambar.refresh()
                diskbar.refresh()
                sleep_time = .1 + start
                sleep_time = sleep_time - time.time()
                if(sleep_time > 0.0):
                    time.sleep(sleep_time)
                

