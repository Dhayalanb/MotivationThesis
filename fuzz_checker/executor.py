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
from handler import Handler
from exceptions.execution_exeptions import MaximumExecutionTimeException, MaximumRunsException, ConditionFlippedException
import copy
class Executor:

    traces = None
    forkSrv = None
    strategy = None
    NUMBER_OF_TRIES = 50

    def setup_forksvr(self):
        self.forkSrv = ForkSrv()
        self.forkSrv.listen()

    def import_data(self, folder):
        importer = Importer(folder)
        self.traces =  importer.get_file_contents()

    def set_strategies(self, strategies):
        self.strategies = strategies

    def run(self):
        self.setup_forksvr()
        print("Found %d traces" % len(self.traces))
        for trace in self.traces:
            print("New trace with %d conditions" % len(trace.conditions))
            for i in range(0,trace.getConditionLength()):
                print(trace.getCurrentCondition().base.__dict__)
                if trace.getCurrentCondition().isSkipped:
                    continue
                for strategy in self.strategies:
                    #continue
                    print("Trying strategy", strategy.__name__)
                    handler = Handler(self.forkSrv, strategy.__name__)
                    strategy_instance = strategy(handler)
                    try:
                        strategy_instance.search(trace)
                    except MaximumExecutionTimeException:
                        continue
                    except MaximumRunsException:
                        continue
                    except ConditionFlippedException:
                        print("Flipped branch!")
                        continue
                    handler.done()
                trace.increaseConditionCounter()
        self.stop()

    def stop(self):
        self.forkSrv.close()

executor = Executor()
executor.import_data('../traces/mini/')
executor.set_strategies([
    RandomStrategy,
    #RandomTaintStrategy,
    #OneByteStrategy,
    #MagicByteStrategy,
    LengthTaintStrategy,
    #LengthStrategy,
    #GradientDescentStrategy,
    ])
executor.run()