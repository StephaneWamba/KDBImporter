from abc import ABC
from time import sleep
from datetime import datetime
from typing import Optional
import random

class Sleeper(ABC):
    time_last_request: datetime = datetime.now()

    def __init__(self, idle_time: float, random_idle_time: bool = False):
        self.idle_time = idle_time
        self.random_idle_time = random_idle_time

    def _sleep(self, time: Optional[int]) -> None:
        now = datetime.now()
        elapsed = (now - self.time_last_request).total_seconds()

        target_idle = (
            random.uniform(1, time or self.idle_time) if self.random_idle_time 
                                            else time or self.idle_time
        )

        idle_remaining = target_idle - elapsed

        if idle_remaining > 0:
            sleep(idle_remaining)

    def time_action(self, time: Optional[int] = None):
        self._sleep(time)
        
        self.time_last_request = datetime.now()

        return self.time_last_request