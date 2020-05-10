import socket
import sys, os
from shm_conds import CondStmtBase

class ForkSrv:
    sock = None
    server_address = '../forksrv_socket'

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
        while True:
            connection, client_address = self.sock.accept()
            try:
                print('connection from', client_address, file=sys.stderr)

                # Receive the data in small chunks and retransmit it
                while True:
                    print("Sending signal")
                    connection.sendall(bytes('\x01\x01\x01\x01', encoding='utf8'))#signal start
                    condStmtBase = CondStmtBase()
                    condStmtBase.cmpid = 3997931254
                    condStmtBase.context = 201841
                    condStmtBase.order = 1
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
                    print(CondStmtBase)

                    break
                    
            finally:
                # Clean up the connection
                connection.close()
server = ForkSrv()
server.listen()