from strategies.strategy import Strategy
import random
from trace import Trace
from helpers.utils import Util
import defs
class RandomTaintStrategy(Strategy):
#This class applies random char insertion, random char deletion and random bitflip to the input a random amount between 1 and 10

    reuse_previous = False


    def search(self, trace: Trace):
        #apply random number of random bitflips to bytes in offset
        condition = trace.getCurrentCondition()
        cur_input = trace.getInput()
        offset_len = len(condition.offsets)
        cur_offset = 0
        if offset_len == 0:
            self.handler.logger.wrong(condition, "No offsets")
            return None

        #We know the offset info, randomize first only the bytes in the offset
        while True:
                begin = condition.offsets[cur_offset]['begin']
                end = condition.offsets[cur_offset]['end']

                for i in range(random.randrange(defs.MIN_RANDOM_MUTATIONS, defs.MAX_RANDOM_MUTATIONS)):
                    cur_input = cur_input[:begin] + Util.flip_random_character(cur_input[begin:end]) + cur_input[end:]

                cur_offset =  (cur_offset + 1) % offset_len #there can be multiple offsets, try every one of them
                self.handler.run(condition, cur_input)
                if not self.reuse_previous:
                    cur_input = trace.getInput()
            
        return None
        