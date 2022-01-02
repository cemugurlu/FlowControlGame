import queue
import threading
from socket import *
import time
import random

mode_select = None

class Client:
    def __init__(self):
        # CLIENT SOCKET
        self.serverPort = 12000
        self.serverName = gethostname()
        self.serverAddress = None
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)
        self.clientSocket.connect((self.serverName, self.serverPort))

        # POINT SYSTEM
        self.client_minus_points = 0
        self.client_plus_points = 0
        self.losing_point = False

        # BUFFER
        self.init_buffer_size = 16  # KB
        self.buffer_size = 16

        # MODE
        self.mode_select = mode_select
        self.next_turn = True
        self.buffer_update = False

        self.data_queue = queue.Queue()
        self.data_receiver = threading.Thread(target=self.data_receiver)
        self.data_receiver.start()
        self.client_loop()

    def client_loop(self):
        while True:
            try:
                data = self.data_queue.get_nowait()
                self.client_receive_iteration(data)
            except queue.Empty:
                pass

            if self.next_turn and self.buffer_update:
                self.buffer_update = False

            if self.next_turn and not self.buffer_update:
                self.client_send_iteration()

    def data_receiver(self):
        while True:
            try:
                message, self.serverAddress = self.clientSocket.recvfrom(2048)
                updated_message = (message.decode("utf-8"))
                self.data_queue.put(updated_message)
                self.next_turn = True
            except OSError:
                pass

    def client_send_iteration(self):
        #check point is 10
        if (self.client_plus_points-self.client_minus_points) == 10:
            message = "WON"
            self.clientSocket.sendto(message.encode('UTF-8'),
                                     (self.serverName,
                                      self.serverPort) if not self.serverAddress else self.serverAddress)
            self.clientSocket.close()
            quit()

        # USER INTERACTION STATE
        self.losing_point = False
        self.next_turn = False

        # manual mode
        if self.mode_select == '1':
            while True:
                message = input("Enter receive window number and packet length as \"{RWND} {PCK_LEN}\": ")
                if message == "":
                    print("invalid input try again")
                else:
                    break

            message_array = message.split(' ')

            if (len(message_array) != 2) or int(message_array[1]) <= 0:
                print("invalid input")
                print("-" * 36)
                self.client_minus_points = self.client_minus_points + 1
                print("\t\t** W R O N G :( **")
                print(
                    f"SCORE ->\tTotal:{self.client_plus_points - self.client_minus_points}\t"
                    f"Plus:{self.client_plus_points}\tMinus:{self.client_minus_points}")
                print("-" * 36)
                
                return

            # GOLD DATA CALCULATION
            user_rwnd = message_array[0]
            if int(user_rwnd) != self.buffer_size:  # if user write wrong RWND
                print(f"Receive window number is wrong. You will LOSE point.\n"
                      f"Correct RWND: {self.buffer_size}")
                message = f"{self.buffer_size} {message_array[1]}"
                self.losing_point = True

        # auto mode
        elif self.mode_select == '2':
            random_packet_len = random.randint(1, int(self.init_buffer_size/2))
            message = f"{self.buffer_size} {random_packet_len}"
            # randomizes the waiting time of the client
            random_number = random.randint(0, 100)
            if 0 < random_number < 33:
                time.sleep(6)
            elif 33 < random_number < 66:
                time.sleep(7)
            else:
                time.sleep(8)

            print(f"\t\tCLIENT MESSAGE: {message}")
        

        # SEND TO THE SERVER
        self.clientSocket.sendto(message.encode('UTF-8'),
            (self.serverName, self.serverPort) if not self.serverAddress else self.serverAddress)

        print("Waiting for the response from server...")

    def client_receive_iteration(self,data):
        if data == "WON":
            print("* " * 13)
            print("*\t\tSERVER WON\t\t*")
            print("* " * 13)
            self.clientSocket.close()
            self.data_receiver.join()
            exit()

        modifiedMessage_array = data.split(' ')
        server_rwnd = modifiedMessage_array[0]
        server_pck_len = modifiedMessage_array[1]
        server_ack = modifiedMessage_array[2]
        #BUFFER UPDATES
        if int(server_pck_len) == 0 and server_ack == "ACK":
            self.update_buffer(server_rwnd)
            print("")
            print("*"*40)
            print("\t\tServer Buffer is Updated")
            print(f"\t\tServer message: {data}")
            print("*"*40)
            print("")
            self.buffer_update = True
            self.next_turn = True
            return

        self.update_buffer(server_rwnd)  # update buffer according to servers buffer
        print(f"Response from server: RNWD:{server_rwnd} PCK_LEN:{server_pck_len} ACK:{server_ack}")

        # SCORE MECHANISM
        if server_ack == "ACK" and not self.losing_point:
            self.client_plus_points = self.client_plus_points + 1
            print("\t\t** C O R R E C T **")
        else:
            self.client_minus_points = self.client_minus_points + 1
            print("\t\t** W R O N G :( **")

        # OUTPUT
        print(
            f"SCORE ->\tTotal:{self.client_plus_points - self.client_minus_points}\t"
            f"Plus:{self.client_plus_points}\tMinus:{self.client_minus_points}")
        print("-" * 36)
        print("")
        if (self.client_plus_points - self.client_minus_points) == 10:
            message = "WON"
            print("* " * 13)
            print("*\t\tCLIENT WON\t\t*")
            print("* " * 13)
            self.clientSocket.sendto(message.encode('UTF-8'), self.serverAddress)
            self.clientSocket.close()
            self.data_receiver.join()
            exit()

    def update_buffer(self,server_buffer):
        self.buffer_size = int(server_buffer)

if __name__ == '__main__':
    # MODE SELECTION
    while True:
        mode_select = input("Press 1 for manual mode, press 2 for auto mode:")
        if mode_select == '1':
            print('Manual mode is activated.')
            break
        elif mode_select == '2':
            print('Auto mode is activated.')
            break
        else:
            print('Invalid entry. Please try again.')
    Client()