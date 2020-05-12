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
class CondStmtBase:
    FORMAT = "<IIIIIIIIIIQQ" #little endian
    def __init__(self):
        self.cmpid = self.order = self.belong = self.condition = self.level = self.op = self. size = self.lb1 = self.lb2 = self.arg1 = self.arg2 = 0

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
    

    
