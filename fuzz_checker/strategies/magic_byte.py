from strategies.strategy import Strategy
from trace import Trace
from cond_stmt import CondStmt
import random
import logging
from itertools import product
import defs

class MagicByteStrategy(Strategy):

    @staticmethod
    def arithmatic(cur_input, condition, reverse, value):
        for cur_offset in range(len(condition.offsets)):#loop over different offsets
            begin = condition.offsets[cur_offset]['begin']
            end = condition.offsets[cur_offset]['end']
            start = begin if not reverse else end - 1
            for offset in range(begin, end):
                if len(cur_input) >= offset:
                    value_to_insert = condition.variables[start-begin]
                    if offset == end - 1:
                        value_to_insert = (value_to_insert + value) %256
                    cur_input = cur_input[0: offset] +  bytes([value_to_insert]) + cur_input[offset + 1:]
        return cur_input

    @staticmethod
    def fill_in(cur_input, condition, reverse):
        for cur_offset in range(len(condition.offsets)):#loop over different offsets
            begin = condition.offsets[cur_offset]['begin']
            end = condition.offsets[cur_offset]['end']
            start = begin if not reverse else end - 1
            for offset in range(begin, end):
                if len(cur_input) >= offset:
                    cur_input = cur_input[0: offset] +  bytes([condition.variables[start-begin]]) + cur_input[offset + 1:]
        return cur_input

    def place_magic_bytes(self, condition, cur_input):
        orig = cur_input
        for modifier in product(['fill_in', 'arithmatic_1', 'arithmatic_-1'], [False, True]):
            cur_input = orig
            if modifier[0] == "fill_in":
                cur_input = self.fill_in(cur_input, condition, modifier[1])
            if modifier[0] == "arithmatic_1":
                cur_input = self.arithmatic(cur_input, condition, modifier[1], 1)
            if modifier[0] == "arithmatic_-1":
                cur_input = self.arithmatic(cur_input, condition, modifier[1], -1)
            self.handler.logger.comment(condition.base, modifier[1])
            self.handler.run(condition, cur_input)

    def search(self, trace: Trace, index:int):
        cur_input = trace.getInput()
        condition = trace.getCondition(index)
        offset_length = len(condition.offsets)
        if offset_length == 0:
            self.handler.logger.wrong(condition, defs.COMMENT_NO_OFFSETS)
            return None
        self.place_magic_bytes(condition, cur_input)
        self.handler.logger.wrong(condition, defs.COMMENT_TRIED_EVERYTHING)
        return None