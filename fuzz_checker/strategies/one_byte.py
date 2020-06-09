from strategies.strategy import Strategy
from trace import Trace

class OneByteStrategy(Strategy):

    def search(self, trace: Trace):
        condition = trace.getCurrentCondition()
        if condition.is_one_byte():
            for i in range(256):
                cur_input = trace.getInput()
                byte_offset = condition.offsets[0]['begin']
                cur_input = cur_input[0:byte_offset] + bytes([i]) + cur_input[byte_offset+1:]
                self.handler.run(condition, cur_input)
            return None
        else:
            return None