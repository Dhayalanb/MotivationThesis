from strategies.strategy import Strategy
from trace import Trace
from helpers.utils import Util
import random
import defs


class LengthStrategy(Strategy):
    #tries all lengths from 0 to 10000
    length = 0

    def search(self, trace: Trace):
        condition = trace.getCurrentCondition()
        input_to_append = b''
        if self.length >= defs.MAX_LENGHT:
            return None
        for i in range(length):
            input_to_append = Util.insert_random_character(input_to_append)
        self.length += 100 #To speed this strategy up, use steps of 100 bytes, maybe change to 1 byte at a time for more fine grained results
        return input_to_append