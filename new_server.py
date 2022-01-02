import queue
import random
import threading
import time
from socket import *

mode_select = '2'

class Server:
    def __init__(self):
        # MODE
        self.mode_select = mode_select

        # BUFFER
        self.server_buffer = 16  # KB
        self.buffer_time_limit = 30
        self.local_store = []

        # POINT SYSTEM
        self.server_minus_points = 0
        self.server_plus_points = 0

        # SERVER SOCKET
        self.serverPort = 12000
        self.clientAddress = gethostname()
        self.serverSocket = socket(AF_INET, SOCK_DGRAM)
        self.serverSocket.bind(('', self.serverPort))

        self.data_queue = queue.Queue()
        self.data_receiver = threading.Thread(target=self.data_receiver)
        self.data_receiver.start()
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
        while True:
            try:
                message, self.clientAddress = self.serverSocket.recvfrom(2048)
                updated_message = (message.decode("utf-8"))
                self.data_queue.put(updated_message)
            except OSError:
                pass

    def server_iteration(self, data):
        # if data is "WON"
        if data == "WON":
            print("* " * 13)
            print("*\t\tCLIENT WON\t\t*")
            print("* " * 13)
            self.serverSocket.close()
            self.data_receiver.join()
            exit()

        #check point is 10
        if(self.server_plus_points-self.server_minus_points) == 10:
            message = "WON"
            self.serverSocket.sendto(message.encode('UTF-8'), self.clientAddress)
            self.serverSocket.close()
            quit()


        message_array = data.split(' ')
        client_rwnd = message_array[0]
        message_length = message_array[1]
        print(f"Message from the client: RWND:{client_rwnd} PCK_LEN:{message_length}")

        # manual mode
        if self.mode_select == '1':
            losing_point = False
            while True:
                message = input("Enter receive window number, packet length and ack status as \"{RWND} {PCK_LEN} {ACK or NAK}\": ")
                if message == "":
                    print("invalid input try again")
                else:
                    break

            message_array = message.split(' ')

            if(len(message_array) != 3):
                losing_point = True

            buffer = message_array[0]
            length = message_array[1]
            ack_message = message_array[2]

            #GOLD DATA CALCULATION
            if int(message_length) <= self.server_buffer: #possible to send?
                remaining_buffer = self.server_buffer - int(message_length)
                gold_length = message_length
                gold_ack_message = "ACK"
            else:
                remaining_buffer = self.server_buffer
                gold_length = 0
                gold_ack_message = "NAK"

            #INPUT CONTROL
            if int(buffer) != remaining_buffer:
                losing_point = True
            elif ack_message != gold_ack_message:
                losing_point = True

            #POINT SYSTEM
            if losing_point: #USER WRONG
                self.server_minus_points += 1

                #Correct the input
                buffer = remaining_buffer
                length = gold_length
                ack_message = gold_ack_message

                print("\t\t** W R O N G :( **")
                print(f"Correct answer was: \"{buffer} {length} {ack_message}\"")
            else: #USER CORRECT
                self.server_plus_points += 1
                print("\t\t** C O R R E C T **")

            #UPDATE BUFFER
            if gold_ack_message == "ACK":
                self.decrease_available_buffer(int(length))
                self.local_store.append([int(message_length), time.time()])

            #ACK MESSAGE
            acknowledged_message = f'{buffer} {length} {ack_message}'
            print(f"\t\tSERVER MESSAGE: {acknowledged_message}")
            print(f"SCORE ->\tTotal:{self.server_plus_points - self.server_minus_points}\t"
                  f"Plus:{self.server_plus_points}\tMinus:{self.server_minus_points}")
            print("-" * 36)
            print("")
            
        # auto mode
        elif self.mode_select == '2':
            # Check if its okay to receive
            if int(message_length) <= self.server_buffer :
                self.decrease_available_buffer(int(message_length))
                self.local_store.append([int(message_length), time.time()])
                ack_message = "ACK"
            else:
                ack_message = "NAK"
                message_length = 0

            random_number = random.randint(0, 100)
            if random_number < 40:
                self.server_minus_points += 1
                old_ack_status = ack_message
                ack_message == "NAK" if ack_message == "ACK" else "ACK"
                print(f"Ack status is wrong. You will LOSE point.\n"
                     f"Correct Ack status: {old_ack_status}")
                ack_message = old_ack_status
            else:
                self.server_plus_points += 1


            acknowledged_message = f'{self.server_buffer} {message_length} {ack_message}'
            print(f"\t\tSERVER MESSAGE: {acknowledged_message}")
            print(f"SCORE ->\tTotal:{self.server_plus_points - self.server_minus_points}\t"
                  f"Plus:{self.server_plus_points}\tMinus:{self.server_minus_points}")
            print("-" * 36)
            print("")
        
        # check point is 10
        if (self.server_plus_points - self.server_minus_points) == 10:
            message = "WON"
            self.serverSocket.sendto(message.encode('UTF-8'), self.clientAddress)
            print("* " * 13)
            print("*\t\tSERVER WON\t\t*")
            print("* " * 13)
            self.serverSocket.close()
            self.data_receiver.join()
            exit()
            
        self.serverSocket.sendto(acknowledged_message.encode('UTF-8'), self.clientAddress)
        print("Waiting for the message from client...")

    def check_timer(self):
        for message in self.local_store:
            length = message[0]
            start_time = message[1]
            end = time.time()

            if (end - start_time) > self.buffer_time_limit:
                self.update_available_buffer(length)
                self.local_store.remove(message)

    def update_available_buffer(self,size):
        self.server_buffer += size
        print("")
        print("*" * 40)
        print("\t\tServer Buffer is Updated")
        print(f"\t\tRemaining Buffer: {self.server_buffer}")
        print("*" * 40)
        print("")
        acknowledgedMessageOne = f'{self.server_buffer} 0 ACK'
        self.serverSocket.sendto(acknowledgedMessageOne.encode('UTF-8'), self.clientAddress)

    def decrease_available_buffer(self,size):
        self.server_buffer -= size

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