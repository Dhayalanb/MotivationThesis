import socket
import sys, os

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
        while True:
            connection, client_address = self.sock.accept()
            try:
                print('connection from', client_address, file=sys.stderr)

                # Receive the data in small chunks and retransmit it
                while True:
                    connection.sendall(bytes('\x01\x01\x01\x01', encoding='utf8'))
                    data = connection.recv(4)
                    data2 = connection.recv(48)
                    print('received "%s"', data)
                    print('received "%s"', data2)
                    break
                    
            finally:
                # Clean up the connection
                connection.close()

server = ForkSrv()
server.listen()