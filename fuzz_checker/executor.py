from forksrv import ForkSrv
from shm_conds import CondStmtBase

class Executor:

    def run(self):
        forkSrv = ForkSrv(self)
        forkSrv.listen()

    def getCondStmts(self):
        return self.condStmts

    def importData(self):
        condStmtBase = CondStmtBase()
        condStmtBase.cmpid = 3997935313
        condStmtBase.context = 0
        condStmtBase.order = 1
        self.condStmts = [condStmtBase]

    def setStrategy(self, strategy):
        self.strategy = strategy

    def processResult(self, condStmtBase):
        return
executor = Executor()
executor.importData()
executor.setStrategy(strategy)
executor.run()