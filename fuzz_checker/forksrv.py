import socket
import sys, os, stat
from cond_stmt_base import CondStmtBase
import defs
import subprocess

class ForkSrv:
    sock = None
    server_address = '../forksrv_socket'
    connection = None
    input_folder = '../test/input/'
    file_hander = None

    def listen(self, id):
        # Make sure the socket does not already exist
        self.server_address = self.server_address + "_" +str(id)
        try:
            os.unlink(self.server_address)
        except OSError:
            if os.path.exists(self.server_address):
                raise
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.server_address)
        os.chmod(self.server_address, 0o664 ) #make socket accessable
        self.input_file = self.input_folder+str(id)+".txt"
        self.file_hander = open(self.input_file, "wb")
        self.sock.listen(1)
        print("Listening")
        self.run_binary(id)
        self.connection, client_address = self.sock.accept()
        print('connection from', client_address)
        #accepted forkcli

    def run_binary(self, id):
        new_env = os.environ.copy()
        new_env['ANGORA_FORKSRV_SOCKET_PATH'] = self.server_address
        self.client = subprocess.Popen([defs.BINARY, self.input_file], env=new_env)

    def reset_input_file(self, input_content):
        self.file_hander.seek(0)
        self.file_hander.write(input_content)
        self.file_hander.truncate() #old content was still in the file, remove it
        self.file_hander.seek(0) #set position to read again at the start

    def run_with_condition(self, condition, input_content):

        self.reset_input_file(input_content)

        #print("Sending signal")
        self.connection.sendall(bytes('\x01\x01\x01\x01', encoding='utf8'))#signal start
        #print("Sending condStmtBase")
        self.connection.sendall(condition.toStruct())#send cmpid
        #print("Reveiving pid")
        pid = self.connection.recv(4)
        #print('received "%s"', pid)

        #print("Reveiving status")
        status = self.connection.recv(4)
        #print('received "%s"', status)

        #print("Reveiving compare data")
        cmp_data = self.connection.recv(CondStmtBase.getSize())
        #print('received "%s"', cmp_data)
        receivedCondStmtBase = CondStmtBase.createFromStruct(cmp_data)
        #print(receivedCondStmtBase.__dict__)
        return (status, receivedCondStmtBase)


    def close(self):
        self.file_hander.close()
        self.connection.close()
        self.client.kill()
        os.remove(self.server_address)
        os.remove(self.input_file)