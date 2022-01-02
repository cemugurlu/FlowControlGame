from socket import *
import time

import random

# ATTRIBUTES
# MODE
mode_select = "2"

# BUFFER
init_buffer_size = 8 # KB
buffer_size = 8

# POINT SYSTEM
client_minus_points = 0
client_plus_points = 0

# CLIENT SOCKET
serverPort = 12000
serverName = gethostname()
serverAddress = None
clientSocket = socket(AF_INET, SOCK_DGRAM)

modifiedMessage = '8 0'.encode('utf-8')

def main():
    global client_minus_points,client_plus_points,modifiedMessage

    while True:
        #TODO
        #CHECK BUFFER SIZE INCREASE MESSAGE
        #BUNU HEP KONTROL edebilmeli

        #USER INTERACTION STATE
        losing_point = False

        # manual mode
        if mode_select == '1':
            message = input("Enter receive window number and packet length as \"{RWND} {PCK_LEN}\": ")
            message_array = message.split(' ')

            if (len(message_array) != 2) or int(message_array[1]) <= 0:
                print("invalid input")
                client_minus_points = client_minus_points + 1
                print("\t\t** W R O N G :( **")
                print(f"SCORE ->\tTotal:{client_plus_points - client_minus_points}\tPlus:{client_plus_points}\tMinus:{client_minus_points}")
                print("-" * 32)
                continue

            # GOLD DATA CALCULATION
            user_rwnd = message_array[0]
            if int(user_rwnd) != buffer_size: #if user write wrong RWND
                print(f"Receive window number is wrong. You will LOSE point.\nCorrect RWND: {buffer_size}")
                message = f"{buffer_size} {message_array[1]}"

        # auto mode
        elif mode_select == '2':
            random_packet_len = random.randint(1, int(init_buffer_size))
            message = f"{buffer_size} {random_packet_len}"
            # randomizes the waiting time of the client
            random_number = random.randint(0, 100)
            if 0 < random_number < 33:
                time.sleep(2)
            elif 33 < random_number < 66:
                time.sleep(3)
            else:
                time.sleep(4)

            print(f"\tCLIENT MESSAGE: {message}")

        #SEND TO THE SERVER
        global serverAddress
        clientSocket.sendto(message.encode('UTF-8'), (serverName, serverPort) if not serverAddress else serverAddress)

        print("Waiting for the response from server...")

        #RECEIVE FROM THE SERVER
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        modifiedMessage_array = modifiedMessage.decode("utf-8").split(' ')
        server_rwnd = modifiedMessage_array[0]
        server_pck_len =  modifiedMessage_array[1]
        server_ack = modifiedMessage_array[2]

        update_buffer(server_rwnd) #update buffer according to servers buffer
        print(f"Response from server: RNWD:{server_rwnd} PCK_LEN:{server_pck_len} ACK:{server_ack}")

        # SCORE MECHANISM
        print("-" * 36)
        if server_ack == "ACK" and not losing_point:
            client_plus_points = client_plus_points + 1
            print("\t\t** C O R R E C T **")
        else:
            client_minus_points = client_minus_points + 1
            print("\t\t** W R O N G :( **")

        #OUTPUT
        print(f"SCORE ->\tTotal:{client_plus_points-client_minus_points}\tPlus:{client_plus_points}\tMinus:{client_minus_points}")
        print("-"*36)

def update_buffer(server_buffer):
    global buffer_size
    buffer_size = server_buffer


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
    main()