from socket import *
import time

# ATTRIBUTES
isAutomatic = True
buffer_time_limit = 30
local_store = []
server_buffer = 8  # KB
serverPort = 12000
clientAddress = gethostname()

# SERVER SOCKET
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
print('The server is ready to receive')


def checkTimer():
    for message in local_store:
        length = message[0]
        start_time = message[1]
        end = time.time()

        if (end - start_time) > buffer_time_limit:
            updateAvailableBuffer(length)


def updateAvailableBuffer(size):
    global server_buffer, clientAddress
    server_buffer += size
    acknowledgedMessageOne = f'ACK {server_buffer}'
    serverSocket.sendto(acknowledgedMessageOne.encode('UTF-8'), (clientAddress, serverPort))


def decreaseAvailableBuffer(size):
    global server_buffer
    server_buffer -= size


def main():
    while 1:
        message, clientAddress = serverSocket.recvfrom(2048)

        message_array = (message.decode("utf-8")).split(' ')
        client_rwnd = message_array[0]
        message_length = message_array[1]
        decreaseAvailableBuffer(int(message_length))
        local_store.append([int(message_length), time.time()])

        # TODO: Bu kısım while döngüsünde sürekli ziyaret ediliyor mu? Kontrol edilmeli
        checkTimer()

        if isAutomatic:
            print("auto mod")
            acknowledgedMessage = f'{server_buffer} {message_length}'
            # TODO: Send ACK, Cond, if manual wait for user input from terminal
            # TODO: Input: Remaining buffer length, ACK or NAK *
        else:
            print("manual mod")
            acknowledgedMessage = f'ACK {server_buffer}'
            # TODO: Get  ACK message from user input
            # TODO: send ACK message
            # TODO: Input: Remaining buffer length, ACK or NAK *

        serverSocket.sendto(acknowledgedMessage.encode('UTF-8'), clientAddress)


if __name__ == '__main__':
    main()
    # TODO: mod selection question. Auto or manual

    local_store = [[2, time.time()], [4, time.time()]]
    buffer_time_limit = 1
    for i in range(100000000):
        continue
    checkTimer()
