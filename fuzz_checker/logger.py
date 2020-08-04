import defs
import time
import os, json, base64, logging
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from threading import Condition
from exceptions.execution_exeptions import MaximumExecutionTimeException, MaximumRunsException

class Logger:

    result = {}     

    def __init__(self):
        self.condition_counter = 0
        self.lock = Condition()
        self.output_dir = defs.OUTPUT_DIR   
        if os.path.isdir(self.output_dir) and len(os.listdir(self.output_dir)) != 0:
            raise Exception("Output folder %s not empty!" % self.output_dir)

    def addStrategy(self, strategy: str):
        if strategy not in self.result:
            self.result[strategy] = {}

    def addCondition(self, strategy: str, conditionStmt: CondStmt):
        self.lock.acquire()
        cond_id = conditionStmt.base.getLogId()
        self.condition_counter += 1
        if cond_id not in self.result[strategy]:
            self.result[strategy][cond_id] = {}
            self.result[strategy][cond_id]['input'] = []
            self.result[strategy][cond_id]['output'] = []
            self.result[strategy][cond_id]['nrOfInputs'] = 0
            self.result[strategy][cond_id]['totalTime'] = 0
            self.result[strategy][cond_id]['depth'] = conditionStmt.depth
        #this is done when a strategy starts executing, start the timer
        self.startTimer(strategy, conditionStmt)
        self.lock.release()



    def addRun(self, strategy: str, conditionStmt: CondStmt, inputValue:bytes):
        self.lock.acquire()
        self.stopTimer(strategy, conditionStmt) #Always called directly before a run starts
        cond_id = conditionStmt.base.getLogId()
        #self.result[strategy][cond_id]['input'].append(inputValue)
        self.result[strategy][cond_id]['nrOfInputs'] += 1
        self.lock.release()

    def addResult(self, strategy: str, conditionStmt: CondStmt, status, condition: CondStmtBase):
        self.lock.acquire()
        cond_id = conditionStmt.base.getLogId()
        #self.result[strategy][cond_id]['output'].append((status, condition))
        self.check(strategy, conditionStmt)
        self.startTimer(strategy, conditionStmt) #Always called directly after a run
        self.lock.release()

    def startTimer(self, strategy: str, conditionStmt: CondStmt):
        self.result[strategy][conditionStmt.base.getLogId()]['startTime'] = time.time()

    def stopTimer(self, strategy: str, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        self.result[strategy][cond_id]['stopTime'] = time.time()
        self.result[strategy][cond_id]['totalTime'] += self.result[strategy][cond_id]['stopTime'] - self.result[strategy][cond_id]['startTime']
        self.result[strategy][cond_id]['startTime'] = None
        self.result[strategy][cond_id]['stopTime'] = None
        self.check(strategy, conditionStmt)

    def check(self, strategy: str, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        if self.result[strategy][cond_id]['totalTime'] >= defs.MAXIMUM_EXECUTION_TIME:
            self.result[strategy][cond_id]['status'] = defs.MAXIMUM_EXECUTION_TIME_STRING
            self.lock.release()
            raise MaximumExecutionTimeException('Maximum number of runs obtained')
        if self.result[strategy][cond_id]['nrOfInputs'] >= defs.NUMBER_OF_RUNS:
            self.result[strategy][cond_id]['status'] = defs.MAXIMUM_INPUT_STRING
            self.lock.release()
            raise MaximumRunsException('Maximum number of runs obtained')

    def isTiming(self, strategy: str, condition: CondStmt):
        return self.result[strategy][condition.base.getLogId()]['startTime'] != None

    def wrong(self, strategy: str, conditionStmt: CondStmtBase, explanation: str):
        cond_id = conditionStmt.base.getLogId()
        self.lock.acquire()
        self.result[strategy][cond_id]['status'] = defs.WRONG_STATUS_STRING
        self.result[strategy][cond_id]['comment'] = explanation
        self.lock.release()

    def comment(self, strategy: str, conditionStmt: CondStmtBase, comment: str):
        cond_id = conditionStmt.getLogId()
        self.lock.acquire()
        self.result[strategy][cond_id]['comment'] = comment
        self.lock.release()

    def flipped(self, strategy: str, conditionStmt: CondStmt, explanation):
        cond_id = conditionStmt.base.getLogId()
        self.lock.acquire()
        self.result[strategy][cond_id]['status'] = defs.FLIPPED_STRING
        self.lock.release()

    def done(self, strategy: str, condition: CondStmt):
        self.lock.acquire()
        if self.isTiming(strategy, condition):
            self.stopTimer(strategy, condition)
        self.lock.release()

    # Call at the end of every trace, in order to prevent too much data in memory. Conditions in traces are unique, so you should never overwrite a file
    def writeData(self):
        files_written = 0
        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)
        for strategy_name in self.result:
            if not os.path.isdir(self.output_dir+strategy_name):
                os.mkdir(self.output_dir+strategy_name)
            for condition_name in self.result[strategy_name]:
                file_name = self.output_dir+strategy_name+'/'+condition_name+".json"
                if os.path.isfile(file_name):
                    continue
                with open(file_name, "w") as output_file:
                    data_to_write = self.result[strategy_name][condition_name]
                    #data_to_write['input'] = list(map(lambda i: str(base64.encodebytes(i)), data_to_write['input']))
                    #data_to_write['output'] = list(map(lambda i: (str(base64.encodebytes(i[0])),i[1].toJson()), data_to_write['output']))
                    output_file.write(json.dumps(data_to_write))
                    files_written += 1
        logging.info("Wrote %d files" % files_written)
        self.result = {}

    def stop(self):
        logging.info(self.result)
        self.writeData()
