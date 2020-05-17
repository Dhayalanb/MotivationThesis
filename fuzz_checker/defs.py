# ** Cond Type
# < 0xFF: simple if
# http:#llvm.org/doxygen/InstrTypes_8h_source.html
# Opcode              U L G E    Intuitive operation
COND_FCMP_FALSE = 0
#/< 0 0 0 0    Always false (always folded)
COND_FCMP_OEQ = 1
#/< 0 0 0 1    True if ordered and equal
COND_FCMP_OGT = 2
#/< 0 0 1 0    True if ordered and greater than
COND_FCMP_OGE = 3
#/< 0 0 1 1    True if ordered and greater than or equal
COND_FCMP_OLT = 4
#/< 0 1 0 0    True if ordered and less than
COND_FCMP_OLE = 5
#/< 0 1 0 1    True if ordered and less than or equal
COND_FCMP_ONE = 6
#/< 0 1 1 0    True if ordered and operands are unequal
COND_FCMP_ORD = 7
#/< 0 1 1 1    True if ordered (no nans)
COND_FCMP_UNO = 8
#/< 1 0 0 0    True if unordered: isnan(X) | isnan(Y)
COND_FCMP_UEQ = 9
#/< 1 0 0 1    True if unordered or equal
COND_FCMP_UGT = 10
#/< 1 0 1 0    True if unordered or greater than
COND_FCMP_UGE = 11
#/< 1 0 1 1    True if unordered greater than or equal
COND_FCMP_ULT = 12
#/< 1 1 0 0    True if unordered or less than
COND_FCMP_ULE = 13
#/< 1 1 0 1    True if unordered less than or equal
COND_FCMP_UNE = 14
#/< 1 1 1 0    True if unordered or not equal
COND_FCMP_TRUE = 15
#/< 1 1 1 1    Always true (always folded)

COND_ICMP_EQ_OP = 32
COND_ICMP_NE_OP = 33
COND_ICMP_UGT_OP = 34
COND_ICMP_UGE_OP = 35
COND_ICMP_ULT_OP = 36
COND_ICMP_ULE_OP = 37
COND_ICMP_SGT_OP = 38
COND_ICMP_SGE_OP = 39
COND_ICMP_SLT_OP = 40
COND_ICMP_SLE_OP = 41
COND_SW_OP = 0x00FF

COND_BASIC_MASK = 0xFF
COND_SIGN_MASK = 0x100
COND_BOOL_MASK = 0x200
# COND_CALL_MASK = 0x400
# COND_CALL_REV_MASK = 0xFBFF

COND_MAX_EXPLORE_OP = 0x4000 - 1
COND_MAX_EXPLOIT_OP = 0x5000 - 1

COND_AFL_OP = 0x8001
# sensititve offsets
COND_FN_OP = 0x8002
COND_LEN_OP = 0x8003
# COND_ENTER_FN = 0x8010
# COND_LEAVE_FN = 0x8011

# condition field
COND_FALSE_ST = 0
COND_TRUE_ST = 1
COND_DONE_ST = 2