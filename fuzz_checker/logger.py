import defs
import time
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from exceptions.execution_exeptions import MaximumExecutionTimeException, MaximumRunsException

class Logger:

    result = {}

    def __init__(self, strategy: str):
        self.strategy = strategy
        self.result[self.strategy] = {}
        self.result[self.strategy]['input'] = []
        self.result[self.strategy]['output'] = []
        self.result[self.strategy]['nrOfInputs'] = 0
        self.result[self.strategy]['totalTime'] = 0
        self.startTimer()

    def addRun(self, conditionStmt: CondStmt, inputValue:bytes):
        self.stopTimer() #Always called directly before a run starts
        self.result[self.strategy]['input'].append(inputValue)
        self.result[self.strategy]['nrOfInputs'] += 1

    def addResult(self, conditionStmt: CondStmt, status, condition: CondStmtBase):
        self.result[self.strategy]['output'].append((status, condition))
        self.check()
        self.startTimer() #Always called directly after a run

    def startTimer(self):
        self.result[self.strategy]['startTime'] = time.time()

    def stopTimer(self):
        self.result[self.strategy]['stopTime'] = time.time()
        self.result[self.strategy]['totalTime'] += self.result[self.strategy]['stopTime'] - self.result[self.strategy]['startTime']
        self.result[self.strategy]['startTime'] = None
        self.check()

    def check(self):
        if self.result[self.strategy]['totalTime'] >= defs.MAXIMUM_EXECUTION_TIME:
            self.result[self.strategy]['status'] = defs.MAXIMUM_EXECUTION_TIME_STRING
            raise MaximumExecutionTimeException('Maximum number of runs obtained')
        if self.result[self.strategy]['nrOfInputs'] >= defs.NUMBER_OF_RUNS:
            self.result[self.strategy]['status'] = defs.MAXIMUM_INPUT_STRING
            raise MaximumRunsException('Maximum number of runs obtained')

    def isTiming(self):
        return self.result[self.strategy]['startTime'] != None

    def wrong(self, condition, explanation):
        return

    def flipped(self, condition, explanation):
        return

    def done(self):
        if self.isTiming():
            self.stopTimer()
        #TODO write to file
        return
