import socket


def receive_helper(clientSocket):
    valueOfFirstByte = int(clientSocket.recv(1)[0])
    if valueOfFirstByte == 0:
        wordSize, numberOfIncorrectGuesses = clientSocket.recv(2)
        return 0, clientSocket.recv(int(wordSize)), clientSocket.recv(int(numberOfIncorrectGuesses))
    else:
        return 1, clientSocket.recv(valueOfFirstByte)


def letterGuesser(clientSocket):
    while True:
        receivedFlagAndData = receive_helper(clientSocket)
        Flag = receivedFlagAndData[0]
        if Flag != 0:
            message = receivedFlagAndData[1].decode('utf8')
            print("".join(message))
            if message == 'Game Over!' in message:
                break
        else:
            gameString = receivedFlagAndData[1].decode('utf8')
            listOfIncorrectLetters = receivedFlagAndData[2].decode('utf8')
            print(" ".join(list(gameString)))
            print("Incorrect Guesses List: " + "".join(listOfIncorrectLetters) + "\n")

            numberOfIncorrectGuesses = int(clientSocket.recv(1)[0])
            if "_" not in gameString or numberOfIncorrectGuesses >= 7:
                continue
            else:
                letterGuessed = input('Guess a Letter: ').lower()
                message = bytes([len(letterGuessed)]) + bytes(letterGuessed, 'utf8')
                clientSocket.send(message)

    clientSocket.shutdown(socket.SHUT_RDWR)
    clientSocket.close()


if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 1234
    print('Client Host: ' + ip + '| Port: ' + str(port))

    clientSocket = socket.socket()
    clientSocket.connect((ip, port))

    sign = clientSocket.recv(10)[0]

    if sign == 1:
        numberOfPlayers = input("Number of Players? >> ")

        while not numberOfPlayers.isnumeric():
            numberOfPlayers = input("Number of Players? >> ")

        clientSocket.send(numberOfPlayers.encode('utf-8'))

    lengthOfText = int(clientSocket.recv(1)[0])
    text = clientSocket.recv(lengthOfText)
    userName = input(text.decode('utf8'))

    data = bytes([len(userName)]) + bytes(userName, 'utf8')
    clientSocket.send(data)

    registerChecker = clientSocket.recv(10)[0]

    if registerChecker == 1:
        lengthOfText = int(clientSocket.recv(1)[0])
        text = clientSocket.recv(lengthOfText)
        password = input(text.decode('utf8'))

        data = bytes([len(password)]) + bytes(password, 'utf8')
        clientSocket.send(data)

        lengthOfText = int(clientSocket.recv(1)[0])
        text = clientSocket.recv(lengthOfText)
        print(text.decode('utf8'))
    else:
        lengthOfText = int(clientSocket.recv(1)[0])
        text = clientSocket.recv(lengthOfText)
        password = input(text.decode('utf8'))

        data = bytes([len(password)]) + bytes(password, 'utf8')
        clientSocket.send(data)

        passwordChecker = clientSocket.recv(10)[0]

        if passwordChecker == 1:
            print("You successfully logged in.")
        else:
            clientSocket.shutdown(socket.SHUT_RDWR)
            clientSocket.close()


    letterGuesser(clientSocket)
