from strategies.concolic import ConcolicStrategy
from strategies.gradient_descent import GradientDescentStrategy
from strategies.length import LengthStrategy
from strategies.length_taint import LengthTaintStrategy
from strategies.magic_byte import MagicByteStrategy
from strategies.one_byte import OneByteStrategy
from strategies.random import RandomStrategy
from strategies.random_taint import RandomTaintStrategy
from trace import Trace
from importer import Importer

class TestDoneException(Exception):
    pass

class TestHandler:
    valuesToCheck = []
    runCount = 0

    def __init__(self, values):
        self.valuesToCheck = values

    def run(self, condition, inputValue):
        print(inputValue)
        if self.runCount >= len(self.valuesToCheck):
            raise TestDoneException
        valueToCompare = self.valuesToCheck[self.runCount]['value']
        compareType = self.valuesToCheck[self.runCount]['compare']
        if 'index' in self.valuesToCheck[self.runCount]:
            inputValue = inputValue[self.valuesToCheck[self.runCount]['index']]

        if compareType == 'equal':
            assert(valueToCompare == inputValue)
        elif compareType == 'lenLess':
            assert(valueToCompare < len(inputValue))
        elif compareType == 'lenEqual':
            assert(valueToCompare == len(inputValue))
        else: 
            assert(valueToCompare != inputValue)
        self.runCount += 1
        return (1, condition)

class Test:

    subfolder = 'strategy_test/'

    def check_one_byte(self, trace: Trace):
        print("Testing one byte strategy")
        testHandler = TestHandler([{'value':i, 'compare': 'equal', 'index': 3} for i in range(256)])
        one_byte = OneByteStrategy(testHandler)
        output = one_byte.search(trace)
        assert(output == None)

    def check_random_taint(self, trace: Trace):
        print("Testing random taint strategy")
        testHandler = TestHandler([{'value':trace.getInput()[3], 'compare': 'notEqual', 'index': 3}])
        random = RandomTaintStrategy(testHandler)
        output = random.search(trace)
        assert(output == None)
        trace.increaseConditionCounter()
        try:
            output = random.search(trace)
        except TestDoneException:
            pass

    def check_random(self, trace: Trace):
        print("Testing random strategy")
        testHandler = TestHandler([{'value':trace.getInput(), 'compare': 'notEqual'}])
        random = RandomStrategy(testHandler)
        try:
            output = random.search(trace)
        except TestDoneException:
            pass

    def check_magic_1(self, trace: Trace):
        print("Testing magic byte strategy")
        testHandler = TestHandler([{'value':b'test\xde\xad\xbe\xef', 'compare': 'equal'}])
        mb = MagicByteStrategy(testHandler)
        output = mb.search(trace)
        assert(output == None)

    def check_magic_2(self, trace: Trace):
        print("Testing magic byte strategy 2")
        testHandler = TestHandler([{'value':b'test\xde\xad\xbe\xef', 'compare': 'notEqual'}])
        mb = MagicByteStrategy(testHandler)
        output = mb.search(trace)
        assert(output == None)

    def check_length_1(self, trace: Trace):
        print("Testing length taint strategy")
        testHandler = TestHandler([{'value':len(trace.getInput()), 'compare': 'lenLess'}])
        length = LengthTaintStrategy(testHandler)
        try:
            output = length.search(trace)
        except TestDoneException:
            pass

    def check_length_2(self, trace: Trace):
        print("Testing length strategy")
        testHandler = TestHandler([{'value':0, 'compare': 'lenEqual'}, {'value':100, 'compare': 'lenEqual'}, {'value':200, 'compare': 'lenEqual'}])
        length = LengthStrategy(testHandler)
        try:
            output = length.search(trace)
        except TestDoneException:
            pass

    def run_all(self):
        for strategy_to_test in ['length_1', 'length_2', 'magic_1', 'magic_2', 'one_byte', 'random_taint', 'random']:
            importer = Importer(self.subfolder + strategy_to_test +'/')
            trace = importer.get_file_contents()[0]
            function_to_run = getattr(self, 'check_'+strategy_to_test)
            function_to_run(trace)