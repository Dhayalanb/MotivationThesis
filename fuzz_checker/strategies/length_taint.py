from strategies.strategy import Strategy
from trace import Trace
from helpers.utils import Util
import defs

class LengthTaintStrategy(Strategy):
    #some special chars: NULL, LF, CR, SPACE
    
    def search(self, trace: Trace, index:int):
        condition = trace.getCondition(index)
        if condition.base.op != defs.COND_LEN_OP:
            self.handler.wrong(defs.COMMENT_WRONG_STATEMENT)
            return None
        cur_input = trace.getInput()
        size = condition.base.lb2
        delta = condition.base.get_output()
        extended_len = delta * size
        if delta < 0 or extended_len > defs.MAX_INPUT_LENGHT:
            self.handler.wrong(defs.COMMENT_WRONG_LENGTH)
            return None
        
        if len(cur_input) + extended_len < defs.MAX_INPUT_LENGHT:
            # len > X
            input_to_append = b''
            for i in range(extended_len):
                input_to_append = Util.insert_random_character(input_to_append)
            self.handler.run(condition, cur_input+input_to_append)

        if len(cur_input) > extended_len:
            # len < X
            self.handler.run(condition, cur_input[:extended_len])
            self.handler.run(condition, cur_input[:extended_len-1])
        self.handler.wrong(defs.COMMENT_TRIED_EVERYTHING)
        return None

