from socket import *
import time

import random

# ATTRIBUTES
# MODE
mode_select = "2"

# BUFFER
buffer_size = 8  # KB
buffer_available = True
used_buffer = 0

# POINT SYSTEM
client_minus_points = 0
client_plus_points = 0

# CLIENT SOCKET
serverPort = 12000
serverName = gethostname()
clientSocket = socket(AF_INET, SOCK_DGRAM)

modifiedMessage = '8 0'.encode('utf-8')

def main():
    global buffer_available,client_minus_points,client_plus_points,modifiedMessage,used_buffer

    while True:
        #USER INTERACTION STATE
        # manual mode
        if mode_select == '1':
            message = input("Enter receive window number and packet length: ")

        # auto mode
        elif mode_select == '2':
            random_packet_len = random.randint(0, 8)
            message = str(buffer_size - used_buffer) + ' ' + str(random_packet_len)
            # randomizes the waiting time of the client
            random_number = random.randint(0, 100)
            if 0 < random_number < 33:
                time.sleep(2)
            elif 33 < random_number < 66:
                time.sleep(3)
            else:
                time.sleep(4)

        #SEND TO THE SERVER
        clientSocket.sendto(message.encode('UTF-8'), (serverName, serverPort))

        #SCORE MECHANISM
        if no_buffer(modifiedMessage, message):
            client_minus_points = client_minus_points + 1
        else:
            client_plus_points = client_plus_points + 1

        print("A")
        #RECEIVE FROM THE SERVER
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        modifiedMessage_array = modifiedMessage.decode("utf-8").split(' ')
        rcvr_packet_len = modifiedMessage_array[1]
        used_buffer = used_buffer + int(rcvr_packet_len) #used buffer updated
        print("B")
        #TODO bu burada mı olmalı kontrol edilecek
        #increase_buffer_size(modifiedMessage) #update buffer according to servers buffer

        client_message_array = message.split(' ')

        #TODO manual ve auto için farklı print'ler

        print("-"*32)
        print("Window Number:", buffer_size - used_buffer,"Packet length:", int(client_message_array[1]))
        print("Waiting for the response from server")
        print("Response from server:" + modifiedMessage.decode("utf-8"))
        print(f"SCORE ->\tTotal:{client_plus_points-client_minus_points}\tPlus:{client_plus_points}\tMinus:{client_minus_points}")

# checks whether the server's buffer size is sufficient
def no_buffer(rcvr_msg:bytes, client_msg:str):
    is_buffer_not_available = False
    rcvr_msg_array = rcvr_msg.decode("utf-8").split(' ')
    rcvr_buffer_len = rcvr_msg_array[0]

    client_msg_array = client_msg.split(' ')
    client_buffer_len = client_msg_array[1]

    if client_buffer_len > rcvr_buffer_len:
        is_buffer_not_available = True

    return is_buffer_not_available

# increases the buffer size if the specific message is received from the server
def increase_buffer_size(msg_buffer_increased: bytes):
    global buffer_size
    msg_buffer_increased = msg_buffer_increased.decode("utf-8")
    #TODO if message is about buffer size updated
    if msg_buffer_increased == "Buffer size is increased":
        buffer_size = buffer_size + buffer_size * 2


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