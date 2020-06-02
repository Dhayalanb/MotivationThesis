from strategies.strategy import Strategy
from trace import Trace
from cond_stmt import CondStmt
import random

class MagicByteStrategy(Strategy):

    has_run = False

    def search(self, trace: Trace):
        #TODO make all combinations with offsets
        if self.has_run:
            return None
        condition = trace.getCurrentCondition()
        offset_length = len(condition.offsets)
        cur_input = trace.getInput()
        for cur_offset in range(offset_length):
            if offset_length > 0 and len(cur_input) >= offset_length:
                for offset in range(condition.offsets[cur_offset]['begin'], condition.offsets[cur_offset]['end']):
                    cur_input = cur_input[0: offset] +  bytes([condition.variables[offset-condition.offsets[cur_offset]['begin']]]) + cur_input[offset + 1:]
                if cur_input[offset:offset+offset_length] == trace.getInput()[offset:offset+offset_length]:
                    #magic bytes are already in place!
                    #change magic bytes by adding +1!
                    for offset in range(condition.offsets[cur_offset]['begin'], condition.offsets[cur_offset]['end']):
                        cur_input = cur_input[0: offset] +  bytes([(condition.variables[offset-condition.offsets[cur_offset]['begin']]+1) % 256]) + cur_input[offset + 1:]
        self.has_run = True
        return cur_input