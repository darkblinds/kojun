from tkinter import *
from time import sleep
from .board import *
from .player import Player
from .move import Move
# Elementos de Pynetgames:
from py_netgames_client.tkinter_client.PyNetgamesServerProxy import PyNetgamesServerProxy
from py_netgames_client.tkinter_client.PyNetgamesServerListener import PyNetgamesServerListener


class Kojun(PyNetgamesServerListener):
    def __init__(self) -> None:
        self.mainWindow = Tk()
        self.mainWindow.title('Kojun Online')
        self.mainWindow.geometry('660x720')
        self.mainWindow.resizable(False, False)
        self.mainWindow['bg'] = 'gray'

        self.mainFrame = Frame(self.mainWindow, padx=32, pady=25, bg='gray')
        self.messageFrame = Frame(self.mainWindow, padx=4, pady=1, bg='gray')
        self.colors = [
            'white', 'yellow', 'pink', 'red', 'aqua', 'aquamarine1', 'bisque4', 'cadetblue',
            'chartreuse1', 'darkorchid', 'gray59', 'green1', 'khaki4', 'skyblue4', 'violetred',
            'coral', 'blue', 'purple', 'orange'
        ]

        self.localPlayer: Player = None
        self.board: Board = None
        self.boardView: list[list[Label]] = []
        self._createBoardFrame()

        self.labelMessage = Label(self.messageFrame, bg='gray', text='Aguardando jogador.',
                                  font=('Helvatical bold', 15))
        self.labelMessage.grid(row=0, column=0, columnspan=3)

        self.mainFrame.grid(row=2, column=0)
        self.messageFrame.grid(row=3, column=0)

        self.add_listener()
        self.send_connect()

        self.mainWindow.mainloop()

    def _createBoardFrame(self) -> None:
        heightOfSquare = 3
        widthOfSquare = 6

        for x in range(8):
            viewTier: list[Label] = []
            for y in range(8):
                squareLabel = Label(self.mainFrame,
                                    height=heightOfSquare, width=widthOfSquare,
                                    bd=3, text='',
                                    relief='solid', bg='white')
                squareLabel.config(font=('Helvatical bold', 15))
                squareLabel.grid(row=x, column=y)
                viewTier.append(squareLabel)

            self.boardView.append(viewTier)

    def _addColorToLabels(self):
        for i in range(len(self.boardView)):
            for j in range(len(self.boardView)):
                self.boardView[i][j].config(bg=self.colors[(self.board.groups[i][j] - 1) % len(self.colors)])

    def _bindClickActionToBoardLabels(self):
        for i in range(len(self.boardView)):
            for j in range(len(self.boardView)):
                self.boardView[i][j].bind('<Button-1>',
                                          lambda event, line=i, column=j: self._proceedMove(event, line, column))

    def _updateBoardLabels(self):
        for i in range(len(self.boardView)):
            for j in range(len(self.boardView)):
                if value := self.board.getValue(i, j):
                    self.boardView[i][j].config(text=str(value), fg='black')
                else:
                    self.boardView[i][j].config(text='', fg='black')

    def _restartMatch(self):
        sleep(5)
        self.localPlayer.enable()
        self.board = Board()
        self._bindClickActionToBoardLabels()
        self._addColorToLabels()
        self._updateBoardLabels()
        self.labelMessage.config(text='Faça sua jogada', fg='black')
        self.send_move(boardGroups=self.board.groups, boardValues=self.board.boardValues)

    def _registerMoveAndUpdateMessage(self, move: Move):
        winner = self.board.registerMove(move)
        if winner == Winner.none:
            return
        if winner == Winner.disabledPlayer:
            self.send_move(messageText=self.board.messageToNotCurrentPlayer, messageColor='green')
            self.labelMessage.config(text=self.board.messageToCurrentPlayer, fg='red')
            self.labelMessage.update()
            self.localPlayer.setLoser()
        if winner == Winner.enabledPlayer:
            self.send_move(messageText=self.board.messageToNotCurrentPlayer, messageColor='red')
            self.labelMessage.config(text=self.board.messageToCurrentPlayer, fg='green')
            self.labelMessage.update()
        if winner == Winner.tie:
            self.send_move(messageText=self.board.messageToNotCurrentPlayer, messageColor='yellow')
            self.labelMessage.config(text=self.board.messageToCurrentPlayer, fg='yellow')
            self.labelMessage.update()

    def _proceedMove(self, event: Event, row: int, column: int) -> None:
        if (self.localPlayer.turn and self.board.positionValidToReceiveInput(row, column)):
            # Obtém o valor a ser inserido através de um popup
            self._popupToGetNewValue()
            if (self.newValue == -999):
                return
            if (not self.board.valueIsValid(self.newValue)):
                self.labelMessage.config(text=self.board.messageToCurrentPlayer, fg='red')
                return

            move = Move(row, column, self.newValue)
            self.send_move(moveRow=row, moveColumn=column, moveValue=self.newValue)
            self._registerMoveAndUpdateMessage(move)
            self._updateBoardLabels()
            self.localPlayer.disable()
            if (self.localPlayer.loser):
                self.localPlayer.reset()
                self._restartMatch()
            else:
                self.labelMessage.config(text='Aguardado jogada do oponente', fg='black')

    def _popupToGetNewValue(self) -> None:
        self.newValue: int = -999

        def destroy_top(top: Toplevel):
            top.destroy()

        def set_new_value_and_destroy_top(top: Toplevel, entry: Entry):
            newValue = entry.get()
            if str.isdigit(newValue):
                self.newValue = int(newValue)
            destroy_top(top)

        top = Toplevel(self.mainWindow)

        Label(top, text='Digite o valor que deseja colocar na casa').pack()
        entry = Entry(top)
        entry.pack()
        Button(top, text='Cancelar', command=lambda: destroy_top(top)).pack()
        Button(top, text='Confirmar',
               command=lambda: set_new_value_and_destroy_top(top, entry)).pack()
        top.wait_window()

    ########################################################PYNETGAMES#######################################################################################################

    def add_listener(self):  # Pyng use case "add listener"
        self.server_proxy = PyNetgamesServerProxy()
        self.server_proxy.add_listener(self)

    def send_connect(self):  # Pyng use case "send connect"
        self.server_proxy.send_connect("wss://py-netgames-server.fly.dev")

    def send_match(self):  # Pyng use case "send match"
        self.server_proxy.send_match(2)

    def receive_connection_success(self):  # Pyng use case "receive connection"
        self.send_match()

    def receive_disconnect(self):  # Pyng use case "receive disconnect"
        pass

    def receive_error(self):  # Pyng use case "receive error"
        pass

    def receive_match(self, match):  # Pyng use case "receive match"
        self.matchId = match.match_id

        self.localPlayer = Player(name='Jogador ' + str(match.position))
        if (match.position == 1):
            self.localPlayer.enable()
            self.board = Board()
            self._bindClickActionToBoardLabels()
            self._addColorToLabels()
            self._updateBoardLabels()
            self.labelMessage.config(text='Faça sua jogada', fg='black')
            self.send_move(boardGroups=self.board.groups, boardValues=self.board.boardValues)

    def receive_move(self, message):  # Pyng use case "receive move"
        payload = message.payload

        if (payload['boardValues'] and payload['boardGroups']):
            self.localPlayer.reset()
            self.board = Board(payload['boardValues'], payload['boardGroups'])
            self._bindClickActionToBoardLabels()
            self._addColorToLabels()
            self._updateBoardLabels()
            self.labelMessage.config(text='Aguardado jogada do oponente', fg='black')
            return

        if (payload['messageText'] and payload['messageColor']):
            self.labelMessage.config(text=payload['messageText'], fg=payload['messageColor'])
            return

        self.board.registerMove(Move(payload['moveRow'], payload['moveColumn'], payload['moveValue']))
        self.boardView[payload['moveRow']][payload['moveColumn']].config(text=str(payload['moveValue']), fg='black')
        self.labelMessage.config(text='Faça sua jogada', fg='black')
        self.localPlayer.enable()

    def send_move(self, moveRow=None, moveColumn=None, moveValue=None, messageText=None, messageColor=None,
                  boardValues=None, boardGroups=None):  # Pyng use case "send move"
        self.server_proxy.send_move(self.matchId, {'moveRow': moveRow, 'moveColumn': moveColumn, 'moveValue': moveValue,
                                                   'boardValues': boardValues,
                                                   'boardGroups': boardGroups, 'messageText': messageText,
                                                   'messageColor': messageColor})


if __name__ == "__main__":
    Kojun()
