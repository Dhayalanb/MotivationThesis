from logger import Logger
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from forksrv import ForkSrv
from exceptions.execution_exeptions import ConditionFlippedException
from socket import timeout
import logging

# Class which executes and logs the execution of the fast program
# Is unique per thread
class Handler:

    strategy = None
    id = 0

    def __init__(self, id: int, logger: Logger):
        self.forkSrv = self.setupForkServer(id)
        self.id = id
        self.logger = logger
        self.condition = None

    def setupForkServer(self, id):
        server = ForkSrv()
        server.listen(id)
        return server

    def run(self, condition: CondStmt, inputValue: bytes):
        #print(condition.base.__dict__)
        self.logger.addRun(self.strategy, condition, inputValue)
        #print("trying %s" % inputValue)
        condition.base.lb1 = 2**32-1
        try:
            (status, returnedCondition) =  self.forkSrv.run_with_condition(condition.base, inputValue)
        except timeout:
            #socket connection timed out. Restart fork server and client
            print("Process timed out, rebinding")
            self.forkSrv.rebind()
            (status, returnedCondition) = (bytes([255]), condition.base)
        self.logger.addResult(self.strategy, condition, status, returnedCondition)
        #print(returnedCondition.__dict__)
        logging.debug("STATUS: %d" % int.from_bytes(status, "little"))
        if not returnedCondition.isReached():
            return (status, returnedCondition)
        if returnedCondition.get_condition_output(True) != condition.base.get_condition_output():
            self.logger.flipped(self.strategy, condition, "flipped")
            raise ConditionFlippedException
        return (status, returnedCondition)

    def setStrategy(self, strategy: str):
        self.strategy = strategy
        self.logger.addStrategy(self.strategy)

    def setCondition(self, condition: CondStmt):
        self.condition = condition
        self.logger.addCondition(self.strategy, condition)

    def done(self):
        self.logger.done(self.strategy, self.condition)

    def stop(self):
        self.forkSrv.close()


    def wrong(self, explanation: str):
        self.logger.wrong(self.strategy, self.condition, explanation)

    def comment(self, comment: str):
        self.logger.comment(self.strategy, self.condition.base, comment)


