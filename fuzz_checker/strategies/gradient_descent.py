from strategies.strategy import Strategy
from cond_stmt import CondStmt
from trace import Trace
from helpers.grad import Grad, GradDirection
from helpers.utils import Util
import defs
import sys
import logging

class GradientDescentStrategy(Strategy):
    
    last_input = None

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
            print("Guess step", guess_step)
            newInput = self.compute_delta_all(condition, grad, guess_step)
            (status, condition_output) = self.handler.run(condition, newInput)
            f_new = condition_output.get_output()
            if f_new < f0:
                print("found better input: ", newInput)
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

    def repick_start_point(self):
        #random
        #TODO
        print("Still have to implement this", file=sys.stderr)
        pass

    def gradient_iteration(self, f0, condition: CondStmt, grad: Grad):
        self.calculate_gradient(f0, condition, grad)
        local_optima = 0
        while grad.max_value() == 0:
            if local_optima < defs.MAX_LOCAL_OPTIMA:
                #stuck in local optima
                return None
            f0 = self.repick_start_point()
            self.calculate_gradient(f0, condition, grad)
            local_optima += 1
        grad.normalize()
        logging.debug("normalized")
        return self.descend(condition, grad, f0)

    def search(self, trace: Trace):
        condition = trace.getCurrentCondition()
        if len(condition.offsets) == 0:
            self.handler.logger.wrong(condition, "No offsets")
            return None
        grad = Grad(len(condition.offsets))
        self.last_input = trace.getInput()
        epoch = 0
        output_value = condition.base.get_output() #TODO checks on status?
        logging.debug("Original output: %s",output_value)
        while epoch < defs.MAX_GRAD_ITERATIONS:
            output_value = self.gradient_iteration(output_value, condition, grad)
            if output_value == None:
                # Not changing input anymore
                self.handler.logger.wrong(condition, "Stuck in optima")
                return None
            epoch += 1
        self.handler.logger.wrong(condition, "Max iterations reached")
        