import defs
import time
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from exceptions.execution_exeptions import MaximumExecutionTimeException, MaximumRunsException

class Logger:

    result = {}        

    def setStrategy(self, strategy: str):
        self.strategy = strategy
        if self.strategy not in self.result:
            self.result[self.strategy] = {}
        #this is done when a strategy starts executing, start the timer
        self.startTimer()

    def addCondition(self, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        if cond_id not in self.result[self.strategy]:
            self.result[self.strategy][cond_id] = {}
            self.result[self.strategy][cond_id]['input'] = []
            self.result[self.strategy][cond_id]['output'] = []
            self.result[self.strategy][cond_id]['nrOfInputs'] = 0
            self.result[self.strategy][cond_id]['totalTime'] = 0



    def addRun(self, conditionStmt: CondStmt, inputValue:bytes):
        self.stopTimer(conditionStmt) #Always called directly before a run starts
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy][cond_id]['input'].append(inputValue)
        self.result[self.strategy][cond_id]['nrOfInputs'] += 1

    def addResult(self, conditionStmt: CondStmt, status, condition: CondStmtBase):
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy][cond_id]['output'].append((status, condition))
        self.check(conditionStmt)
        self.startTimer() #Always called directly after a run

    def startTimer(self):
        self.result[self.strategy]['startTime'] = time.time()

    def stopTimer(self, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy]['stopTime'] = time.time()
        self.result[self.strategy][cond_id]['totalTime'] += self.result[self.strategy]['stopTime'] - self.result[self.strategy]['startTime']
        self.result[self.strategy]['startTime'] = None
        self.result[self.strategy]['stopTime'] = None
        self.check(conditionStmt)

    def check(self, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        if self.result[self.strategy][cond_id]['totalTime'] >= defs.MAXIMUM_EXECUTION_TIME:
            self.result[self.strategy][cond_id]['status'] = defs.MAXIMUM_EXECUTION_TIME_STRING
            raise MaximumExecutionTimeException('Maximum number of runs obtained')
        if self.result[self.strategy][cond_id]['nrOfInputs'] >= defs.NUMBER_OF_RUNS:
            self.result[self.strategy][cond_id]['status'] = defs.MAXIMUM_INPUT_STRING
            raise MaximumRunsException('Maximum number of runs obtained')

    def isTiming(self):
        return self.result[self.strategy]['startTime'] != None

    def wrong(self, condition, explanation):
        return

    def flipped(self, condition, explanation):
        return

    def done(self, condition: CondStmt):
        if self.isTiming():
            self.stopTimer(condition)
        #TODO write to file here or at stop?
        return

    def stop(self):
        # TODO Write to file
        print(self.result)
