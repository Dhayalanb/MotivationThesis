from forksrv import ForkSrv
from cond_stmt_base import CondStmtBase
from importer import Importer
from strategies.random import RandomStrategy

class Executor:

    traces = None
    forkSrv = None
    strategy = None

    def setup_forksvr(self):
        self.forkSrv = ForkSrv()
        self.forkSrv.listen()

    def import_data(self, folder):
        importer = Importer(folder)
        self.traces =  importer.get_file_contents()

    def set_strategy(self, strategy):
        self.strategy = strategy

    def run(self):
        self.setup_forksvr()
        for trace in self.traces:
            #TODO filter same conditions out of the loop?
            for i in range(0,len(trace.conditions)):
                new_input = self.strategy.search(trace, i)
                (status, cond_stmt_base) = self.forkSrv.run_with_condition(trace.conditions[i].base, new_input)
                self.process_result(status, cond_stmt_base)

    def process_result(self, status, cond_stmt_base):
        print(status)
        print(cond_stmt_base.__dict__)

    def stop(self):
        self.forkSrv.close()

strategy = RandomStrategy()
executor = Executor()
executor.import_data('../traces/mini/')
executor.set_strategy(strategy)
executor.run()