from forksrv import ForkSrv
from cond_stmt_base import CondStmtBase
import logging, os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
condition = CondStmtBase.fromJson({'context': 0, 'lb1': 4294967295, 'lb2': 0, 'order': 1, 'condition': 0, 'arg2': 4194967291, 'op': 294, 'size': 4, 'belong': 0, 'arg1': 2756609892, 'isSkipped': False, 'cmpid': 3997980985, 'level': 0})
server = ForkSrv()
server.listen(0)
server.run_with_condition(condition, b'h=0lo worl\xfc\x1e\n\xfa(6\xec\xc3^\xffL')
server.close()