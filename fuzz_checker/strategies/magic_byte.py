from strategies.strategy import Strategy
from trace import Trace
from cond_stmt import CondStmt
import random

class MagicByteStrategy(Strategy):

    def place_magic_bytes(self, condition, cur_input, add_one):
        #TODO make all combinations with offsets?
        offset_length = len(condition.offsets)
        for cur_offset in range(offset_length):#loop over different offsets
            begin = condition.offsets[cur_offset]['begin']
            end = condition.offsets[cur_offset]['end']
            for offset in range(begin, end):
                if len(cur_input) >= offset:
                    if add_one:
                        cur_input = cur_input[0: offset] +  bytes([(condition.variables[offset-begin]+1) % 256]) + cur_input[offset + 1:]
                    else:
                        cur_input = cur_input[0: offset] +  bytes([condition.variables[offset-begin]]) + cur_input[offset + 1:]
        return cur_input

    def search(self, trace: Trace):
        cur_input = trace.getInput()
        condition = trace.getCurrentCondition()
        new_input = self.place_magic_bytes(condition, cur_input, False)
        if cur_input == new_input:
            new_input = self.place_magic_bytes(condition, cur_input, True)
        self.handler.run(condition, new_input)
        return None