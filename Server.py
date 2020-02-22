import socket
from _thread import *
import random

totalNumberOfPlayers = 0
word_list = [
    'actor', 'bear', 'cheese', 'door', 'electric',
    'famous', 'garden', 'hospital', 'island', 'juice',
    'knife', 'lock', 'million', 'night', 'office',
    'police', 'queen', 'ring', 'sword', 'table',
    'uncle', 'village', 'world', 'yellow', 'zoo'
]
full = False
sign = 0
user_password = {

}


class GameClass:
    word = ""
    gameString = ""
    numberOfIncorrectGuesses = 0
    listOfIncorrectLetters = 0
    turn = 1
    attempts_left = 7

    def __init__(self, word):
        self.listOfIncorrectLetters = []
        self.word = word
        for i in range(len(word)):
            self.gameString += "_"

    def guessLetter(self, letterGuessed):
        if len(letterGuessed) > 1:
            if letterGuessed == self.word:
                self.gameString = self.word
                return 'Correct Answer!'
            else:
                self.numberOfIncorrectGuesses += 1
                self.attempts_left -= 1
                self.listOfIncorrectLetters.append(letterGuessed)
                return 'Incorrect Answer!'
        else:
            if letterGuessed in self.listOfIncorrectLetters or letterGuessed in self.gameString:
                self.numberOfIncorrectGuesses += 1
                self.attempts_left -= 1
                return 'Incorrect Letter!'
            elif letterGuessed not in self.word:
                self.numberOfIncorrectGuesses += 1
                self.attempts_left -= 1
                self.listOfIncorrectLetters.append(letterGuessed)
                return 'Incorrect Letter!'
            else:
                gameString = list(self.gameString)
                for i in range(len(self.word)):
                    if self.word[i] == letterGuessed:
                        gameString[i] = letterGuessed
                self.gameString = ''.join(gameString)
                return 'Correct Letter!'

    def isOver(self):
        if self.numberOfIncorrectGuesses >= 7:
            return 'You Lose! Game Over!'
        elif not '_' in self.gameString:
            return 'You Win! Game Over!'
        else:
            return ''

    def changeTurn(self):
        global totalNumberOfPlayers
        if self.turn != totalNumberOfPlayers:
            self.turn = self.turn + 1
        else:
            self.turn = 1


def sendMessage(c, message):
    data = bytes([len(message)]) + bytes(message, 'utf8')
    c.send(data)


def sendDataForGuessLetter(c, game):
    Flag = 0
    data = bytes(game.gameString + " ".join(game.listOfIncorrectLetters), 'utf8')
    finalData = bytes([Flag]) + bytes([len(game.gameString)]) + bytes([len(" ".join(game.listOfIncorrectLetters))]) + data + bytes([game.numberOfIncorrectGuesses])
    c.send(finalData)


def multiplayerGame(c, player, game):
    global sign
    global full

    while True:
        currentTurn = game.turn
        while game.turn != player:
            if currentTurn != game.turn:
                sendMessage(c, " ".join(list(game.gameString)))
                sendMessage(c, "Incorrect Guesses List: " + " ".join(game.listOfIncorrectLetters) + "\n")
                sendMessage(c, "You have " + str(game.attempts_left) + " attempts_left" + "\n")
                sendMessage(c, 'Player ' + str(game.turn) + 's turn...')
                currentTurn = game.turn
            continue

        isOverCheck = game.isOver()
        if isOverCheck != '':
            sendDataForGuessLetter(c, game)
            sendMessage(c, isOverCheck)
            sendMessage(c, "Game Over!")
            game.changeTurn()
            break

        sendMessage(c, 'Your Turn!')
        sendMessage(c, "You have " + str(game.attempts_left) + " attempts_left" + "\n")

        sendDataForGuessLetter(c, game)

        receivedLetterLength = int(c.recv(1)[0])
        receivedLetter = c.recv(receivedLetterLength)
        letterGuessed = receivedLetter.decode('utf-8')

        sendMessage(c, game.guessLetter(letterGuessed))

        sendMessage(c, " ".join(list(game.gameString)))
        sendMessage(c, "Incorrect Guesses List: " + " ".join(game.listOfIncorrectLetters) + "\n")

        isOverCheck = game.isOver()
        if isOverCheck != '':
            sendDataForGuessLetter(c, game)
            sendMessage(c, isOverCheck)
            sendMessage(c, "Game Over!")
            game.changeTurn()
            break

        sendMessage(c, "Waiting for other players to play...")
        sendMessage(c, "You have " + str(game.attempts_left) + " attempts_left" + "\n")
        game.changeTurn()
        sendMessage(c, 'Player ' + str(game.turn) + 's turn...')

    sign -= 1
    if sign == 0:
        full = False
    c.close()


def Thread(c, sign):
    global totalNumberOfPlayers
    global full
    global game

    player = sign
    if player == 1:
        word = word_list[random.randint(0, 24)]
        game = GameClass(word)

    sendMessage(c, 'What is your username: ')
    lengthOfText = int(c.recv(1)[0])
    userName = c.recv(lengthOfText).decode('utf8')

    if userName not in user_password:
        registerChecker = 1
        c.send(bytes([registerChecker]))
        sendMessage(c, 'Your username is ' + userName + ', you have not registered up before please write your password to register: ')
        lengthOfText = int(c.recv(1)[0])
        text = c.recv(lengthOfText).decode('utf8')
        user_password[userName] = text
        sendMessage(c, 'Your password saved.')

        sendMessage(c, 'Waiting for other players to connect!')

        if player == totalNumberOfPlayers:
            full = True

        while not full:
            continue

        sendMessage(c, 'All players connected, ready to start!')
        multiplayerGame(c, player, game)
    else:
        registerChecker = 0
        c.send(bytes([registerChecker]))
        sendMessage(c, 'Your username is ' + userName + ', please write your password to login: ')
        lengthOfText = int(c.recv(1)[0])
        text = c.recv(lengthOfText).decode('utf8')
        if user_password[userName] == text:
            passwordChecker = 1
            c.send(bytes([passwordChecker]))

            sendMessage(c, 'Waiting for other players to connect!')

            if player == totalNumberOfPlayers:
                full = True

            while not full:
                continue

            sendMessage(c, 'All players connected, ready to start!')
            multiplayerGame(c, player, game)
        else:
            passwordChecker = 0
            sign -= 1
            if sign == 0:
                full = False
            c.send(bytes([passwordChecker]))
            c.close()


if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 1234

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Server Host: ' + ip + '| Port: ' + str(port))

    try:
        serverSocket.bind((ip, port))
    except socket.error as e:
        print(str(e))
    serverSocket.listen()

    c, address = serverSocket.accept()
    print("Connection " + str(sign + 1) + " established from: " + str(address))
    sign += 1

    c.send(bytes([sign]))
    totalNumberOfPlayers = int(c.recv(10).decode('utf-8'))

    start_new_thread(Thread, (c, sign))

    while True:
        while sign < totalNumberOfPlayers:
            c, address = serverSocket.accept()
            print("Connection " + str(sign + 1) + " established from: " + str(address))
            sign += 1
            c.send(bytes([sign]))
            if sign == 1:
                totalNumberOfPlayers = int(c.recv(10).decode('utf-8'))
            start_new_thread(Thread, (c, sign))
        continue