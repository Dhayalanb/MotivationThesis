from strategies.strategy import Strategy
from cond_stmt import CondStmt
from trace import Trace
from helpers.grad import Grad
from helpers.utils import Util
import defs
import sys

class GradientDescentStrategy(Strategy):
    
    last_input = None
    grad = None

    def calculate_gradient(self, output_orig, condition: CondStmt):
        origInput = self.last_input
        max_val = 0
        for direction in self.grad.directions:
            (sign, linear, delta) = self.partialDerivative(condition, direction, origInput, output_orig)
            if delta > max_val:
                max_val = delta
            condition.linear &= linear
            direction.value = delta
            direction.sign = sign

    def descend(self, condition: CondStmt, grad: Grad, f0):
        vsum = grad.val_sum()
        if vsum > 0:
            guess_step = f0 / vsum
            newInput = self.compute_delta_all(grad, guess_step)
            (status, condition_output) = self.handler.run(condition, newInput)
            f_new = condition_output.get_output()
            if f_new < f0:
                self.last_input = newInput
                f0 = f_new
        else:
            # We are not changing anything anymore
            # Angora starts using partial gradients here, not pure, skipping
            return None
        return f0
            
        


    def partialDerivative(self, condition: CondStmt, i: int, origInput, output_orig):
        results = []
        newInput = Util.mutateOffset(origInput, i, True) #1 bigger
        results.append(self.handler.run(condition, newInput))
        newInput = Util.mutateOffset(origInput, i, False) #1 smaller
        results.append(self.handler.run(condition, newInput))
        output_plus = results[0].condition.get_output()
        output_min = results[1].condition.get_output()
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
        print("Still have to implement this", file=sys.stderr)
        pass

    def gradient_iteration(self, f0, condition: CondStmt):
        self.calculate_gradient(condition, grad)
        local_optima = 0
        while grad.max_value() == 0:
            if local_optima < defs.MAX_LOCAL_OPTIMA:
                #stuck in local optima
                return None
            self.repick_start_point()
            self.calculate_gradient(condition, grad)
            local_optima += 1
        grad.normalize()
        return self.descend(condition, grad, f0)

    def search(self, trace: Trace):
        if not self.last_input:
            self.last_input = trace.getInput()
        condition = trace.getCurrentCondition()
        self.grad = Grad(len(condition.offsets))
        epoch = 0
        output_value = condition.get_output[1] #TODO checks on status?
        while epoch < defs.MAX_GRAD_ITERATIONS:
            output_value = self.gradient_iteration(condition, output_value)
            if output_value == None:
                # Not changing input anymore
                return None
            epoch += 1
        