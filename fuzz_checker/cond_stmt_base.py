'''
Implementation of the rust struct:

pub struct CondStmtBase :
    pub cmpid: u32,
    pub context: u32,
    pub order: u32,
    pub belong: u32,

    pub condition: u32,
    pub level: u32,
    pub op: u32,
    pub size: u32,

    pub lb1: u32,
    pub lb2: u32,

    pub arg1: u64,
    pub arg2: u64,
'''

import struct
import defs
from helpers.utils import Util
class CondStmtBase:
    FORMAT = "<IIIIIIIIIIQQ" #little endian
    EPS = 1

    def __init__(self):
        self.cmpid = self.order = self.belong = self.condition = self.level = self.op = self. size = self.lb1 = self.lb2 = self.arg1 = self.arg2 = self.context = 0
        self.isSkipped = False

    @staticmethod
    def getSize() :
        return struct.calcsize(CondStmtBase.FORMAT)

    def toStruct(self):
        return struct.pack(CondStmtBase.FORMAT, self.cmpid, self.context, self.order, self.belong, self.condition, self.level, self.op, self.size, self.lb1, self.lb2, self.arg1, self.arg2)

    @staticmethod
    def createFromStruct(data):
        condStmtBase = CondStmtBase()
        data = struct.unpack(CondStmtBase.FORMAT, data)
        condStmtBase.cmpid = data[0]
        condStmtBase.context = data[1]
        condStmtBase.order = data[2]
        condStmtBase.belong = data[3]
        condStmtBase.condition = data[4]
        condStmtBase.level = data[5]
        condStmtBase.op = data[6]
        condStmtBase.size = data[7]
        condStmtBase.lb1 = data[8]
        condStmtBase.lb2 = data[9]
        condStmtBase.arg1 = data[10]
        condStmtBase.arg2 = data[11]
        return condStmtBase

    @staticmethod
    def fromJson(json):
        condStmt = CondStmtBase()
        condStmt.__dict__.update(json)
        return condStmt


    def flip_condition(self):
        if self.condition == defs.COND_FALSE_ST:
            self.condition = defs.COND_TRUE_ST
        else:
            self.condition = defs.COND_FALSE_ST
        
    def is_explore(self):
        return self.op <= defs.COND_MAX_EXPLORE_OP
    

    def is_exploitable(self):
        return self.op > defs.COND_MAX_EXPLORE_OP and self.op <= defs.COND_MAX_EXPLOIT_OP
    

    def is_signed(self):
        return (self.op & defs.COND_SIGN_MASK) > 0 or ((self.op & defs.COND_BASIC_MASK) >= defs.COND_ICMP_SGT_OP and (self.op & defs.COND_BASIC_MASK) <= defs.COND_ICMP_SLE_OP)
    

    def is_afl(self):
        return self.op == defs.COND_AFL_OP
    

    def may_be_bool(self):
        # sign or unsigned
        return self.op & 0xFF == defs.COND_ICMP_EQ_OP and self.arg1 <= 1 and self.arg2 <= 1
    

    def is_float(self):
        return (self.op & defs.COND_BASIC_MASK) <= defs.COND_FCMP_TRUE
    

    def is_switch(self) :
        return (self.op & defs.COND_BASIC_MASK) == defs.COND_SW_OP
    

    def is_done(self):
        return self.condition == defs.COND_DONE_ST


    def get_condition_output(self, fast = False):
        op = self.op & defs.COND_BASIC_MASK
        if op == defs.COND_SW_OP:
            return self.arg1 #The condition for a switch is located at arg1
        if fast:
            return self.lb1 #From the fast instrumentation, it is located at lb1
        return self.condition #From the track information it is located at condition for non switch statements

    def isReached(self):
        return self.lb1 != 2**32-1

    def getLogId(self):
        return str(self.cmpid) + '_' + str(self.context)

    def get_output(self):
        a = self.arg1
        b = self.arg2

        if self.is_signed():
            a = Util.translate_signed_value(a, self.size)
            b = Util.translate_signed_value(b, self.size)
        

        op = self.op & defs.COND_BASIC_MASK

        if op == defs.COND_SW_OP:
            op = defs.COND_ICMP_EQ_OP
        

        # if its condition is true, we want its opposite constraint.
        if self.is_explore() and self.condition == defs.COND_TRUE_ST:
            op_mapping = {
                defs.COND_ICMP_EQ_OP : defs.COND_ICMP_NE_OP,
                defs.COND_ICMP_NE_OP : defs.COND_ICMP_EQ_OP,
                defs.COND_ICMP_UGT_OP : defs.COND_ICMP_ULE_OP,
                defs.COND_ICMP_UGE_OP : defs.COND_ICMP_ULT_OP,
                defs.COND_ICMP_ULT_OP : defs.COND_ICMP_UGE_OP,
                defs.COND_ICMP_ULE_OP : defs.COND_ICMP_UGT_OP,
                defs.COND_ICMP_SGT_OP : defs.COND_ICMP_SLE_OP,
                defs.COND_ICMP_SGE_OP : defs.COND_ICMP_SLT_OP,
                defs.COND_ICMP_SLT_OP : defs.COND_ICMP_SGE_OP,
                defs.COND_ICMP_SLE_OP : defs.COND_ICMP_SGT_OP,
            }
            if op in op_mapping:
                op = op_mapping[op]
            
        
        # RELU: if f <= 0, we set f = 0.
        # In other words, if we reach our goal, f = 0.

        if op == defs.COND_ICMP_EQ_OP:
            # a == b : f = abs(a - b)
            output = Util.sub_abs(a, b)
        elif op == defs.COND_ICMP_NE_OP:
            # a != b :
            # f = 0 if a != b, and f = 1 if a == b
            if a == b :
                output = 1
            else:
                output = 0
        elif op == (defs.COND_ICMP_SGT_OP | defs.COND_ICMP_UGT_OP):
            # a > b :
            # f = 0 if a > b, and f = b - a + e if a <= b
            if a > b:
                output = 0
            else:
                output = b - a + self.EPS
            
        elif op == (defs.COND_ICMP_UGE_OP | defs.COND_ICMP_SGE_OP):
            # a > = b
            # f = 0 if a >= b, and f = b - a if a < b
            if a >= b:
                output = 0
            else: 
                output = b - a
            
            
        elif op == (defs.COND_ICMP_ULT_OP | defs.COND_ICMP_SLT_OP):
            # a < b :
            # f = 0 if a < b, and f = a - b + e if a >= b
            if a < b:
                output = 0
            else:
                output = a - b + self.EPS
                
            
        elif op == (defs.COND_ICMP_ULE_OP | defs.COND_ICMP_SLE_OP):
            # a < = b
            # f = 0 if a <= b, and f = a - b if a > b
            if a <= b:
                output = 0
            else:
                output = a - b
                
        else:
            #TODO : support float.
            # if self.is_float() 
            output = Util.sub_abs(a, b)
            
        

        print(
            "id: %s, op:  %s-> %s, size:%s, condition: %s, arg(0x:%s 0x:%s), output: %s" % (
            self.cmpid, self.op, op, self.size, self.condition, a, b, output)
        )

        return output
    
