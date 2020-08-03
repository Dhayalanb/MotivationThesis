from strategies.strategy import Strategy
import random
from trace import Trace
from helpers.utils import Util
import defs
class RandomStrategy(Strategy):
#This class applies random char insertion, random char deletion and random bitflip to the input a random amount between 1 and 10


    def search(self, trace: Trace, index:int):
        #apply random number of random mutations
        condition = trace.getCondition(index)
        cur_input = trace.getInput()
        while True: # Try until timeout
            for i in range(random.randrange(defs.MIN_RANDOM_MUTATIONS, defs.MAX_RANDOM_MUTATIONS)):
                cur_input = Util.mutate(cur_input)
                self.handler.run(condition, cur_input)
                cur_input = trace.getInput()
                    
        self.handler.wrong(defs.COMMENT_TRIED_EVERYTHING)
        return None
        