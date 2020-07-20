from forksrv import ForkSrv
from cond_stmt_base import CondStmtBase
from importer import Importer
from strategies.random import RandomStrategy
from strategies.gradient_descent import GradientDescentStrategy
from strategies.length import LengthStrategy
from strategies.length_taint import LengthTaintStrategy
from strategies.magic_byte import MagicByteStrategy
from strategies.one_byte import OneByteStrategy
from strategies.random_taint import RandomTaintStrategy
from strategies.concolic import ConcolicStrategy
from handler import Handler
from exceptions.execution_exeptions import MaximumExecutionTimeException, MaximumRunsException, ConditionFlippedException
import copy
import defs
import concurrent.futures
import logging
from threading import Condition
class Executor:

    traces = None

    def import_data(self, folder):
        importer = Importer(folder)
        self.traces =  importer.get_file_contents()

    def set_strategies(self, strategies):
        self.strategies = strategies

    def setupHandlers(self):
        self.handlerLock = Condition()
        self.handlers = [Handler(i) for i in range(defs.NUMBER_OF_THREADS)]

    def getHandler(self):
        self.handlerLock.acquire()
        while not self.handlers:
            self.handlerLock.wait()
        handler = self.handlers.pop()
        self.handlerLock.release()
        return handler

    def returnHandler(self, handler):
        handler.done()
        self.handlerLock.acquire()
        self.handlers.append(handler)
        self.handlerLock.release()

    def destoyHandlers(self):
        for handler in self.handlers:
            handler.stop()

    @staticmethod
    def run_condition(data):
        (self, strategy, trace, index) = data
        handler = self.getHandler()
        logging.info("Trying strategy", strategy.__name__)
        strategy_instance = strategy(handler, trace.getCondition(index))
        try:
            strategy_instance.search(trace, index)
        except MaximumExecutionTimeException:
            logging.info("Maximum run time")
            pass
        except MaximumRunsException:
            logging.info("Maximum runs")
            pass
        except ConditionFlippedException:
            logging.info("Condition flipped!")
            pass
        finally:
            self.returnHandler(handler)

    def run(self):
        self.setupHandlers()
        logging.info("Found %d traces" % len(self.traces))
        for trace in self.traces:
            logging.info("New trace with %d conditions" % len(trace.conditions))
            with concurrent.futures.ThreadPoolExecutor(max_workers = min(defs.NUMBER_OF_THREADS, len(self.strategies))) as thread_executor:
                for i in range(0,trace.getConditionLength()):
                    #logging.info(trace.getCondition(index).base.__dict__)
                    if trace.getCondition(i).isSkipped():
                        trace.increaseConditionCounter()
                        continue
                    results = thread_executor.map(Executor.run_condition, [(self, strategy, trace, i) for strategy in self.strategies])
                    for result in results:
                        result
                    trace.increaseConditionCounter()
        self.destoyHandlers()
        

executor = Executor()
executor.import_data('../traces/mini/')
executor.set_strategies([
    RandomStrategy,
    RandomTaintStrategy,
    OneByteStrategy,
    MagicByteStrategy,
    LengthTaintStrategy,
    #LengthStrategy,
    GradientDescentStrategy,
    ConcolicStrategy
    ])
executor.run()
print("Done!\n")