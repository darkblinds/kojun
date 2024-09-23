from .move import Move
from .randomBoardSelector import RandomBoardSelector
from enum import Enum


class BoardState(Enum):
    boardNotInitialized = 0
    boardValid = 1
    proceedMove = 2
    requestMove = 3
    registerMove = 4
    evaluateWinner = 5
    irregularMove = 6
    boardFull = 98
    boardInvalidToContinue = 99


class Winner(Enum):
    none = 0
    enabledPlayer = 1
    disabledPlayer = 2
    tie = 3


class Board:
    def __init__(self, initialBoardValues=None, initialGroups=None):
        self.matchStatus = BoardState.boardNotInitialized
        if initialBoardValues and initialGroups:
            self.boardValues = initialBoardValues
            self.groups = initialGroups
            self.matchStatus = BoardState.boardValid
            self.messageToCurrentPlayer = ''
            self.messageToNotCurrentPlayer = ''
        else:
            self._startBoard()

    def getValue(self, line, column):
        return self.boardValues[line][column]

    def _startBoard(self):
        self.boardValues, self.groups = RandomBoardSelector.getRandomBoardAndGroup()

    def positionValidToReceiveInput(self, line, column):
        self.matchStatus = BoardState.proceedMove
        if not self.boardValues[line][column]:
            self.matchStatus = BoardState.requestMove
            return True
        else:
            self.matchStatus = BoardState.irregularMove
            self.messageToCurrentPlayer = 'A célula está ocupada'
            self.matchStatus = BoardState.boardValid
            return False

    def valueIsValid(self, value):
        if not isinstance(value, int):
            self.matchStatus = BoardState.irregularMove
            self.messageToCurrentPlayer = 'O valor digitado deve ser um inteiro'
            self.matchStatus = BoardState.boardValid
            return False
        if value <= 0:
            self.matchStatus = BoardState.irregularMove
            self.messageToCurrentPlayer = 'O valor digitado deve ser maior que 0'
            self.matchStatus = BoardState.boardValid
            return False
        return True

    def _getCellsPositionsInGroup(self, group: int):
        return [(i, j) for i in range(len(self.groups)) for j in range(len(self.groups)) if self.groups[i][j] == group]

    def _getEmptyCellsPositions(self):
        return [(i, j) for i in range(len(self.boardValues)) for j in range(len(self.boardValues)) if
                not self.boardValues[i][j]]

    def _checkMoveValid(self, move: Move):
        cellsInGroup = self._getCellsPositionsInGroup(self.groups[move.getLine()][move.getColumn()])

        # Check if there is another equal number in the same group
        for cell in cellsInGroup:
            if move.getLine() == cell[0] and move.getColumn() == cell[1]:
                continue

            if move.getValue() == self.boardValues[cell[0]][cell[1]]:
                return False

        # Check if the number is less than or equal to the group size
        if move.getValue() > len(cellsInGroup):
            return False

        # Check if orthogonally adjacent numbers are different
        orthogonalPositions = [(move.getLine() - 1, move.getColumn()), (move.getLine() + 1, move.getColumn()),
                               (move.getLine(), move.getColumn() - 1), (move.getLine(), move.getColumn() + 1)]
        for position in orthogonalPositions:
            if (position[0] < 0 or position[0] >= len(self.boardValues) or position[1] < 0 or position[1] >= len(
                    self.boardValues)):
                continue
            if self.boardValues[position[0]][position[1]] == move.getValue():
                return False

        # Check if there is a vertically adjacent number in the same group
        if move.getLine() - 1 >= 0:  # Check if there's an upper cell
            if self.boardValues[move.getLine() - 1][move.getColumn()]:  # Check if the cell is filled
                if (self.groups[move.getLine() - 1][move.getColumn()] == self.groups[move.getLine()][
                    move.getColumn()]):  # Check if the cell is in the same group of the move
                    # Check if the upper value is greater than the lower one
                    if self.boardValues[move.getLine() - 1][move.getColumn()] < move.getValue():
                        return False
        if move.getLine() + 1 < len(self.boardValues):  # Check if there's a lower cell
            if self.boardValues[move.getLine() + 1][move.getColumn()]:  # Check if the cell is filled
                if (self.groups[move.getLine() + 1][move.getColumn()] == self.groups[move.getLine()][
                    move.getColumn()]):  # Check if the cell is in the same group of the move
                    # Check if the upper value is greater than the lower one
                    if self.boardValues[move.getLine() + 1][move.getColumn()] > move.getValue():
                        return False

        # Move is valid
        return True

    def _evaluateWinner(self, move: Move):
        self.matchStatus = BoardState.evaluateWinner
        if not self._checkMoveValid(move):
            return Winner.disabledPlayer

        for emptyCell in self._getEmptyCellsPositions():
            for i in range(len(self._getCellsPositionsInGroup(self.groups[emptyCell[0]][emptyCell[1]]))):
                if self._checkMoveValid(Move(emptyCell[0], emptyCell[1], i)):
                    return Winner.none

        return Winner.enabledPlayer

    def _checkBoardFull(self):
        for line in self.boardValues:
            for value in line:
                if not value:
                    return False
        return True

    def registerMove(self, move: Move): # Diagrama de sequencia Receive Move
        self.matchStatus = BoardState.registerMove
        self.boardValues[move.getLine()][move.getColumn()] = move.getValue()
        if winner := self._evaluateWinner(move):
            self.matchStatus = BoardState.boardInvalidToContinue
            if winner == Winner.disabledPlayer:
                self.messageToCurrentPlayer = 'Jogada inválida. Você perdeu!'
                self.messageToNotCurrentPlayer = 'A jogada do outro jogador é inválida. Você venceu!'
            else:
                self.messageToCurrentPlayer = 'A jogada bloqueou qualquer movimento possível. Você venceu!'
                self.messageToNotCurrentPlayer = 'A jogada bloqueou qualquer movimento possível. Você perdeu!'
            return winner

        if self._checkBoardFull():
            self.matchStatus = BoardState.boardFull
            self.messageToCurrentPlayer = 'Tabuleiro cheio. Empate!'
            self.messageToNotCurrentPlayer = 'Tabuleiro cheio. Empate!'
            return Winner.tie

        self.matchStatus = BoardState.boardValid
        return Winner.none
