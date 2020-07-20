import defs
import time
import os, json, base64, logging
from cond_stmt import CondStmt
from cond_stmt_base import CondStmtBase
from exceptions.execution_exeptions import MaximumExecutionTimeException, MaximumRunsException

class Logger:

    result = {}        

    def __init__(self, id):
        self.id = id
        self.condition_counter = 0
        if os.path.isdir('../output/') and len(os.listdir('../output')) != 0:
            raise Exception("Output folder not empty!")

    def setStrategy(self, strategy: str):
        self.strategy = strategy
        if self.strategy not in self.result:
            self.result[self.strategy] = {}

    def addCondition(self, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        self.condition_counter += 1
        if cond_id not in self.result[self.strategy]:
            self.result[self.strategy][cond_id] = {}
            self.result[self.strategy][cond_id]['input'] = []
            self.result[self.strategy][cond_id]['output'] = []
            self.result[self.strategy][cond_id]['nrOfInputs'] = 0
            self.result[self.strategy][cond_id]['totalTime'] = 0
        #this is done when a strategy starts executing, start the timer
        self.startTimer(conditionStmt)



    def addRun(self, conditionStmt: CondStmt, inputValue:bytes):
        self.stopTimer(conditionStmt) #Always called directly before a run starts
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy][cond_id]['input'].append(inputValue)
        self.result[self.strategy][cond_id]['nrOfInputs'] += 1

    def addResult(self, conditionStmt: CondStmt, status, condition: CondStmtBase):
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy][cond_id]['output'].append((status, condition))
        self.check(conditionStmt)
        self.startTimer(conditionStmt) #Always called directly after a run

    def startTimer(self, conditionStmt: CondStmt):
        self.result[self.strategy][conditionStmt.base.getLogId()]['startTime'] = time.time()

    def stopTimer(self, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy][cond_id]['stopTime'] = time.time()
        self.result[self.strategy][cond_id]['totalTime'] += self.result[self.strategy][cond_id]['stopTime'] - self.result[self.strategy][cond_id]['startTime']
        self.result[self.strategy][cond_id]['startTime'] = None
        self.result[self.strategy][cond_id]['stopTime'] = None
        self.check(conditionStmt)

    def check(self, conditionStmt: CondStmt):
        cond_id = conditionStmt.base.getLogId()
        if self.result[self.strategy][cond_id]['totalTime'] >= defs.MAXIMUM_EXECUTION_TIME:
            self.result[self.strategy][cond_id]['status'] = defs.MAXIMUM_EXECUTION_TIME_STRING
            raise MaximumExecutionTimeException('Maximum number of runs obtained')
        if self.result[self.strategy][cond_id]['nrOfInputs'] >= defs.NUMBER_OF_RUNS:
            self.result[self.strategy][cond_id]['status'] = defs.MAXIMUM_INPUT_STRING
            raise MaximumRunsException('Maximum number of runs obtained')

    def isTiming(self, condition: CondStmt):
        return self.result[self.strategy][condition.base.getLogId()]['startTime'] != None

    def wrong(self, conditionStmt: CondStmtBase, explanation: str):
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy][cond_id]['status'] = defs.WRONG_STATUS_STRING
        self.result[self.strategy][cond_id]['comment'] = explanation
        return

    def comment(self, conditionStmt: CondStmtBase, comment: str):
        cond_id = conditionStmt.getLogId()
        self.result[self.strategy][cond_id]['comment'] = comment
        return

    def flipped(self, conditionStmt: CondStmt, explanation):
        cond_id = conditionStmt.base.getLogId()
        self.result[self.strategy][cond_id]['status'] = defs.FLIPPED_STRING
        return

    def done(self, condition: CondStmt):
        if self.isTiming(condition):
            self.stopTimer(condition)
        if (self.condition_counter % 1000) == 0:
            #Every 1000 conditions, write results in case of crash
            self.writeData()
        return

    def writeData(self):
        if not os.path.isdir('../output/'):
            os.mkdir('../output/')
        for strategy_name in self.result:
            if not os.path.isdir('../output/'+strategy_name):
                os.mkdir('../output/'+strategy_name)
            for condition_name in self.result[strategy_name]:
                file_name = '../output/'+strategy_name+'/'+condition_name+".json"
                if os.path.isfile(file_name):
                    continue
                with open(file_name, "w") as output_file:
                    data_to_write = self.result[strategy_name][condition_name]
                    data_to_write['input'] = list(map(lambda i: str(base64.encodebytes(i)), data_to_write['input']))
                    data_to_write['output'] = list(map(lambda i: (str(base64.encodebytes(i[0])),i[1].toJson()), data_to_write['output']))
                    output_file.write(json.dumps(data_to_write))

    def stop(self):
        logging.info(self.result)
        self.writeData()
