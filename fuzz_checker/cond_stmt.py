from cond_stmt_base import CondStmtBase

class CondStmt:
    def __init__(self):
        self.offsets = self.offsets_opt = self.variables = self.speed = self.is_desirable = self.is_consistent = self.fuzz_times = self.state = self.num_minimal_optima = self.linear= 0
        self.base = CondStmtBase


    @staticmethod
    def fromJson(json):
        condStmt = CondStmt()
        condStmt.__dict__.update(json)
        condStmt.base = CondStmtBase.fromJson(json['base'])
        return condStmt