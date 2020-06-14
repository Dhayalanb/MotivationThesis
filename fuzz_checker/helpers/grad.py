import defs

class Grad:

    directions = []

    def __init__(self, numberOfDirections):
        self.directions = [GradDirection() for i in range(numberOfDirections)]

    def normalize(self):
        # f32::MAX > u64::MAX
        max_grad = self.max_value()
        if max_grad > 0.0:
            for direction in self.directions:
                direction.percent = defs.GD_MOMENTUM_BETA * direction.percent + (1.0 - defs.GD_MOMENTUM_BETA) * (direction.value / max_grad)
            
        
    

    def max_value(self):
        return max([direction.value for direction in self.directions])
        
    

    def val_sum(self):
        total_sum = 0
        for direction in self.directions:
            total_sum += direction.value
        return total_sum
    

    def clear(self):
        for direction in self.directions:
            direction.percent = 0.0
            direction.value = 0
        
    


class GradDirection:
    sign = False
    value = 0
    percent = 0
