from typing import Union, TextIO
import traceback
import sys
from time import time
from io import TextIOWrapper
from pathlib import Path
from threading import Condition


class IOWrapper:
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

    def __init__(self, start: int = 0, indentation: int = 1, file: Union[TextIO, IOWrapper, TextIOWrapper, str, Path] = sys.stdout, con: Condition = None, level: int = 2):
        self.output_file = file
        self.con = con or Condition()
        self.start = start or time()
        self.indentation = indentation
        self.level = level
        self.block_name = ''
        with self.con:
            if isinstance(self.output_file, (str, Path)):
                self.output_file = open(self.output_file, 'a')

    def close(self):
        with self.con:
            self.output_file.close()

    def track(self, message: str, prefix: str = ''):
        with self.con:
            self.output_file.write('# %s%s %s -> at time %.2f\n' % (prefix, '\t' * self.indentation, message, time() - self.start))
            self.output_file.flush()

    def step(self, message: str):
        if self.level <= Logger.STEP: self.track(message, prefix='STEP')

    def debug(self, message: str):
        if self.level <= Logger.DEBUG: self.track(message, prefix='DEBUG')

    def info(self, message: str):
        if self.level <= Logger.INFO: self.track(message, prefix='INFO')

    def warn(self, message: str):
        if self.level <= Logger.WARNING: self.track(message, prefix='WARN')

    def tab(self):
        with self.con:
            return Logger(start=self.start, indentation=self.indentation+1, file=self.output_file, con=self.con)

    def __getitem__(self, item: str):
        self.block_name = item
        return self

    def __enter__(self):
        self.enter = time()
        with self.con:
            self.track(f'enter {self.block_name} at %.2f seconds' % (time() - self.start), prefix='WITH')
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
            self.track(f'exit {self.block_name} at %.2f seconds -- costing %.2f seconds' % (time() - self.start, time() - self.enter), prefix='EXIT')
        return False
