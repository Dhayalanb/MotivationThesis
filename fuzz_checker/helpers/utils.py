import random
import defs


class Util:

    # From https://www.fuzzingbook.org/html/MutationFuzzer.html
    @staticmethod
    def mutate(s):
        """Return s with a random mutation applied"""
        mutators = [
            Util.delete_random_character,
            Util.insert_random_character,
            Util.flip_random_character
        ]
        mutator = random.choice(mutators)
        # print(mutator)
        return mutator(s)

    @staticmethod
    def delete_random_character(s):
        """Returns s with a random character deleted"""
        if s == "":
            return s

        pos = random.randint(0, len(s) - 1)
        # print("Deleting", repr(s[pos]), "at", pos)
        return s[:pos] + s[pos + 1:]

    @staticmethod
    def insert_random_character(s):
        """Returns s with a random character inserted"""
        pos = random.randint(0, len(s))
        random_character = random.randrange(0, 255)
        # print("Inserting", repr(random_character), "at", pos)
        return s[:pos] + bytes([random_character]) + s[pos:]

    @staticmethod
    def flip_random_character(s):
        """Returns s with a random bit flipped in a random position"""
        if s == "":
            return s

        pos = random.randint(0, len(s) - 1)
        c = s[pos]
        bit = 1 << random.randint(0, 7)
        new_c = bytes([c ^ bit])
        # print("Flipping", bit, "in", repr(c) + ", giving", repr(new_c))
        return s[:pos] + new_c + s[pos + 1:]

    @staticmethod
    def sub_abs(arg1, arg2):
        if arg1 < arg2:
            return arg2 - arg1
        else:
            return arg1 - arg2

    @staticmethod
    def updateArray(condition, byte_array: bytes, index: int, direction: bool, delta: int):
        offset = condition.offsets[index]
        begin = offset['begin']
        end = offset['end']
        sign = offset['sign']
        bytes_to_update = byte_array[begin:end]
        size = end - begin
        int_value = int.from_bytes(bytes_to_update, "little", signed = sign)
        if direction:
            calculated_value = (int_value + delta)
        else:
            calculated_value = (int_value - delta)
        if sign:
            if calculated_value < (2**(8*size-1)):
                calculated_value %=  2**(8*size)
            if calculated_value >= (2**(8*size-1)):
                calculated_value %= 2**(8*size)
                calculated_value -= (2**(8*size-1))
        else:
            calculated_value %=  2**(8*size)
        bytes_to_update = calculated_value.to_bytes(size, "little", signed = sign)
        return byte_array[:begin] + bytes_to_update + byte_array[end:]

    @staticmethod
    def translate_signed_value(v, size):
        if size == 1:
            if v > defs.I8_MAX:
                # [-128, -1] => [0, 127]
                v = v + (defs.I8_MAX)
            else:
                # [0, 127] -> [128, 255]
                v = v + (defs.I8_MAX + 1)
            v = v % (2**8-1)
        if size == 2:
            if v > defs.I16_MAX:
                v = v + defs.I16_MAX
            else:
                v = v + (defs.I16_MAX + 1)
            v = v % (2**16-1)
        if size == 4:
            if v > defs.I32_MAX:
                v = v + defs.I32_MAX
            else:
                v = v + (defs.I32_MAX + 1)
            v = v % (2**32-1)
        if size == 8:
            if v > defs.I64_MAX:
                v = v + defs.I64_MAX
            else:
                v = v + (defs.I64_MAX + 1)

        return v % (2**64-1)
