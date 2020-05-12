from strategies.strategy import Strategy
class RandomStrategy(Strategy):
    def search(self, trace, index):
        print("Checking position "+str(index))
        return trace.input_content