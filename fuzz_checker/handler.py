from logger import Logger
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from forksrv import ForkSrv
from exceptions.execution_exeptions import ConditionFlippedException

# Class which executes and logs the execution of the fast program
# Is unique per thread
class Handler:

    def __init__(self, id: int):
        self.forkSrv = self.setupForkServer(id)
        self.logger = Logger()
        self.condition = None

    def setupForkServer(self, id):
        server = ForkSrv()
        server.listen(id)
        return server

    def run(self, condition: CondStmt, inputValue: bytes):
        #print(condition.base.__dict__)
        self.logger.addRun(condition, inputValue)
        #print("trying %s" % inputValue)
        condition.base.lb1 = 2**32-1
        (status, returnedCondition) =  self.forkSrv.run_with_condition(condition.base, inputValue)
        self.logger.addResult(condition, status, returnedCondition)
        #print(returnedCondition.__dict__)
        #print("STATUS: %d" % int.from_bytes(status, "little"))
        if not returnedCondition.isReached():
            return (status, returnedCondition)
        if returnedCondition.get_condition_output(True) != condition.base.get_condition_output():
            self.logger.flipped(condition, "flipped")
            raise ConditionFlippedException
        return (status, returnedCondition)

    def setStrategy(self, strategy: str):
        self.logger.setStrategy(strategy)

    def setCondition(self, condition: CondStmt):
        self.condition = condition
        self.logger.addCondition(condition)

    def done(self):
        self.logger.done(self.condition)
        self.condition = None

    def stop(self):
        self.logger.stop()
        self.forkSrv.close()


