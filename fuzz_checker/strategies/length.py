from strategies.strategy import Strategy
from trace import Trace
from helpers.utils import Util
import random
import defs


class LengthStrategy(Strategy):
    #tries all lengths from 0 to 10000

    def search(self, trace: Trace, index:int):
        condition = trace.getCondition(index)
        length = 0
        while length < defs.MAX_INPUT_LENGHT:
            input_to_append = b''
            for i in range(length):
                input_to_append = Util.insert_random_character(input_to_append)
            self.handler.run(condition, input_to_append)
            length += defs.STEP_SIZE_LENGTH #To speed this strategy up, use steps of 100 bytes, maybe change to 1 byte at a time for more fine grained results
        self.handler.wrong(defs.COMMENT_TRIED_EVERYTHING)
        return None