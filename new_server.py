import queue
import threading
import time
from socket import *

# ATTRIBUTES
# MODE
mode_select = '2'

# BUFFER
server_buffer = 8  # KB
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
         global clientAddress,serverSocket
         while True:
             message, clientAddress = serverSocket.recvfrom(2048)
             updated_message = (message.decode("utf-8"))
             self.data_queue.put(updated_message)

    def server_iteration(self, data):
        message_array = data.split(' ')
        client_rwnd = message_array[0]
        message_length = message_array[1]
        print(f"Message from the client: RWND:{client_rwnd} PCK_LEN:{message_length}")

        # manual mode
        if mode_select == '1':
            losing_point = False
            message = input("Enter receive window number, packet length and ack status as \"{RWND} {PCK_LEN} {ACK or NAK}\": ")
            message_array = message.split(' ')

            if(len(message_array) != 3):
                losing_point = True

            buffer = message_array[0]
            length = message_array[1]
            ack_message = message_array[2]

            #GOLD DATA CALCULATION

            if int(message_length) <= server_buffer: #possible to send?
                remaining_buffer = server_buffer - int(message_length)
                gold_ack_message = "ACK"
            else:
                remaining_buffer = server_buffer
                gold_length = 0
                gold_ack_message = "NAK"

            #INPUT CONTROL
            if int(buffer) != remaining_buffer:
                losing_point = True
            elif ack_message != gold_ack_message:
                losing_point = True

            #POINT SYSTEM
            print("-" * 36)
            if losing_point: #USER WRONG
                global server_minus_points
                server_minus_points += 1

                #Correct the input
                buffer = remaining_buffer
                length = gold_length
                ack_message = gold_ack_message

                print("\t\t** W R O N G :( **")
                print(f"Correct answer was: \"{server_buffer} {length} {ack_message}\"")
            else: #USER CORRECT
                global server_plus_points
                server_plus_points += 1
                print("\t\t** C O R R E C T **")

            #UPDATE BUFFER
            if gold_ack_message == "ACK":
                self.decrease_available_buffer(int(length))
                local_store.append([int(message_length), time.time()])

            #ACK MESSAGE
            acknowledged_message = f'{buffer} {length} {ack_message}'

            print(f"SCORE ->\tTotal:{server_plus_points - server_minus_points}\tPlus:{server_plus_points}\tMinus:{server_minus_points}")
            print("-" * 36)

        # auto mode
        elif mode_select == '2':
            # Check if its okay to receive
            if int(message_length) <= server_buffer :
                self.decrease_available_buffer(int(message_length))
                local_store.append([int(message_length), time.time()])
                ack_message = "ACK"
            else:
                ack_message = "NAK"
                message_length = 0

            acknowledged_message = f'{server_buffer} {message_length} {ack_message}'

        serverSocket.sendto(acknowledged_message.encode('UTF-8'), clientAddress)
        print("Waiting for the message from client...")

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

        print(f"kalan buffer {server_buffer}")
        acknowledgedMessageOne = f'{server_buffer} 0 ACK'
        serverSocket.sendto(acknowledgedMessageOne.encode('UTF-8'), clientAddress)


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
    print("Waiting for the message from client...")
    Server()