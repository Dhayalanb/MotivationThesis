from cond_stmt_base import CondStmtBase

class CondStmt:
    def __init__(self):
        self.offsets = self.offsets_opt = self.variables = self.speed = self.is_desirable = self.is_consistent = self.fuzz_times = self.state = self.num_minimal_optima = self.linear= 0
        self.base = CondStmtBase
        self.isSkipped = False


    @staticmethod
    def fromJson(json):
        condStmt = CondStmt()
        condStmt.__dict__.update(json)
        condStmt.base = CondStmtBase.fromJson(json['base'])
        return condStmt

    def is_one_byte(self) -> bool:
        if len(self.offsets) == 1 and self.offsets[0]['end'] - self.offsets[0]['begin'] == 1:
            return True
        return False