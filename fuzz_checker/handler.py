from logger import Logger
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from forksrv import ForkSrv
from exceptions.execution_exeptions import ConditionFlippedException

class Handler:

    def __init__(self, forkSrv: ForkSrv, strategy: str):
        self.forkSrv = forkSrv
        self.logger = Logger(strategy)

    def run(self, condition: CondStmt, inputValue: bytes):
        print(condition.base.__dict__)
        self.logger.addRun(condition, inputValue)
        print("trying %s" % inputValue)
        (status, returnedCondition) =  self.forkSrv.run_with_condition(condition.base, inputValue)
        self.logger.addResult(condition, status, returnedCondition)
        print(returnedCondition.__dict__)
        print("STATUS: %d" % int.from_bytes(status, "little"))
        if returnedCondition.condition != condition.base.condition:
            self.logger.flipped()
            raise ConditionFlippedException
        return (status, returnedCondition)

    def done(self):
        self.logger.done()


