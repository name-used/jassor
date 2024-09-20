import traceback
import time
import sys
from typing import Dict, Union


class TimerManager(object):
    register: Dict[str, Dict[str, float]] = {}

    def __init__(self, container: Union[str, Dict[str, float]] = None):
        self._timers: Dict[str, Timer] = {}
        if isinstance(container, str):
            self._costs: Dict[str, float] = TimerManager.register[container]
        elif container is not None:
            self._costs: Dict[str, float] = container
        else:
            self._costs: Dict[str, float] = {}

    def __getitem__(self, item: str):
        if item not in self._timers:
            self._timers[item] = Timer(item, self._costs)
        if item not in self._costs:
            self._costs[item] = 0.
        return self._timers[item]

    @property
    def costs(self) -> Dict[str, float]:
        return self._costs

    @staticmethod
    def stamp(t: float) -> str:
        r = f'{round(t * 1000 % 1000)}ms'
        t = int(t)
        for n, s in zip(
                [60, 60, 24, 1024],
                ['s', 'm', 'h', 'd'],
        ):
            x = t % n
            t = t // n
            r = f'{x}{s} ' + r
            if t == 0: break
        return r

    @staticmethod
    def regist_container(key: str, container: Dict[str, float]):
        TimerManager.register[key] = container


class Timer(object):
    def __init__(self, key: str, container: Union[str, Dict[str, float]]):
        self._name = key
        self._costs = container

    def __enter__(self):
        if isinstance(self._costs, str):
            self._costs = TimerManager.register[self._costs]
        if self._name not in self._costs:
            self._costs[self._name] = 0.
        self._start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            sys.stderr.write('#%s -------------------------------------- Error Message ---------------------------------------------- \n')
            sys.stderr.write(f'#%s Error: exc_type - {exc_type} \n')
            sys.stderr.write(f'#%s Error: exc_val - {exc_val} \n')
            sys.stderr.write(f'#%s Error: exc_tb - {exc_tb} \n')
            sys.stderr.write('#%s --------------------------------------------------------------------------------------------------- \n')
            sys.stderr.flush()
            traceback.print_exc()
        else:
            self._costs[self._name] += time.time() - self._start
        return False

    def __call__(self, func: callable):
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper
