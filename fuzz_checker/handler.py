from logger import Logger
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from forksrv import ForkSrv

class Handler:

    def __init__(self, forkSvr: ForkSrv, condition: CondStmt, strategy: str):
        self.forkSrv = forkSrv
        self.condition = condition
        self.logger = Logger(condition, strategy)

    def run(self, inputValue: bytes):
        self.logger.addRun(inputValue)
        (status, returnedCondition) =  self.forkSrv.run_with_condition(condition, inputValue)
        self.logger.addResult(status, returnedCondition)
        return (status, returnedCondition)

    def done(self):
        self.logger.done()


