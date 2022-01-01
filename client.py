from socket import *
import time

import random

buffer_available = True
serverName = gethostname()
serverPort = 12000
buffer_size = 8
used_buffer = 0
client_minus_points = 0
client_plus_points = 0
counter = 0
modifiedMessage = '8 0'
modifiedMessage = modifiedMessage.encode('utf-8')

clientSocket = socket(AF_INET, SOCK_DGRAM)


def main():
    global buffer_available
    global client_minus_points
    global client_plus_points
    global counter
    global modifiedMessage
    global used_buffer

    mode_select = input("Press 1 for manual mode, press 2 for auto mode:")
    if mode_select == '1':
        print('Manual mode is activated.')
    elif mode_select == '2':
        print('Auto mode is activated.')
    else:

        print('Invalid entry.')
    while True:
        modifiedMessage_array = modifiedMessage.decode("utf-8").split(' ')
        rcvr_rwnd = modifiedMessage_array[0]
        rcvr_packet_len = modifiedMessage_array[1]

        # manual mode
        if mode_select == '1':
            message = input("Enter receive window number and packet length: ")
            clientSocket.sendto(message.encode(), (serverName, serverPort))
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
            clientSocket.sendto(message.encode(), (serverName, serverPort))
        # plus, minus points conditions
        if no_buffer(modifiedMessage, message):
            client_minus_points = client_minus_points + 1
        else:
            client_plus_points = client_plus_points + 1

        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        used_buffer = used_buffer + int(rcvr_packet_len)
        increase_buffer_size(modifiedMessage)

        client_message_array = message.split(' ')
        print("Window Number:", buffer_size - used_buffer,"Packet length:", int(client_message_array[1]))

        print("Waiting for the response from server")
        print("Response from server:" + modifiedMessage.decode())

        print(client_minus_points, client_plus_points)


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
    if msg_buffer_increased == "Buffer size is increased":
        buffer_size = buffer_size + buffer_size * 2


main()

