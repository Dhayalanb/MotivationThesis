from strategies.strategy import Strategy
import random
from trace import Trace
class RandomStrategy(Strategy):
#This class applies random char insertion, random char deletion and random bitflip to the input a random amount between 1 and 10
    min_mutations = 1
    max_mutations = 10
    mutations_per_byte_in_offset = 16

    cur_offset = 0
    cur_offset_counter = 0
    cur_offset_max_counter = 0
    all_offsets_checked = False


    #From https://www.fuzzingbook.org/html/MutationFuzzer.html
    def mutate(self, s):
        """Return s with a random mutation applied"""
        mutators = [
            self.delete_random_character,
            self.insert_random_character,
            self.flip_random_character
        ]
        mutator = random.choice(mutators)
        # print(mutator)
        return mutator(s)

    def delete_random_character(self, s):
        """Returns s with a random character deleted"""
        if s == "":
            return s

        pos = random.randint(0, len(s) - 1)
        # print("Deleting", repr(s[pos]), "at", pos)
        return s[:pos] + s[pos + 1:]


    def insert_random_character(self, s):
        """Returns s with a random character inserted"""
        pos = random.randint(0, len(s))
        random_character = random.randrange(0, 127)
        # print("Inserting", repr(random_character), "at", pos)
        return s[:pos] + bytes([random_character]) + s[pos:]

    def flip_random_character(self, s):
        """Returns s with a random bit flipped in a random position"""
        if s == "":
            return s

        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        bit = 1 << random.randint(0, 6)
        new_c = bytes([c ^ bit])
        # print("Flipping", bit, "in", repr(c) + ", giving", repr(new_c))
        return s[:pos] + new_c + s[pos + 1:]


    def search(self, trace: Trace):
        #TODO split this in 2 strategies?
        #apply random number of random mutations
        condition = trace.getCurrentCondition()

        cur_input = trace.getInput()

        #We know the offset info, randomize first only the bytes in the offset

        if not self.all_offsets_checked and len(condition.offsets) > 0:
            begin = condition.offsets[self.cur_offset]['begin']
            end = condition.offsets[self.cur_offset]['end']
            if self.cur_offset_max_counter == 0:
                self.cur_offset_max_counter = (end-begin)*self.mutations_per_byte_in_offset
            for i in range(random.randrange(self.min_mutations, self.max_mutations)):
                cur_input = cur_input[:begin] + self.mutate(cur_input[begin:end]) + cur_input[end:]
            self.cur_offset_counter += 1
            #If we tried that a number of times, randomize entire input
            if self.cur_offset_counter == self.cur_offset_max_counter:
                self.cur_offset_counter = 0
                self.cur_offset_max_counter = 0
                self.cur_offset += 1
                if self.cur_offset >= len(condition.offsets):
                    self.all_offsets_checked = True
            return cur_input
            
        #no more offset specific stuff to fuzz, fuzz entire input
        for i in range(random.randrange(self.min_mutations, self.max_mutations)):
            cur_input = self.mutate(cur_input)
        return cur_input
        