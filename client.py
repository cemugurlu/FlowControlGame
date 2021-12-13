from socket import *

buffer_available = True
serverName = gethostname()
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)


def main():
    global buffer_available
    while True:

        if buffer_available:
            # enough buffer

            message = input("Enter receive window number and packet length: ")
            clientSocket.sendto(message.encode(), (serverName, serverPort))

            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)

            print("\nMessage Sent to server" + str(serverAddress))
            print("Waiting for the response from server")
            print("Response from server:" + modifiedMessage.decode())

        if int(check_buffer(modifiedMessage.decode())) <= 0:
            buffer_available = False
        else:
            buffer_available = True


def check_buffer(msg):
    msg_array = msg.split(' ')
    buffer_len = msg_array[1]

    return buffer_len


main()
