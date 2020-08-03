from strategies.strategy import Strategy
from cond_stmt import CondStmt
from trace import Trace
from helpers.grad import Grad, GradDirection
from helpers.utils import Util
import defs
import sys
import logging
from strategies.magic_byte import MagicByteStrategy

class GradientDescentStrategy(Strategy):
    
    original_input = None
    last_input = None
    repick_count = 0

    #When condition is not reached, return

    def calculate_gradient(self, output_orig, condition: CondStmt, grad: Grad):
        origInput = self.last_input
        max_val = 0
        for i in range(len(grad.directions)):
            (sign, linear, delta) = self.partialDerivative(condition, i, origInput, output_orig)
            if delta > max_val:
                max_val = delta
            condition.linear &= linear
            grad.directions[i].value = delta
            grad.directions[i].sign = sign
            logging.debug('delta: %d', delta)

    def compute_delta_all(self, condition: CondStmt, grad: Grad, step: int):
        new_input = self.last_input
        for i in range(len(grad.directions)):
            movement = grad.directions[i].percent * step
            new_input = Util.updateArray(condition, new_input, i, grad.directions[i].sign, movement)
        return new_input
        
    

    def descend(self, condition: CondStmt, grad: Grad, f0):
        vsum = grad.val_sum()
        logging.debug("vsum: %d", vsum)
        if vsum > 0:
            guess_step = f0 / vsum
            logging.info("Guess step %d" % guess_step)
            newInput = self.compute_delta_all(condition, grad, guess_step)
            (status, condition_output) = self.handler.run(condition, newInput)
            f_new = condition_output.get_output()
            if f_new < f0:
                logging.info("found better input: %s" % newInput)
                self.last_input = newInput
                f0 = f_new
        else:
            # We are not changing anything anymore
            # Angora starts using partial gradients here, not pure, skipping
            # Could also do a repick startpoint
            return None
        return f0


    def partialDerivative(self, condition: CondStmt, index: int, origInput, output_orig):
        results = []
        newInput = Util.updateArray(condition, origInput, index, True, 1) #1 bigger
        logging.debug("new input: %s",newInput)
        results.append(self.handler.run(condition, newInput))
        newInput = Util.updateArray(condition, origInput, index, False, 1)#1 smaller
        logging.debug("new input 2: %s",newInput)
        results.append(self.handler.run(condition, newInput))
        output_plus = results[0][1].get_output() #TODO Check on status?
        output_min = results[1][1].get_output()
        logging.debug("Output plus: %s", output_plus)
        logging.debug("Output min: %s", output_min)
        logging.debug("Output orig: %s", output_orig)
        #Add sign, linear, delta
        if output_plus < output_orig and output_min < output_orig:
            if output_min < output_plus:
                (False, False, output_orig - output_min)
            else:
                (True, False, output_orig - output_plus)
        if not output_plus < output_orig and output_min < output_orig:
            return (False, 
            output_plus != output_orig and output_orig - output_min == output_plus - output_orig
            , output_orig - output_min)
        if output_plus < output_orig and not output_min < output_orig:
            return (True, 
            output_min != output_orig and output_min - output_orig == output_orig - output_plus
            , output_plus - output_orig)
        if not output_plus < output_orig and not output_min < output_orig:
            return (True, False, 0)

    def repick_start_point(self, condition: CondStmt):
        reverse = False if self.repick_count %2 == 0 else True
        if self.repick_count == 0 or self.repick_count == 1:
            MagicByteStrategy.fill_in(self.original_input, condition, reverse)
            self.handler.comment("fill_in_%d" % reverse)
        if self.repick_count == 2 or self.repick_count == 3:
            value = 1 if self.repick_count <= 2 else -1
            MagicByteStrategy.arithmatic(self.original_input, condition, reverse, value)
            self.handler.comment("arithmatic_%d" % reverse)
            self.last_input = cur_input
            (status, condition_output) = self.handler.run(condition, cur_input)
            return condition_output.get_output()
        #insert random bytes on all offsets
        cur_input = self.last_input
        for cur_offset in range(condition.offsets):
            begin = condition.offsets[cur_offset]['begin']
            end = condition.offsets[cur_offset]['end']
            bytes_to_insert = bytes([]).join([Util.insert_random_character(bytes([])) for i in range(end-begin)])
            cur_input = cur_input[:begin] + bytes_to_insert + cur_input[end:]
        self.last_input = cur_input
        (status, condition_output) = self.handler.run(condition, cur_input)
        return condition_output.get_output()

    def gradient_iteration(self, f0, condition: CondStmt, grad: Grad):
        self.calculate_gradient(f0, condition, grad)
        local_optima = 0
        while grad.max_value() == 0:
            if local_optima < defs.MAX_LOCAL_OPTIMA:
                #stuck in local optima
                return None
            f0 = self.repick_start_point(condition)
            self.repick_count += 1
            self.calculate_gradient(f0, condition, grad)
            local_optima += 1
        grad.normalize()
        logging.debug("normalized")
        return self.descend(condition, grad, f0)

    def search(self, trace: Trace, index:int):
        condition = trace.getCondition(index)
        if len(condition.offsets) == 0:
            self.handler.wrong(defs.COMMENT_NO_OFFSETS)
            return None
        grad = Grad(len(condition.offsets))
        self.last_input = trace.getInput()
        self.original_input = self.last_input
        epoch = 0
        output_value = condition.base.get_output() #TODO checks on status?
        logging.debug("Original output: %s",output_value)
        while epoch < defs.MAX_GRAD_ITERATIONS:
            output_value = self.gradient_iteration(output_value, condition, grad)
            if output_value == None:
                # Not changing input anymore
                self.handler.wrong(defs.COMMENT_STUCK_IN_OPTIMA)
                return None
            epoch += 1
        self.handler.wrong(defs.COMMENT_TRIED_EVERYTHING)
        