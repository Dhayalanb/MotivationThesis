import socket
import sys, os, stat
from cond_stmt_base import CondStmtBase
import defs
import subprocess
import logging

class ForkSrv:
    sock = None
    server_address = '../forksrv_socket'
    connection = None
    input_folder = '../test/input/'
    file_hander = None
    id = -1

    def listen(self, id):
        # Make sure the socket does not already exist
        self.id = id
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
        logging.info("Listening")
        self.run_binary(id)
        self.connection, client_address = self.sock.accept()
        logging.debug('connection from', client_address)
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

    def rebind(self):
        self.close()
        self.listen(self.id)

    def run_with_condition(self, condition, input_content):

        self.reset_input_file(input_content)

        logging.debug("Sending signal")
        self.connection.sendall(bytes('\x01\x01\x01\x01', encoding='utf8'))#signal start
        logging.debug("Sending condStmtBase")
        self.connection.sendall(condition.toStruct())#send cmpid
        logging.debug("Reveiving pid")
        pid = self.connection.recv(4)
        logging.debug('received "%s"', pid)

        logging.debug("Reveiving status")
        #Make sure program does not execute longer than execution time
        self.connection.settimeout(defs.MAXIMUM_EXECUTION_TIME)
        status = self.connection.recv(4)
        logging.debug('received "%s"', status)

        logging.debug("Reveiving compare data")
        cmp_data = self.connection.recv(CondStmtBase.getSize())

        #reset timeout
        self.connection.settimeout(None)
        logging.debug('received "%s"', cmp_data)
        receivedCondStmtBase = CondStmtBase.createFromStruct(cmp_data)
        logging.debug(receivedCondStmtBase.__dict__)
        return (status, receivedCondStmtBase)


    def close(self):
        self.file_hander.close()
        self.connection.close()
        self.client.kill()
        os.remove(self.server_address)
        os.remove(self.input_file)