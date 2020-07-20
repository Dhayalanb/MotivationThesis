from strategies.strategy import Strategy
from trace import Trace

class OneByteStrategy(Strategy):

    def search(self, trace: Trace, index:int):
        condition = trace.getCondition(index)
        if condition.is_one_byte():
            for i in range(256):
                cur_input = trace.getInput()
                byte_offset = condition.offsets[0]['begin']
                cur_input = cur_input[0:byte_offset] + bytes([i]) + cur_input[byte_offset+1:]
                self.handler.run(condition, cur_input)
            self.handler.logger.wrong(condition, defs.COMMENT_TRIED_EVERYTHING)
            return None
        else:
            self.handler.logger.wrong(condition, defs.COMMENT_NO_OFFSETS)
            return None