from forksrv import ForkSrv
from cond_stmt_base import CondStmtBase
from importer import Importer
from strategies.random import RandomStrategy
from handler import Handler
from exceptions.execution_exeptions import MaximumExecptionTimeException, MaximumRunsException
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
        for trace in self.traces:
            for i in range(0,trace.getConditionLength()):
                if trace.getCurrentCondition().isSkipped:
                    continue
                for strategy in self.strategies:
                    handler = Handler(self.forkSrv, trace.getCurrentCondition(), strategy.__name__)
                    strategy_instance = strategy()
                    try:
                        strategy_instance.search(trace)
                    except MaximumExecptionTimeException:
                        continue
                    except MaximumRunsException:
                        continue
                    handler.done()
                trace.increaseConditionCounter()
        self.stop()

    def stop(self):
        self.forkSrv.close()

executor = Executor()
executor.import_data('../traces/mini/')
executor.set_strategies([RandomStrategy.__class__])
executor.run()