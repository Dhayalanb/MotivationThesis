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
            variable_offsets = list(range(0, len(condition.variables)))
            if reverse:
                variable_offsets.reverse()
            for offset in range(begin, end):
                if len(cur_input) >= offset:
                    value_to_insert = condition.variables[variable_offsets[offset-begin]]
                    if offset == end - 1:
                        value_to_insert = (value_to_insert + value) %256
                    cur_input = cur_input[0: offset] +  bytes([value_to_insert]) + cur_input[offset + 1:]
        return cur_input

    @staticmethod
    def encode(cur_input, condition, reverse, encoding):
        #reverse to prevent overwriting bytes
        for cur_offset in reversed(range(len(condition.offsets))):#loop over different offsets
            begin = condition.offsets[cur_offset]['begin']
            end = condition.offsets[cur_offset]['end']
            variable_offsets = list(range(0, len(condition.variables)))
            if reverse:
                variable_offsets.reverse()
            encoded_bytes_to_insert = bytes([])
            for offset in range(begin, end):
                if len(cur_input) >= offset:
                    value_to_insert = encoding(condition.variables[variable_offsets[offset-begin]])
                    encoded_bytes_to_insert = encoded_bytes_to_insert + value_to_insert
            cur_input = cur_input[0: begin] +  encoded_bytes_to_insert + cur_input[end + 1:]
        return cur_input

    def zero(cur_input, condition, reverse):
        #reverse to prevent overwriting bytes
        cur_input = MagicByteStrategy.arithmatic(cur_input, condition, reverse, 0)
        for cur_offset in reversed(range(len(condition.offsets))):#loop over different offsets
            begin = condition.offsets[cur_offset]['begin']
            end = condition.offsets[cur_offset]['end']
            if reverse:
                if begin > 0 and len(cur_input) >= begin-1:
                    cur_input = cur_input[:begin-1] + bytes([0]) + cur_input[begin:]
            else:
                if len(cur_input) >= end+1:
                    cur_input = cur_input[:end] + bytes([0]) + cur_input[end+1:]
        return cur_input

    @staticmethod
    def get_modified_output(method, reverse, cur_input, condition):
            if method == "fill_in":
                return MagicByteStrategy.arithmatic(cur_input, condition, reverse, 0)
            if method == "arithmatic_1":
                return MagicByteStrategy.arithmatic(cur_input, condition, reverse, 1)
            if method == "arithmatic_-1":
                return MagicByteStrategy.arithmatic(cur_input, condition, reverse, -1)
            if method == "encoding_ascii":
                return MagicByteStrategy.encode(cur_input, condition, reverse, lambda val: str(val).encode('ascii'))
            if method == "encoding_hex":
                return MagicByteStrategy.encode(cur_input, condition, reverse, lambda val: hex(val)[2:].encode('ascii'))
            if method == "encoding_oct":
                return MagicByteStrategy.encode(cur_input, condition, reverse, lambda val: oct(val)[2:].encode('ascii'))
            if method == "zero":
                return MagicByteStrategy.zero(cur_input, condition, reverse)
            raise Exception("Unknown method")

    @staticmethod
    def get_combinations():
        return product(['fill_in', 'arithmatic_1', 'arithmatic_-1', 'encoding_ascii', 'encoding_hex', 'encoding_oct', 'zero'], [False, True])

    def place_magic_bytes(self, condition, orig):
        combinations = self.get_combinations()
        for modifier in combinations:
            cur_input = self.get_modified_output(modifier[0], modifier[1], orig, condition)
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