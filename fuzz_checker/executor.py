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
from logger import Logger
from exceptions.execution_exeptions import MaximumExecutionTimeException, MaximumRunsException, ConditionFlippedException
import defs
import copy
import defs
import concurrent.futures
import logging
import sys, getopt, os
from threading import Condition
class Executor:

    traces = None
    total_traces = 0
    logger = None

    def __init__(self):
        self.logger = Logger()

    def import_data(self, folder):
        importer = Importer(folder)
        self.traces =  importer.get_traces_iterator()
        self.total_traces = importer.get_traces_length()

    def set_strategies(self, strategies):
        self.strategies = strategies

    def setupHandlers(self):
        self.handlerLock = Condition()
        self.handlers = [Handler(i, self.logger) for i in range(defs.NUMBER_OF_THREADS)]

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
        self.handlerLock.notify()
        self.handlerLock.release()

    def destroyHandlers(self):
        for handler in self.handlers:
            handler.stop()
        

    @staticmethod
    def run_condition(data):
        (self, strategy, trace, index) = data
        handler = self.getHandler()
        print("Running condition %d/%d with strategy %s and handler %d" % (index, len(trace.conditions), strategy.__name__, handler.id))
        strategy_instance = strategy(handler, trace.getCondition(index))
        try:
            strategy_instance.search(trace, index)
            handler.done()
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
            print("Done with condition %d/%d with strategy %s and handler %d" % (index, len(trace.conditions), strategy.__name__, handler.id))
            self.returnHandler(handler)

    def run(self):
        self.setupHandlers()
        logging.info("Found %d traces" % self.total_traces)
        number_of_traces = 1
        seen_conditions = set()
        for trace in self.traces:
            logging.info("New trace with %d conditions" % len(trace.conditions))
            with concurrent.futures.ThreadPoolExecutor(max_workers = defs.NUMBER_OF_THREADS) as thread_executor:
                results = []
                for i in range(0,trace.getConditionLength()):
                    if trace.getCondition(i).isSkipped() or trace.getCondition(i).base.getLogId() in seen_conditions:
                        continue
                    results.append(thread_executor.map(Executor.run_condition, [(self, strategy, trace, i) for strategy in self.strategies]))
                    seen_conditions.add(trace.getCondition(i).base.getLogId())
            for result in results:
                for condition in result:
                    condition
            print("Running trace %d/%d" % (number_of_traces, self.total_traces))
            number_of_traces += 1
            self.logger.writeData()
        self.destroyHandlers()
        

def main(argv):
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
    try:
        opts, args = getopt.getopt(argv,"hb:c:j:o:t:",["binary=","concolic=","threads=","output=", "traces="])
    except getopt.GetoptError:
        print('test.py -b <binary> -c <concolic> -j <threads> -o <output> -t <traces>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -b <binary> -c <concolic> -j <threads> -o <output> -t <traces>')
            sys.exit()
        elif opt in ("-b", "--binary"):
            defs.BINARY = arg
        elif opt in ("-c", "--concolic"):
            defs.CONCOLIC_BINARY = arg
        elif opt in ("-j", "--threads"):
            defs.NUMBER_OF_THREADS = int(arg)
        elif opt in ("-o", "--output"):
            defs.OUTPUT_DIR = arg
        elif opt in ("-t", "--traces"):
            defs.TRACES_FOLDER = arg
    print('Binary is ', defs.BINARY)
    print('Concolic binary is ', defs.CONCOLIC_BINARY)
    print('Getting traces from ', defs.TRACES_FOLDER)
    print('Outputting results to ', defs.OUTPUT_DIR)
    print('Running with threads: ', defs.NUMBER_OF_THREADS)
    executor = Executor()
    executor.import_data(defs.TRACES_FOLDER)
    print("Data imported!")
    executor.set_strategies([
        #RandomStrategy,
        #RandomTaintStrategy,
        OneByteStrategy,
        #MagicByteStrategy,
        #LengthTaintStrategy,
        #LengthStrategy,
        #GradientDescentStrategy,
        #ConcolicStrategy
        ])
    print("Starting run")
    executor.run()
    print("Done!\n")

if __name__ == "__main__":
   main(sys.argv[1:])