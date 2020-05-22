from forksrv import ForkSrv
from cond_stmt_base import CondStmtBase
from importer import Importer
from strategies.random import RandomStrategy

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
            #TODO filter same conditions out of the loop?
            cur_input = trace.input_content
            for i in range(0,trace.getConditionLength()):
                #TODO make strategy search for more than 1 input, how many?
                for strategy in self.strategies:
                    try_strategy(strategy)
                trace.increaseConditionCounter()
        self.stop()

    def try_strategy(self, trace):
        for j in range(self.NUMBER_OF_TRIES):
            new_input = strategy.search(trace)
            if new_input == None:
                return
            (status, cond_stmt_base) = self.forkSrv.run_with_condition(trace.getCurrentCondition().base, new_input)
            is_flipped = strategy.process_result(status, cond_stmt_base, new_input, trace)
            if is_flipped:
                return #no need to search for more flips

    def process_result(self, status, cond_stmt_base):
        print(status)
        print(cond_stmt_base.__dict__)

    def stop(self):
        self.forkSrv.close()

executor = Executor()
executor.import_data('../traces/mini/')
executor.set_strategies([RandomStrategy()])
executor.run()