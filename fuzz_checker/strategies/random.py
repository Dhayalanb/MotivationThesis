from strategies.strategy import Strategy
import random
class RandomStrategy(Strategy):
#This class applies random char insertion, random char deletion and random bitflip to the input a random amount between 1 and 10
    min_mutations = 1
    max_mutations = 10

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


    def search(self, trace, index, cur_input):
        print("Checking position "+str(index))
        #apply random number of random mutations
        for i in range(random.randrange(self.min_mutations, self.max_mutations)):
            cur_input = self.mutate(cur_input)
        return cur_input
        