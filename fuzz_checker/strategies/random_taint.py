from strategies.strategy import Strategy
import random
from trace import Trace
from helpers.utils import Util
class RandomTaintStrategy(Strategy):
#This class applies random char insertion, random char deletion and random bitflip to the input a random amount between 1 and 10
    min_mutations = 1
    max_mutations = 10

    cur_offset = 0

    def search(self, trace: Trace):
        #apply random number of random bitflips to bytes in offset
        condition = trace.getCurrentCondition()
        cur_input = trace.getInput()
        offset_len = len(condition.offsets)

        #We know the offset info, randomize first only the bytes in the offset

        if offset_len > 0:
            begin = condition.offsets[self.cur_offset]['begin']
            end = condition.offsets[self.cur_offset]['end']

            for i in range(random.randrange(self.min_mutations, self.max_mutations)):
                cur_input = cur_input[:begin] + Util.flip_random_character(cur_input[begin:end]) + cur_input[end:]

            self.cur_offset =  (self.cur_offset + 1) % offset_len #there can be multiple offsets, try every one of them
            return cur_input
            
        return None
        