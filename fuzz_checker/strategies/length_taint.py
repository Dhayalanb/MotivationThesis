from strategies.strategy import Strategy
from trace import Trace
from helpers.utils import Util
import defs

class LengthTaintStrategy(Strategy):

    MAX_LENGHT = 10000
    number_of_runs = 0
    #some special chars: NULL, LF, CR, SPACE
    SPECIAL_CHARS = [0, 10, 13, 32]
    
    def search(self, trace: Trace):
        condition = trace.getCurrentCondition()
        if condition.base.op != defs.COND_LEN_OP or self.number_of_runs >= len(self.SPECIAL_CHARS)+1:
            print("1")
            return None
        cur_input = trace.getInput()
        size = condition.base.lb2
        delta = condition.base.get_output()
        extended_len = delta * size
        if delta < 0 or extended_len > self.MAX_LENGHT:
            print("2")
            return None
        
        if len(cur_input) + extended_len < self.MAX_LENGHT:
            # len > X
            input_to_append = b''
            for i in range(extended_len):
                input_to_append = Util.insert_random_character(input_to_append)
            if self.number_of_runs != 0:
                input_to_append.append(SPECIAL_CHARS[self.number_of_runs-1])
            self.number_of_runs += 1
            return cur_input + input_to_append

        if len(cur_input) > extended_len:
            # len < X
            if self.number_of_runs == 0:
                return cur_input[:extended_len]
            elif self.number_of_runs == 1:
                output = cur_input[:extended_len]
                output.pop()
                return output
        print("3")
        return None

