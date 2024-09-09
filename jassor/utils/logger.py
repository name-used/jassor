from typing import Union, TextIO
import traceback
import sys
from time import time
from io import TextIOWrapper
from pathlib import Path
from threading import Condition


class _IOWrapper:  # type: ignore
    def __init__(self, write_func: callable, flush_func: callable, close_func: callable):
        self.write = write_func or self.nothing
        self.flush = flush_func or self.nothing
        self.close = close_func or self.nothing

    @staticmethod
    def nothing(*args, **kwargs):
        pass


class Logger(object):
    STEP = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3

    def __init__(self, start: int = 0, indentation: int = 1, file: Union[TextIO, _IOWrapper, TextIOWrapper, str, Path] = sys.stdout, con: Condition = None, level: int = 2):
        self._output_file = file
        self._con = con or Condition()
        self._start = start or time()
        self._indentation = indentation
        self._level = level
        self._block_name = ''
        with self._con:
            if isinstance(self._output_file, (str, Path)):
                self._output_file = open(self._output_file, 'a')

    def close(self):
        with self._con:
            self._output_file.close()

    def track(self, message: str, prefix: str = ''):
        with self._con:
            self._output_file.write('# %s%s %s -> at time %.2f\n' % (prefix, '\t' * self._indentation, message, time() - self._start))
            self._output_file.flush()

    def step(self, message: str):
        if self._level <= Logger.STEP: self.track(message, prefix='STEP')

    def debug(self, message: str):
        if self._level <= Logger.DEBUG: self.track(message, prefix='DEBUG')

    def info(self, message: str):
        if self._level <= Logger.INFO: self.track(message, prefix='INFO')

    def warn(self, message: str):
        if self._level <= Logger.WARNING: self.track(message, prefix='WARN')

    def tab(self):
        with self._con:
            return Logger(start=self._start, indentation=self._indentation+1, file=self._output_file, con=self._con)

    def __getitem__(self, item: str):
        self._block_name = item
        return self

    def __enter__(self):
        self._enter = time()
        with self._con:
            self.track(f'enter {self._block_name} at %.2f seconds' % (time() - self._start), prefix='WITH')
        return self.tab()

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
            self.track(f'exit {self._block_name} at %.2f seconds -- costing %.2f seconds' % (time() - self._start, time() - self._enter), prefix='EXIT')
        return False
