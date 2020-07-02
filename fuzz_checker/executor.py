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
    def run_strategy(data):
        (self, strategy, trace) = data
        handler = self.getHandler()
        print("Trying strategy", strategy.__name__)
        strategy_instance = strategy(handler, trace.getCurrentCondition())
        try:
            strategy_instance.search(trace)
        except MaximumExecutionTimeException:
            self.returnHandler(handler)
            return
        except MaximumRunsException:
            self.returnHandler(handler)
            return
        except ConditionFlippedException:
            print("Flipped branch!")
            self.returnHandler(handler)
            return
        self.returnHandler(handler)

    def run(self):
        self.setupHandlers()
        print("Found %d traces" % len(self.traces))
        for trace in self.traces:
            print("New trace with %d conditions" % len(trace.conditions))
            for i in range(0,trace.getConditionLength()):
                #print(trace.getCurrentCondition().base.__dict__)
                if trace.getCurrentCondition().isSkipped():
                    trace.increaseConditionCounter()
                    continue
                with concurrent.futures.ThreadPoolExecutor(max_workers = min(defs.NUMBER_OF_THREADS, len(self.strategies))) as thread_executor:
                    print("Calling executor")
                    results = thread_executor.map(Executor.run_strategy, [(self, strategy, trace) for strategy in self.strategies])
                    for result in results:
                        print(result)
                trace.increaseConditionCounter()
        self.destoyHandlers()
        

executor = Executor()
executor.import_data('../traces/mini/')
executor.set_strategies([
    #RandomStrategy,
    #RandomTaintStrategy,
    #OneByteStrategy,
    #MagicByteStrategy,
    #LengthTaintStrategy,
    #LengthStrategy,
    #GradientDescentStrategy,
    ConcolicStrategy
    ])
executor.run()