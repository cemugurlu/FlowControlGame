import queue
import threading
import time
from socket import *

# ATTRIBUTES
# MODE
mode_select = '2'

# BUFFER
server_buffer = 8  # KB
buffer_available = True
used_buffer = 0
buffer_time_limit = 10
local_store = []

# POINT SYSTEM
server_minus_points = 0
server_plus_points = 0

# SERVER SOCKET
serverPort = 12000
clientAddress = gethostname()
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive')

class Server:
    def __init__(self):
        self.data_queue = queue.Queue()
        data_receiver = threading.Thread(target=self.data_receiver)
        data_receiver.start()
        self.server_loop()

    def server_loop(self):
        while True:
            self.check_timer()
            #Check if there is a message
            try:
                data = self.data_queue.get_nowait()
                self.server_iteration(data)
            except queue.Empty:
                pass

    def data_receiver(self):
         global clientAddress
         message, clientAddress = serverSocket.recvfrom(2048)

         #edit the data in any way necessary here
         updated_message = (message.decode("utf-8"))
         self.data_queue.put(updated_message)

    def server_iteration(self, data):
        #Assume this method handles updating, drawing, etc
        message_array = data.split(' ')
        client_rwnd = message_array[0]
        message_length = message_array[1]

        self.decrease_available_buffer(int(message_length))
        local_store.append([int(message_length), time.time()])

        # manual mode
        if mode_select == '1':
            print("manual mod")
            acknowledgedMessage = f'{server_buffer} {message_length}'
            # acknowledgedMessage = f'ACK {server_buffer}'
            # TODO: Get  ACK message from user input
            # TODO: send ACK message
            # TODO: Input: Remaining buffer length, ACK or NAK *

        # auto mode
        elif mode_select == '2':
            print("auto mod")
            acknowledgedMessage = f'{server_buffer} {message_length}'
            # TODO: Send ACK, Cond, if manual wait for user input from terminal
            # TODO: Input: Remaining buffer length, ACK or NAK *

        print("A")
        serverSocket.sendto(acknowledgedMessage.encode('UTF-8'), clientAddress)
        print("B")

    def check_timer(self):
        for message in local_store:
            length = message[0]
            start_time = message[1]
            end = time.time()

            if (end - start_time) > buffer_time_limit:
                self.update_available_buffer(length)
                local_store.remove(message)


    def update_available_buffer(self,size):
        global server_buffer, clientAddress
        print("BUFFER UPDATED")
        server_buffer += size
        acknowledgedMessageOne = f'ACK {server_buffer}'
        serverSocket.sendto(acknowledgedMessageOne.encode('UTF-8'), (clientAddress, serverPort))


    def decrease_available_buffer(self,size):
        global server_buffer
        server_buffer -= size


if __name__ == '__main__':
    # MODE SELECTION
    while True:
        mode_select = input("Press 1 for manual mode, press 2 for auto mode:")
        if mode_select == '1':
            print('Manual mode is activated.')
            isAutomatic = False
            break
        elif mode_select == '2':
            print('Auto mode is activated.')
            isAutomatic = True
            break
        else:
            print('Invalid entry. Please try again.')
    Server()