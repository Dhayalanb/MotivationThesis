from trace import Trace
from cond_stmt_base import CondStmtBase

class Strategy:
    def search(self, trace: Trace):
        pass

    def is_flipped(self, trace: Trace, cond_stmt_base: CondStmtBase) -> bool:
        return trace.getCurrentCondition().condition != cond_stmt_base.condition

    def process_result(self, status: bytes, cond_stmt_base: CondStmtBase, cur_input: bytes, trace: Trace) -> bool:
        return self.is_flipped(trace, cond_stmt_base)