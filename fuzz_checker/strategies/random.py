from strategies.strategy import Strategy
import random
from trace import Trace
from helpers.utils import Util
class RandomStrategy(Strategy):
#This class applies random char insertion, random char deletion and random bitflip to the input a random amount between 1 and 10
    min_mutations = 1
    max_mutations = 10


    def search(self, trace: Trace):
        #apply random number of random mutations
        condition = trace.getCurrentCondition()
        cur_input = trace.getInput()

        for i in range(random.randrange(self.min_mutations, self.max_mutations)):
            cur_input = Util.mutate(cur_input)
        return cur_input
        