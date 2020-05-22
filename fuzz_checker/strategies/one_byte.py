from strategies.strategy import Strategy
from trace import Trace

class OneByteStrategy(Strategy):
    
    tried_byte = 0

    def search(self, trace: Trace):
        if self.tried_byte >= 256:
            return None
        condition = trace.getCurrentCondition()
        if condition.is_one_byte():
            cur_input = trace.getInput()
            byte_offset = condition.offsets[0]['begin']
            cur_input = cur_input[0:byte_offset] + bytes([self.tried_byte]) + cur_input[byte_offset+1:]
            self.tried_byte += 1
            return cur_input
        else:
            return None