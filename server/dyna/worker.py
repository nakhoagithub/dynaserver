import threading
import time
from typing import List, Callable
from dyna.environment import workers

class DynaWorker:
    _name = "Worker"
    _description = "Worker run on Dyna Server"
    _running = True
    _time = 1
    _multiple_runable: List[Callable] = []
    _loop = False

    def __init__(self) -> None:
        self._running = True

    def __init_subclass__(cls) -> None:
        workers[cls.__name__] = {
            "active": False,
            "obj": cls()
        }
        cls._name = cls.__name__
    
    def terminate(self):
        self._running = False
    
    def _start(self):
        def _call():
            for runable in self._multiple_runable:
                runable()

        def _run():
            if self._loop:
                while self._running:
                    _call()
                    time.sleep(self._time)
            else:
                _call()

        threading.Thread(target=_run, daemon=True).start()