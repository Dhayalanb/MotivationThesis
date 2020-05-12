import socket
import sys, os
from shm_conds import CondStmtBase

class ForkSrv:
    sock = None
    server_address = '../forksrv_socket'

    def __init__(self, executor):
        self.condStmts = condStmts.getCondStmts()
        self.executor = executor

    def listen(self):
        # Make sure the socket does not already exist
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        self.sock.listen(1)
        print("Listening")
        connection, client_address = self.sock.accept()
        #accepted forkcli
        try:
            print('connection from', client_address, file=sys.stderr)

            # Receive the data in small chunks and retransmit it
            for condStmtBase in self.condStmts:
                print("Sending signal")
                connection.sendall(bytes('\x01\x01\x01\x01', encoding='utf8'))#signal start
                print("Sending condStmtBase")
                connection.sendall(condStmtBase.toStruct())#send cmpid
                print("Reveiving pid")
                pid = connection.recv(4)
                print('received "%s"', pid)

                print("Reveiving status")
                status = connection.recv(4)
                print('received "%s"', status)

                print("Reveiving compare data")
                cmp_data = connection.recv(CondStmtBase.getSize())
                print('received "%s"', cmp_data)
                receivedCondStmtBase = CondStmtBase.createFromStruct(cmp_data)
                print(receivedCondStmtBase.__dict__)

                executor.processResult(receivedCondStmtBase)
                
        finally:
            # Clean up the connection
            connection.close()