import socket
import sys, os, stat
from cond_stmt_base import CondStmtBase

class ForkSrv:
    sock = None
    server_address = '../forksrv_socket'
    connection = None
    input_folder = '../test/input/'
    file_hander = None

    def listen(self):
        # Make sure the socket does not already exist
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        os.chmod(self.server_address, 0o664 ) #make socket accessable
        self.file_hander = open(self.input_folder+"1.txt", "wb")
        self.sock.listen(1)
        print("Listening")
        self.connection, client_address = self.sock.accept()
        print('connection from', client_address, file=sys.stderr)
        #accepted forkcli
    

    def reset_input_file(self, input_content):
        self.file_hander.seek(0)
        self.file_hander.write(input_content)

    def run_with_condition(self, condition, input_content):

        self.reset_input_file(input_content)

        print("Sending signal")
        self.connection.sendall(bytes('\x01\x01\x01\x01', encoding='utf8'))#signal start
        print("Sending condStmtBase")
        self.connection.sendall(condition.toStruct())#send cmpid
        print("Reveiving pid")
        pid = self.connection.recv(4)
        print('received "%s"', pid)

        print("Reveiving status")
        status = self.connection.recv(4)
        print('received "%s"', status)

        print("Reveiving compare data")
        cmp_data = self.connection.recv(CondStmtBase.getSize())
        print('received "%s"', cmp_data)
        receivedCondStmtBase = CondStmtBase.createFromStruct(cmp_data)
        print(receivedCondStmtBase.__dict__)
        return (status, receivedCondStmtBase)


    def close(self):
        self.file_hander.close()
        self.connection.close()
        os.remove(self.server_address)