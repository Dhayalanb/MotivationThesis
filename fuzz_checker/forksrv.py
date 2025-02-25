import socket
import sys, os, stat, signal
from cond_stmt_base import CondStmtBase
import defs
import subprocess
import logging, resource

class ForkSrv:
    sock = None
    server_address = '../forksrv_socket'
    connection = None
    input_folder = defs.INPUT_DIR
    file_hander = None
    id = -1

    def listen(self, id):
        # Make sure the socket does not already exist
        self.id = id
        self.server_address = "../forksrv_socket" + "_" +str(id)
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
        logging.warning("Listening %d" % self.id)
        self.run_binary(id)
        self.connection, client_address = self.sock.accept()
        logging.warning('connection from %s at %d' % (client_address, self.id))
        #accepted forkcli

    def run_binary(self, id):
        new_env = os.environ.copy()
        new_env['ANGORA_FORKSRV_SOCKET_PATH'] = self.server_address
        arguments = [defs.BINARY] + [self.input_file if arg == '@@' else arg for arg in defs.ARGUMENTS ]
        self.client = subprocess.Popen(arguments, env=new_env, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        preexec_fn=limit_virtual_memory
        )

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
        logging.debug("Receiving pid")
        pid = self.connection.recv(4)
        logging.debug('received "%s"', pid)

        logging.debug("Reveiving status")
        #Make sure program does not execute longer than execution time
        self.connection.settimeout(defs.MAXIMUM_EXECUTION_TIME)
        try:
            status = self.connection.recv(4)
            logging.debug('received "%s"', status)

            logging.debug("Receiving compare data")
            cmp_data = self.connection.recv(CondStmtBase.getSize())
        except socket.timeout as e:
            #kill child process of fork client, kill client later
            try:
                os.kill(int.from_bytes(pid, byteorder="little"), signal.SIGKILL)
            except OSError as err:
                #Happens is child already ended between these lines
                logging.warn("Could not kill child")
                pass
            #give exception to handler
            raise e
        #reset timeout
        self.connection.settimeout(None)
        if len(cmp_data) != CondStmtBase.getSize():
            raise socket.timeout()
        #logging.debug('received "%s"', cmp_data)
        receivedCondStmtBase = CondStmtBase.createFromStruct(cmp_data)
        #logging.debug(receivedCondStmtBase.__dict__)
        return (status, receivedCondStmtBase)


    def close(self):
        self.file_hander.close()
        self.connection.close()
        self.client.kill()
        os.remove(self.server_address)
        os.remove(self.input_file)

def limit_virtual_memory():
    # The tuple below is of the form (soft limit, hard limit). Limit only
    # the soft part so that the limit can be increased later (setting also
    # the hard limit would prevent that).
    # When the limit cannot be changed, setrlimit() raises ValueError.
    resource.setrlimit(resource.RLIMIT_AS, (defs.MAX_VIRTUAL_MEMORY, defs.MAX_VIRTUAL_MEMORY))