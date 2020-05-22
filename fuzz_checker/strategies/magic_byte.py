from strategies.strategy import Strategy
from trace import Trace
from cond_stmt import CondStmt

class MagicByteStrategy(Strategy):
    
    tried_all_offsets = False
    cur_offset = 0


    def get_offset_length(self, condition: CondStmt):
        offset = condition.offsets[self.cur_offset]
        return offset['end'] - offset['begin']

    def search(self, trace: Trace):
        if self.tried_all_offsets:
            return None
        condition = trace.getCurrentCondition()
        offset_length = self.get_offset_length(condition)
        cur_input = trace.getInput()
        if offset_length > 0 and len(cur_input) >= offset_length:
            for offset in range(condition.offsets[self.cur_offset]['begin'], condition.offsets[self.cur_offset]['end']):
                cur_input = cur_input[0: offset] +  bytes([condition.variables[offset-condition.offsets[self.cur_offset]['begin']]]) + cur_input[offset + 1:] #TODO check if this works
                #TODO use signed something?
                #TODO if equal to magic bytes, check if we should add/sub 1 based on operator 
        self.cur_offset += 1
        if self.cur_offset >= len(condition.offsets):
            self.tried_all_offsets = True
        return cur_input