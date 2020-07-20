from cond_stmt import CondStmt

class Trace:
    def __init__(self, input_content, conditions):
        self.input_content = input_content
        self.conditions = conditions
        self.index = 0

    def getConditionLength(self):
        return len(self.conditions)

    def getInput(self):
        return self.input_content

    def increaseConditionCounter(self):
        self.index += 1
    
    def getCurrentCondition(self) -> CondStmt:
        return self.conditions[self.index]

    def getCondition(self, index: int) -> CondStmt:
        return self.conditions[index]